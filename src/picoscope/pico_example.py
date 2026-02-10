from pico_base import PicoStreamer

"""
Simply validates the ability to connect to the PicoScope 2206 using the PicoStreamer class.
"""

def main():
    with PicoStreamer() as scope:
        scope.setup_channel('A', voltage_range='10V')

if __name__ == "__main__":
    main()