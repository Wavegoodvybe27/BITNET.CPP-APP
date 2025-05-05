@echo off
echo [INFO] Setting up BitNet.cpp environment...

REM Create virtual environment if it doesn't exist
if not exist .venv (
    echo [INFO] Creating virtual environment...
    python -m venv .venv
) else (
    echo [INFO] Virtual environment already exists.
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

REM Install dependencies
echo [INFO] Installing dependencies...
pip install -r requirements.txt
pip install -r requirements_desktop.txt

echo [SUCCESS] Environment setup complete!
echo.
echo [INFO] The BitNet.cpp environment is now ACTIVE.
echo [INFO] You can verify this by seeing (.venv) at the beginning of your command prompt.
echo [INFO] To check environment status anytime, run 'check_env.bat'.
