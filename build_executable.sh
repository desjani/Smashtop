#!/bin/bash
# Local build script for Linux/macOS

# Exit immediately if a command exits with a non-zero status
set -e

echo "=== Smashtop Build Script ==="
echo "1. Checking Python environment..."

# Determine python command
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python is not installed. Please install Python 3.10+."
    exit 1
fi

# Set up virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment in .venv..."
    $PYTHON_CMD -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt pyinstaller

# Run PyInstaller
echo "Building single-file executable..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    pyinstaller Smashtop_Mac.spec
    echo "Build complete! The executable is at dist/Smashtop and Smashtop.app bundle is at dist/Smashtop.app"
else
    # Linux (or other Unix-like OS)
    pyinstaller Smashtop.spec
    echo "Build complete! The executable is at dist/Smashtop"
fi
