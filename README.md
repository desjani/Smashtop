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

Run the application with Administrator privileges (required to block system keys):

```bash
python main.py
```
