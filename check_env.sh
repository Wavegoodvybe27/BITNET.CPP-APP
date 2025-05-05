#!/bin/bash

if [ -d ".venv" ]; then
    echo "[INFO] BitNet.cpp environment exists."
    
    # Check if the environment is activated
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "[SUCCESS] BitNet.cpp environment is ACTIVE."
        echo "Current environment: $VIRTUAL_ENV"
    else
        echo "[WARNING] BitNet.cpp environment exists but is NOT ACTIVE."
        echo "Run 'source .venv/bin/activate' to activate it."
    fi
else
    echo "[ERROR] BitNet.cpp environment does not exist."
    echo "Run './setup_env.sh' to create it."
fi
