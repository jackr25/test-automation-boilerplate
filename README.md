# test-automation-boilerplate

Boilerplate, default configs, and examples for test automation using the logic analyzer and picoscope.

## Installation and Setup

Follow the respective installation instructions for the environment you need, be it for PicoScope or Logic Analyzer. These instructions are linked below:

- [PicoScope Environment Setup](docs/Pico_Setup.md)
- [Saleae Logic Analyzer Environment Setup and Logic2 Downloads](docs/Saleae_Setup.md)

Both tools will require Python 3, and can run on Windows, Mac, or Linux

*Note for Windows Users:*
    You will need to utilize git bash (as opposed to CMD or powershell) in order to run these scripts. You should already have this from when you installed git. It essentially just mimic a unix environment, and makes environment management easier for python virtual environments.

    Git bash is generally speaking more user-friendly than powershell, and if you're not super bought into the powershell environment, we'd encourage you to become familiar with bash for interoperability between different OS's.

## Usage

### PicoScope

After setup, you can test your connection to the Picoscope with [pico_example.py](src/picoscope/pico_example.py), and run the Pico using [pico_boilerplate.py](src/picoscope/pico_boilerplate.py).

You can make edits to the PicoStreamer class, e.g. Analog sampling, advanced triggers, with use of the PicoSDK in the [pico_base.py](src/picoscope/pico_base.py).
