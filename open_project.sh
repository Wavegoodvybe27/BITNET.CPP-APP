#!/bin/bash
# Shell script to open VSCode with BitNet environment activated
echo "[INFO] Opening BitNet.cpp project with environment activated..."

# Get the current directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if VSCode is installed
if ! command -v code &> /dev/null; then
    echo "[ERROR] VSCode is not found in PATH. Please install VSCode or add it to your PATH."
    exit 1
fi

# Check if the environment exists
if [ ! -d "$PROJECT_DIR/.venv" ]; then
    echo "[WARNING] BitNet.cpp environment not found. Setting it up now..."
    bash "$PROJECT_DIR/setup_env.sh"
fi

# Open VSCode with the workspace
echo "[INFO] Opening VSCode with BitNet.cpp workspace..."
code "$PROJECT_DIR/BitNet.code-workspace"

echo "[SUCCESS] VSCode opened with BitNet.cpp environment activated."
