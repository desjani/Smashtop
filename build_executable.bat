@echo off
echo === Smashtop Windows Build Script ===

:: Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH. Please install Python 3.10+.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment in .venv...
    python -m venv .venv
)

:: Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Install dependencies
echo Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

:: Build executable
echo Building Windows single-file executable...
pyinstaller Smashtop.exe.spec

echo Build complete! The executable is at dist/Smashtop.exe
pause
