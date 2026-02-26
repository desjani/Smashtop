# Smashtop

Smashtop is a standalone Windows application designed as a toy for babies. It locks the system into a full-screen mode, allowing the user to mash keys and see colorful visual responses without interfering with the underlying operating system.

## Features

- **Full Screen Lockout**: Prevents minimizing or switching apps.
- **System Key Blocking**: Blocks Windows key, Alt-Tab, etc. (Requires Admin Privileges for hooks).
- **Interactive Visuals**: Colorful shapes and text appear on keypress.
- **Safety**: 
    - **Exit**: `Ctrl + Shift + Q`
    - **Settings**: `Ctrl + Shift + S` (Placeholder)

## Requirements

- Python 3.x
- `keyboard` library (for global hooks)
- `tkinter` (usually included with Python)

## Installation

1. Install Python 3.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the App

Run the application with Administrator/Root privileges (required to block system keys):

### Windows
Run as Administrator:
```bash
python main.py
```

### macOS
Run with sudo to enable global key hooks (optional but recommended for better lockout):
```bash
sudo python main.py
```

## Building the Executable

### Windows
```bash
pyinstaller Smashtop.spec
```
The executable will be in `dist/Smashtop.exe`.

### macOS
**Note:** You must run this command on a macOS machine to build the Mac app.
```bash
pyinstaller Smashtop_Mac.spec
```
This will create `dist/Smashtop.app`. 
- **Distribution:** Right-click `Smashtop.app` and choose "Compress" to create a ZIP file. Send this ZIP to users.
- **Installation:** Users just unzip and drag the app to their Applications folder. Double-click to run. No terminal required.

## Alternate Installation (using `uv`)

You can also use [uv](https://docs.astral.sh/uv/) to manage dependencies.

1. Install `uv` using [their installation instructions](https://docs.astral.sh/uv/getting-started/installation/).
2. (optional) `uv sync`.
3. `uv run main.py` (or `uv run python main.py` if you prefer).
