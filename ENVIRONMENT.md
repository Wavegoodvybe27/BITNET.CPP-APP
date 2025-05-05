# BitNet.cpp Environment Setup

This document explains how to set up the development environment for the BitNet.cpp project.

## Prerequisites

- Python 3.9 or higher
- CMake
- C++ compiler (Clang recommended)
- Git

## Setting Up the Environment

1. **Clone the repository with submodules**:
   ```bash
   git clone --recursive https://github.com/microsoft/BitNet.git
   cd BitNet
   ```

2. **Run the environment setup script**:
   ```bash
   # On Windows
   .\setup_env.bat

   # On Linux/macOS
   chmod +x setup_env.sh
   ./setup_env.sh
   ```

   This script will:
   - Create a Python virtual environment in the `.venv` directory
   - Install all required dependencies
   - Set up the project structure

3. **Using the application**:
   The batch/shell scripts have been updated to automatically activate the virtual environment before running the application.

   ```bash
   # On Windows
   .\bitnet-desktop.bat  # For desktop UI
   .\bitnet.bat list     # For CLI commands

   # On Linux/macOS
   ./bitnet.sh list      # For CLI commands
   ```

## Automatic Environment Activation with VSCode

For the best development experience, we've set up automatic environment activation when you open the project in VSCode:

```bash
# On Windows
open_bitnet_project.bat

# On Linux/macOS
chmod +x open_project.sh
./open_project.sh
```

This will:
1. Open VSCode with the BitNet.cpp workspace
2. Automatically activate the virtual environment
3. Set up the correct Python interpreter
4. Configure the integrated terminal to use the environment

When you close VSCode, the environment will be automatically deactivated.

## Checking Environment Status

You can check if the BitNet.cpp environment is active using the provided scripts:

```bash
# On Windows
.\check_env.bat

# On Linux/macOS
./check_env.sh
```

When the environment is active, you'll see:
1. `(.venv)` at the beginning of your command prompt
2. A success message when running the check script
3. A success message when running any of the application scripts

If the environment is not active, you can activate it manually:

```bash
# On Windows
call .venv\Scripts\activate.bat

# On Linux/macOS
source .venv/bin/activate
```

## Project Structure

- `.venv/`: Python virtual environment (not tracked by Git)
- `models/`: Directory for downloaded models (not tracked by Git)
- `logs/`: Directory for log files (not tracked by Git)
- `BitNet/`: Core BitNet.cpp code
- `static/`: Static files for the web UI
- `ui/`: Desktop UI code

## Adding New Dependencies

If you need to add new dependencies to the project, add them to the appropriate requirements file:

- `requirements.txt`: Core dependencies for CLI and API
- `requirements_desktop.txt`: Additional dependencies for the desktop UI

Then run the setup script again to install the new dependencies.
