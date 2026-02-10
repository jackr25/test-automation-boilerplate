from pico_base import PicoStreamer

"""
Boilerplate for new Picoscope users to easily set up channels to sample DC voltage,
    save streamed voltage data,
    and output plots of the traces.
"""


SAVE_FILENAME = "supercap_test_01"
SAMPLE_INTERVAL_NS = 1_000_000  # 1ms resolution (1,000,000 ns)

def main():
    with PicoStreamer() as scope: # MAKE SURE YOU CLOSE THE PICOSCOPE APP
        
        # Setup Channels
        # Options: '10V', '5V', '2V', '1V'
        scope.setup_channel('A', voltage_range='10V')
        scope.setup_channel('B', voltage_range='10V') # You can simply comment this one out if you only need one channel
        
        # Start Capture
        # This will block until you type "done" or hit Ctrl+C
        scope.run_capture(sample_interval_ns=SAMPLE_INTERVAL_NS)
        
        # Save Data
        # Saves to a 'results' folder automatically
        scope.save_to_csv(SAVE_FILENAME)
        
        # Saves and Shows plot (show won't work on headless environments such as WSL)
        scope.plot_data(title="Supercapacitor Charging Curve", filename="results.png", directory="results")

if __name__ == "__main__":
    main()