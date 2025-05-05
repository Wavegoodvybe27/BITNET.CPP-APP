# PowerShell script to open VSCode with BitNet environment activated
Write-Host "[INFO] Opening BitNet.cpp project with environment activated..."

# Get the current directory
$projectDir = $PSScriptRoot

# Check if VSCode is installed
$vscodeCmd = Get-Command code -ErrorAction SilentlyContinue
if (-not $vscodeCmd) {
    Write-Host "[ERROR] VSCode is not found in PATH. Please install VSCode or add it to your PATH."
    exit 1
}

# Check if the environment exists
if (-not (Test-Path "$projectDir\.venv")) {
    Write-Host "[WARNING] BitNet.cpp environment not found. Setting it up now..."
    & "$projectDir\setup_env.bat"
}

# Open VSCode with the workspace
Write-Host "[INFO] Opening VSCode with BitNet.cpp workspace..."
& code "$projectDir\BitNet.code-workspace"

Write-Host "[SUCCESS] VSCode opened with BitNet.cpp environment activated."
