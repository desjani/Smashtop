import re

with open('main.py', 'r') as f: content = f.read()

replacement = """    def setup_hooks(self):
        if not KEYBOARD_AVAILABLE:
            return
        
        system = platform.system()
        try:
            # Universal Keys to block when app is running
            keys_to_block = []
            
            if system == "Windows":
                keys_to_block = [
                    'left windows', 'right windows', 'menu',
                    'alt', 'left alt', 'right alt',
                    'ctrl', 'left ctrl', 'right ctrl',
                    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
                    'tab', 'shift', 'left shift', 'right shift',
                    'escape', 'insert', 'delete', 'home', 'end', 'page up', 'page down',
                    'esc'
                ]
                # Try to disable common shortcuts entirely
                shortcuts = ['alt+tab', 'alt+f4', 'ctrl+esc', 'ctrl+shift+esc', 'win+d', 'win+l', 'win+r']
                for shortcut in shortcuts:
                    try: keyboard.add_hotkey(shortcut, lambda: None, suppress=True)
                    except: pass
                
            elif system == "Darwin": # macOS
                keys_to_block = [
                    'command', 'left command', 'right command',
                    'option', 'left option', 'right option',
                    'control', 'left ctrl', 'right ctrl',
                    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
                    'tab', 'escape', 'esc'
                ]
                shortcuts = ['command+tab', 'command+space', 'command+q', 'command+w', 'command+option+esc']
                for shortcut in shortcuts:
                    try: keyboard.add_hotkey(shortcut, lambda: None, suppress=True)
                    except: pass

            elif system == "Linux":
                keys_to_block = [
                    'windows', 'left windows', 'right windows', 
                    'super', 'left super', 'right super', 'meta',
                    'alt', 'left alt', 'right alt',
                    'ctrl', 'left ctrl', 'right ctrl',
                    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
                    'tab', 'escape', 'menu', 'esc'
                ]
                # Block all common compositor/window manager shortcuts directly
                shortcuts = [
                    'alt+tab', 'super+space', 'super+l', 'super+d', 'super+m', 'super+tab', 
                    'alt+f4', 'ctrl+alt+t', 'super+a', 'super+w', 'super+s', 'super+v',
                    'windows+d', 'windows+l'
                ]
                for shortcut in shortcuts:
                    try: keyboard.add_hotkey(shortcut, lambda: None, suppress=True)
                    except: pass
                
            for key in keys_to_block:
                try:
                    keyboard.block_key(key)
                except Exception:
                    pass # Ignore if key doesn't map on specific layout

        except Exception as e:
            # Note: on Linux this requires sudo to actually hook the keys via this module
            print(f"Hook warning: {e}")"""

content = re.sub(r'    def setup_hooks\(self\):[\s\S]*?(?=    def play_sound\(self, event=None\):)', replacement + '\n\n', content)

with open('main.py', 'w') as f: f.write(content)
