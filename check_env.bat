@echo off
if exist .venv (
    echo [INFO] BitNet.cpp environment exists.
    
    REM Check if the environment is activated
    if defined VIRTUAL_ENV (
        echo [SUCCESS] BitNet.cpp environment is ACTIVE.
        echo Current environment: %VIRTUAL_ENV%
    ) else (
        echo [WARNING] BitNet.cpp environment exists but is NOT ACTIVE.
        echo Run 'call .venv\Scripts\activate.bat' to activate it.
    )
) else (
    echo [ERROR] BitNet.cpp environment does not exist.
    echo Run 'setup_env.bat' to create it.
)
