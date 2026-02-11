import time
from saleae_base import SaleaeWrapper

# configuration

RESULTS_DIR = "lab_results" # where to store traces
CSV_NAME = "run_1"

DIGITAL_VOLTAGE = 1.8  # 1.2, 1.8, or 3.3 usually

# 1.8 is pretty standard threshold for pins that give "logic", but use your best judgement
#   based on what you're measuring

# Define your channels here!
# 'digital', 'analog', or 'both'
CHANNEL_SETUP = {
    0: 'digital',   # e.g., GPIO Toggle
    1: 'analog',    # e.g., Current Shunt
    2: 'analog',    # e.g., Voltage Rail
    3: 'digital'    # e.g., UART TX
    # 4: 'analog',
    # 5: 'digital',
    # 6: 'analog',
    # 7: 'digital',
}

DURATION_SEC = 5.0 # how long, in seconds, to capture data 
DIGITAL_SAMPLE_RATE = 500_000_000 # 500 MS/s
ANALOG_SAMPLE_RATE = 50_000 # 50 kS/s

def main():
    # Initialize the wrapper which Connects to Logic 2 App, WHICH MUST BE OPEN 
    with SaleaeWrapper() as logic:
        
        # Setup the Hardware
        logic.setup_channels(
            channel_map=CHANNEL_SETUP,
            digital_sample_rate=DIGITAL_SAMPLE_RATE,
            analog_sample_rate=50_000,       
            digital_voltage_level=DIGITAL_VOLTAGE
        )
        
        # Trigger your external device here, like maybe you're throwing a command over UART to your CDH board?
        #print(">>> Triggering external device (Simulated)...")
        # subprocess.run(["python", "some_other_script.py"]) 
        time.sleep(0.5) 

        # Run Capture
        # This will automatically save CSVs
        logic.capture_timed(
            duration_seconds=DURATION_SEC, 
            output_dir=RESULTS_DIR,
            file_basename=CSV_NAME
        )
        
        print("Test Complete.")

if __name__ == "__main__":
    main()