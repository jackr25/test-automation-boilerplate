import os
import time
from saleae import automation

class SaleaeWrapper:
    """
    A simplified wrapper for the Saleae Logic 2 Automation API.
    Designed for a quick-start to capturing data.
    """
    
    def __init__(self, port=10430): # uh I think this is constant
        self.port = port
        self.manager = None
        self.device_id = None
        self.device_config = None
        
        # State tracking
        self.enabled_digital = []
        self.enabled_analog = []
        
    def __enter__(self):
        """Allows usage in 'with' statements."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup on exit."""
        self.close()

    def connect(self):
        """Connects to the running Logic 2 software."""
        print("Connecting to Saleae Logic 2 Software...")
        try:
            self.manager = automation.Manager.connect(port=self.port)
            print("Connected to Logic 2.")
        except Exception as e:
            print(f"Failed to connect: {e}")
            print("Ensure the Logic 2 app is OPEN and the Automation Server is ENABLED in settings.")
            raise

        # Auto-detect the first connected device
        devices = self.manager.get_devices()
        if not devices:
            raise RuntimeError("No Saleae devices detected!")
        
        self.device_id = devices[0].device_id
        print(f"Using Device: {devices[0].name} (ID: {self.device_id})")

    def setup_channels(self, channel_map, digital_sample_rate=500_000_000, 
                    analog_sample_rate=50_000, digital_voltage_level=1.8):
        """
        Configures the device based on a simple dictionary.
        
        :param channel_map: Dict { channel_index: 'type' }
                            e.g. { 0: 'digital', 1: 'analog', 2: 'both' }
        """
        self.enabled_digital = []
        self.enabled_analog = []

        # Parse the human-readable dict
        for ch_idx, mode in channel_map.items():
            mode = mode.lower()
            if 'dig' in mode or 'both' in mode:
                self.enabled_digital.append(ch_idx)
            if 'ana' in mode or 'both' in mode:
                self.enabled_analog.append(ch_idx)

        # Create the device configuration object from input dict
        try:
            self.device_config = automation.LogicDeviceConfiguration(
                enabled_digital_channels=self.enabled_digital,
                enabled_analog_channels=self.enabled_analog,
                digital_sample_rate=digital_sample_rate,
                analog_sample_rate=analog_sample_rate,
                digital_threshold_volts=digital_voltage_level
            )
            print(f"Configuration Set: {len(self.enabled_digital)} Digital, {len(self.enabled_analog)} Analog channels.")
        except Exception as e:
            print("Error in configuration. Check your sample rates!")
            raise e

    def capture_timed(self, duration_seconds, output_dir, file_basename="capture", save_sal = False):
        """
        Runs a capture for a set duration and exports to CSV.
        """
        if not self.device_config:
            raise RuntimeError("Run setup_channels() before capturing.")

        # Ensure output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        capture_config = automation.CaptureConfiguration(
            capture_mode=automation.TimedCaptureMode(duration_seconds=duration_seconds)
        )

        print(f"Starting {duration_seconds}s capture...")
        
        # Start the capture
        if self.device_id is not None:
            try: 
                with self.manager.start_capture( # pyright: ignore[reportOptionalMemberAccess]
                    device_id=self.device_id,
                    device_configuration=self.device_config,
                    capture_configuration=capture_config
                ) as capture:
                    
                    # Block until capture is done
                    capture.wait()
                    print("Capture complete. processing...")
                    
                    # Export to CSV
                    export_path = os.path.join(output_dir, file_basename)
                    
                    # Note: Saleae exports separate files for analog/digital in the folder
                    capture.export_raw_data_csv(
                        directory=export_path,
                        digital_channels=self.enabled_digital,
                        analog_channels=self.enabled_analog
                    )
                    if save_sal is True:
                        capture.export_to_sal
                    print(f"Data saved to: {export_path}")
                    return export_path
            except ValueError:
                pass


    def close(self):
        """Closes the connection to the manager."""
        if self.manager:
            self.manager.close()
            print("Saleae connection closed.")