#!/bin/bash
echo "[INFO] Activating BitNet.cpp environment..."
source .venv/bin/activate
echo "[SUCCESS] BitNet.cpp environment is now ACTIVE"
echo
python bitnet.py "$@"
