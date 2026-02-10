# test-automation-boilerplate

Boilerplate, default configs, and examples for test automation using the logic analyzer and picoscope.

## Installs

Follow the respective installation instructions for the environment you need, be it for PicoScope or Logic Analyzer. These instructions are linked below:

- [PicoScope Environment Setup]("/docs/Pico_Setup.md")
- Logic Analyzer WIP

Both tools will require Python 3, and can run on Windows, Mac, or Linux

## Usage

### PicoScope

After setup, you can test your connection to the Picoscope with [pico_example.py]("src/picoscope/pico_example.py), and run the Pico using [pico_boilerplate.py]("src/picoscope/pico_boilerplate.py").

You can make edits to the PicoStreamer class, e.g. Analog sampling, advanced triggers, with use of the PicoSDK in the [pico_base.py]("src/picoscope/pico_base.py").
