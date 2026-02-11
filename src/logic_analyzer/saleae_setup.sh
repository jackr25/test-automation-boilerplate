#!/bin/bash

VENV_DIR="venv"
REQUIREMENTS_FILE="requirements.txt"

# Default to using a virtual environment
USE_VENV=true

# Parse arguments
if [[ "$1" == "--no-venv" ]]; then
    USE_VENV=false
    echo "Flag --no-venv detected: Will install dependencies to global Python."
fi

# detect OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Windows;;
    MINGW*)     MACHINE=Windows;;
    MSYS*)      MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "------------------------------------------------"
echo "Detected Operating System: $MACHINE"
echo "------------------------------------------------"

# prefer python3, but fall back to python
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "CRITICAL ERROR: Python is not installed or not in PATH."
    exit 1
fi
echo "Using Python command: $PYTHON_CMD"

# if on linux, just install the picoscope app
if [ "$MACHINE" == "Linux" ]; then
    # Check if picoscope is already installed
    if dpkg -l | grep -q "picoscope"; then
        echo "PicoScope software is already installed. Skipping..."
    else
        echo "PicoScope software not found. Installing via apt..."
        
        # Add the GPG key
        sudo bash -c 'wget -O- https://labs.picotech.com/Release.gpg.key | gpg --dearmor > /usr/share/keyrings/picotech-archive-keyring.gpg'

        # Add the repository
        sudo bash -c 'echo "deb [signed-by=/usr/share/keyrings/picotech-archive-keyring.gpg] https://labs.picotech.com/picoscope7/debian/ picoscope main" >/etc/apt/sources.list.d/picoscope7.list'

        # Update and Install
        sudo apt-get update
        sudo apt-get install -y picoscope
        
        echo "PicoScope installation complete."
    fi
fi

# venv setup

if [ "$USE_VENV" = false ]; then
    # Global Install
    echo "Installing Python dependencies globally..."
    $PYTHON_CMD -m pip install -r "$REQUIREMENTS_FILE"

else
    # Virtual Environment Install
    
    # Check if the 'venv' module is actually installed 
    $PYTHON_CMD -c "import venv" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Error: The 'venv' module is missing."
        if [ "$MACHINE" == "Linux" ]; then
            echo "Attempting to install python3-venv..."
            sudo apt-get install -y python3-venv
            
            # Re-check
            $PYTHON_CMD -c "import venv" 2>/dev/null
            if [ $? -ne 0 ]; then
                echo "Failed to install venv. Please run 'sudo apt install python3-venv' manually."
                exit 1
            fi
        else
            echo "Please install the python venv module for your system."
            exit 1
        fi
    fi

    # Create venv if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment in ./$VENV_DIR..."
        $PYTHON_CMD -m venv "$VENV_DIR"
    fi

    # Activate venv
    # Windows (Git Bash/Mingw) uses Scripts/activate, Unix uses bin/activate
    if [ "$MACHINE" == "Windows" ]; then
        ACTIVATE_PATH="$VENV_DIR/Scripts/activate"
    else
        ACTIVATE_PATH="$VENV_DIR/bin/activate"
    fi

    if [ -f "$ACTIVATE_PATH" ]; then
        echo "Activating virtual environment..."
        source "$ACTIVATE_PATH"
    else
        echo "Error: Could not find activation script at $ACTIVATE_PATH"
        exit 1
    fi

    # Install Dependencies
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install -r "$REQUIREMENTS_FILE"

    echo "------------------------------------------------"
    echo "Setup Complete!"
    echo "To start working, activate the environment:"
    echo "  source $ACTIVATE_PATH"
    echo "------------------------------------------------"
fi