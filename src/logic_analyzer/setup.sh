#!/bin/bash


# Detect where this script is located so we can run from root OR inside the folder
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"  # We assume setup is in the project folder
VENV_PATH="$PROJECT_ROOT/venv"
REQ_FILE="$PROJECT_ROOT/requirements.txt"


# Check if script is being SOURCED or EXECUTED
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
    INTERACTIVE_MODE=true
else
    INTERACTIVE_MODE=false
    echo "⚠️  NOTE: You are executing this script, so the environment will NOT stay active."
    echo "   To keep it active, run: source src/picoscope/setup.sh"
    echo "   (Continuing with installation...)"
    echo ""
fi

# DETECT OS & PYTHON
OS="$(uname -s)"
case "${OS}" in
    CYGWIN*|MINGW*|MSYS*) MACHINE=Windows;;
    Darwin*)    MACHINE=Mac;;
    Linux*)     MACHINE=Linux;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "Detected System: $MACHINE"

# Find Python
if command -v python3 &>/dev/null; then
    PY_CMD=python3
elif command -v python &>/dev/null; then
    PY_CMD=python
elif command -v py &>/dev/null; then
    PY_CMD=py
else
    echo "❌ CRITICAL ERROR: Python not found!"
    return 1 2>/dev/null || exit 1
fi

echo "Using Python: $($PY_CMD --version)"


# Create Requirements if missing
if [ ! -f "$REQ_FILE" ]; then
    echo "Creating default requirements.txt..."
    printf "picosdk\nnumpy\npandas\nmatplotlib\n" > "$REQ_FILE"
fi

# Create VENV if missing
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating Virtual Environment..."
    $PY_CMD -m venv "$VENV_PATH"
fi

# Locate the VENV Python & Activate script (OS Dependent)
if [ "$MACHINE" == "Windows" ]; then
    VENV_PYTHON="$VENV_PATH/Scripts/python.exe"
    ACTIVATE_SCRIPT="$VENV_PATH/Scripts/activate"
else
    VENV_PYTHON="$VENV_PATH/bin/python3"
    ACTIVATE_SCRIPT="$VENV_PATH/bin/activate"
fi

# Install Dependencies (Directly into VENV to avoid activation issues during install)
echo "Installing dependencies..."
"$VENV_PYTHON" -m pip install -r "$REQ_FILE"

# --- 5. ACTIVATION (The Magic Part) ---

if [ "$INTERACTIVE_MODE" = true ]; then
    # If the user sourced the script, we activate the environment for them
    if [ -f "$ACTIVATE_SCRIPT" ]; then
        source "$ACTIVATE_SCRIPT"
        echo ""
        echo "[Success]: Setup Complete & Environment Activated!"
    else
        echo "[Error]: Could not find activate script at $ACTIVATE_SCRIPT"
    fi
else
    # If they just ran it, we give them instructions
    echo ""
    echo "[Success]: Setup Complete."
    echo "   To start working, run this command:"
    echo "   source $ACTIVATE_SCRIPT"
fi