@echo off
echo [INFO] Activating BitNet.cpp environment...
call .venv\Scripts\activate.bat
echo [SUCCESS] BitNet.cpp environment is now ACTIVE
echo.
python bitnet.py %*
