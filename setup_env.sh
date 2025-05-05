#!/bin/bash
echo "[INFO] Setting up BitNet.cpp environment..."

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv .venv
else
    echo "[INFO] Virtual environment already exists."
fi

# Activate virtual environment
echo "[INFO] Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "[INFO] Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements_desktop.txt

echo "[SUCCESS] Environment setup complete!"
echo
echo "[INFO] The BitNet.cpp environment is now ACTIVE."
echo "[INFO] You can verify this by seeing (.venv) at the beginning of your command prompt."
echo "[INFO] To check environment status anytime, run './check_env.sh'."
