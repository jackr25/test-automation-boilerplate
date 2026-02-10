try:
    import ctypes, threading, time, os
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from picosdk.ps2000a import ps2000a as ps
    from picosdk.functions import assert_pico_ok, adc2mV
except ImportError:
    raise SystemExit("Error importing modules - Did you run pico_setup.sh?")

class PicoStreamer:
    """
    A simplified wrapper for the PicoScope 2000a Series (e.g., the 2206B in the lab) 
    Handles streaming, buffer management, and file saving.
    """

    def __init__(self, max_samples=20_000_000):
        self.chandle = ctypes.c_int16()
        self.status = {}
        self.max_samples = max_samples
        self.is_open = False
        
        # track which channels the user actually wants
        self.enabled_channels = {'A': False, 'B': False}
        self.channel_ranges = {'A': 0, 'B': 0}
        
        # data storage
        self.buffers_raw = {'A': None, 'B': None}
        self.data_mv = {'A': None, 'B': None, 'Time': None}
        self.sample_count = 0
        self.max_adc = ctypes.c_int16()
        
        # flags
        self.stop_event = threading.Event()
        self.auto_stop = False

    def __enter__(self):
        """Allows use of 'with' statement to ensure scope closes safely."""
        self.open_unit()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Automatically closes scope on exit or error."""
        self.close_unit()

    def open_unit(self):
        """Connects to the PicoScope."""
        print("Initializing PicoScope...")
        self.status["openunit"] = ps.ps2000aOpenUnit(ctypes.byref(self.chandle), None)
        try:
            assert_pico_ok(self.status["openunit"])
            self.is_open = True
            
            # get Max ADC value for conversion later
            ps.ps2000aMaximumValue(self.chandle, ctypes.byref(self.max_adc))
            print("Scope connected successfully.")
        except Exception as e:
            print(f"Error opening scope: {e}")
            raise

    def setup_channel(self, channel='A', voltage_range='10V'):
        """
        Configures a channel.
        :param channel: 'A' or 'B'
        :param voltage_range: String like '5V', '10V', '1V'.
        """
        channel = channel.upper()
        if channel not in ['A', 'B']:
            raise ValueError("Channel must be 'A' or 'B'")

        ch_map = {
            'A': ps.PS2000A_CHANNEL['PS2000A_CHANNEL_A'],
            'B': ps.PS2000A_CHANNEL['PS2000A_CHANNEL_B']
        }
        
        # map simple strings to Pico Enums
        range_map = {
            '10V': ps.PS2000A_RANGE['PS2000A_10V'],
            '5V':  ps.PS2000A_RANGE['PS2000A_5V'],
            '2V':  ps.PS2000A_RANGE['PS2000A_2V'],
            '1V':  ps.PS2000A_RANGE['PS2000A_1V'],
        }
        
        selected_range = range_map.get(voltage_range, ps.PS2000A_RANGE['PS2000A_10V'])
        self.channel_ranges[channel] = selected_range
        
        # configure and enable
        status = ps.ps2000aSetChannel(
            self.chandle, ch_map[channel], 1, 
            ps.PS2000A_COUPLING['PS2000A_DC'], 
            selected_range, 0.0
        )
        assert_pico_ok(status)
        self.enabled_channels[channel] = True
        print(f"Channel {channel} configured for {voltage_range}.")

    def _streaming_callback(self, handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
        """Internal C-type callback for data collection."""
        destEnd = self.sample_count + noOfSamples
        sourceEnd = startIndex + noOfSamples
        
        if destEnd >= self.max_samples:
            self.auto_stop = True
            destEnd = self.max_samples
        
        # only streams enabled channels
        if self.enabled_channels['A'] and self.buffers_raw['A'] is not None:
            try:
                self.buffers_raw['A'][self.sample_count:destEnd] = self.temp_buffer_a[startIndex:sourceEnd]
            except ValueError:
                print("Unexpected inputs to streaming callback")
        if self.enabled_channels['B'] and self.buffers_raw['B'] is not None:
            try:
                self.buffers_raw['B'][self.sample_count:destEnd] = self.temp_buffer_b[startIndex:sourceEnd]
            except ValueError:
                print("Unexpected inputs to streaming callback")
        self.sample_count += noOfSamples
        if autoStop:
            self.auto_stop = True

    def _wait_for_input(self):
        """Background thread to listen for user stopping the test."""
        print(">>> Type 'done' and press ENTER to stop capture early <<<")
        while not self.stop_event.is_set():
            try:
                i = input()
                if i.strip().lower() == 'done':
                    self.stop_event.set()
            except EOFError:
                break

    def run_capture(self, sample_interval_ns=1_000_000):
        """
        Starts the streaming capture. 
        """
        if not (self.enabled_channels['A'] or self.enabled_channels['B']):
            print("Error: No channels setup! Call setup_channel() first.")
            return

        # disable unused channels to prevent driver errors
        ch_map = {'A': ps.PS2000A_CHANNEL['PS2000A_CHANNEL_A'], 'B': ps.PS2000A_CHANNEL['PS2000A_CHANNEL_B']}
        for ch, enabled in self.enabled_channels.items():
            if not enabled:
                ps.ps2000aSetChannel(self.chandle, ch_map[ch], 0, 0, 0, 0) # 3rd arg 0 means it is disabled

        # allocate memory for enable channels only
        buffer_size = 1000
        
        if self.enabled_channels['A']:
            self.buffers_raw['A'] = np.zeros(shape=self.max_samples, dtype=np.int16)
            self.temp_buffer_a = np.zeros(shape=buffer_size, dtype=np.int16)
            ps.ps2000aSetDataBuffers(self.chandle, ch_map['A'],
                                    self.temp_buffer_a.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                    None, buffer_size, 0, ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'])

        if self.enabled_channels['B']:
            self.buffers_raw['B'] = np.zeros(shape=self.max_samples, dtype=np.int16)
            self.temp_buffer_b = np.zeros(shape=buffer_size, dtype=np.int16)
            ps.ps2000aSetDataBuffers(self.chandle, ch_map['B'],
                                    self.temp_buffer_b.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                    None, buffer_size, 0, ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'])

        # start streaming
        cFuncPtr = ps.StreamingReadyType(self._streaming_callback)
        sample_interval = ctypes.c_int32(int(sample_interval_ns / 1000))
        
        ps.ps2000aRunStreaming(self.chandle, ctypes.byref(sample_interval), 
                            ps.PS2000A_TIME_UNITS['PS2000A_US'], 0, self.max_samples, 
                            1, 1, ps.PS2000A_RATIO_MODE['PS2000A_RATIO_MODE_NONE'], buffer_size)

        print("Streaming started.")
        
        input_thread = threading.Thread(target=self._wait_for_input)
        input_thread.daemon = True
        input_thread.start()

        try:
            while self.sample_count < self.max_samples and not self.auto_stop:
                if self.stop_event.is_set():
                    break
                
                ps.ps2000aGetStreamingLatestValues(self.chandle, cFuncPtr, None)
                
                # status messages
                if self.sample_count > 0 and self.sample_count % 5000 == 0:
                    status_msg = f"\rSamples: {self.sample_count}"
                    if self.enabled_channels['A'] and self.buffers_raw['A'] is not None:
                        val_a = adc2mV(self.buffers_raw['A'][self.sample_count-1], self.channel_ranges['A'], self.max_adc)
                        status_msg += f" | ChA: {val_a:.1f} mV"
                    if self.enabled_channels['B'] and self.buffers_raw['B'] is not None:
                        val_b = adc2mV(self.buffers_raw['B'][self.sample_count-1], self.channel_ranges['B'], self.max_adc)
                        status_msg += f" | ChB: {val_b:.1f} mV"
                    print(status_msg, end="")
                
                time.sleep(0.01)

        except KeyboardInterrupt:
            print("\n!!! INTERRUPT DETECTED !!! performing emergency save...")
            self.stop_event.set()
            
        print("\nStopping capture...")
        ps.ps2000aStop(self.chandle)
        self._process_data(sample_interval_ns)

    def _process_data(self, sample_interval_ns):
        """Converts raw ADC data to mV and time arrays for enabled channels."""
        end_idx = self.sample_count
        
        if self.enabled_channels['A'] and self.buffers_raw['A'] is not None:
            self.data_mv['A'] = adc2mV(self.buffers_raw['A'][:end_idx], self.channel_ranges['A'], self.max_adc)
            
        if self.enabled_channels['B'] and self.buffers_raw['B'] is not None:
            self.data_mv['B'] = adc2mV(self.buffers_raw['B'][:end_idx], self.channel_ranges['B'], self.max_adc)
        
        total_time = (end_idx * sample_interval_ns) / 1e9
        self.data_mv['Time'] = np.linspace(0, total_time, end_idx)

    def save_to_csv(self, filename="data.csv", directory="results"):
        """Saves enabled channels to CSV."""
        if self.data_mv['Time'] is None:
            print("No data to save.")
            return

        if not os.path.exists(directory):
            os.makedirs(directory)
            
        filepath = os.path.join(directory, filename)
        if not filepath.endswith(".csv"):
            filepath += ".csv"
            
        # build Pandas DataFrame dynamically
        data_dict = {'Time_Sec': self.data_mv['Time']}
        if self.enabled_channels['A'] and self.data_mv['A'] is not None:
            data_dict['ChA_mV'] = self.data_mv['A']
        if self.enabled_channels['B'] and self.data_mv['B'] is not None:
            data_dict['ChB_mV'] = self.data_mv['B']
            
        df = pd.DataFrame(data_dict)
        df.to_csv(filepath, index=False)
        print(f"Data saved to: {filepath}")

    def plot_data(self, filename="data.png", directory="results", title="PicoScope Capture"):
        """Plots enabled channels."""
        if self.data_mv['Time'] is None:
            print("No data to plot.")
            return
        
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        filepath = os.path.join(directory, filename)
        if not filepath.endswith(".png"):
            filepath += ".png"
            
        plt.figure(figsize=(10, 6))
        
        if self.enabled_channels['A']:
            plt.plot(self.data_mv['Time'], self.data_mv['A'], label="Ch A", color='blue')
            
        if self.enabled_channels['B']:
            plt.plot(self.data_mv['Time'], self.data_mv['B'], label="Ch B", color='orange', alpha=0.7)
            
        plt.xlabel("Time (s)")
        plt.ylabel("Voltage (mV)")
        plt.title(title)
        plt.legend()
        plt.grid(True)
        plt.savefig(filepath)
        try:
            plt.show()
        except Exception as e:
            # you're on WSL or something
            print(f"\n[Headless Mode Detected]: Could not open window ({e})")
            

    def close_unit(self):
        """Clean up connection."""
        if self.is_open:
            ps.ps2000aStop(self.chandle)
            ps.ps2000aCloseUnit(self.chandle)
            self.is_open = False
            print("PicoScope connection closed.")