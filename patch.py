import re

with open('main.py', 'r') as f: content = f.read()

replacement = """
            elif system == "Linux":
                keys_to_block = [
                    'windows', 'left windows', 'right windows', 
                    'super', 'left super', 'right super', 'meta',
                    'alt', 'left alt', 'right alt',
                    'ctrl', 'left ctrl', 'right ctrl',
                    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
                    'tab', 'escape', 'menu'
                ]
                # Block all common compositor/window manager shortcuts directly
                try: keyboard.add_hotkey('alt+tab', lambda: None, suppress=True)
                except: pass
                try: keyboard.add_hotkey('super+space', lambda: None, suppress=True)
                except: pass
                try: keyboard.add_hotkey('super+l', lambda: None, suppress=True)
                except: pass
                try: keyboard.add_hotkey('super+d', lambda: None, suppress=True)
                except: pass
                try: keyboard.add_hotkey('super+m', lambda: None, suppress=True)
                except: pass
                try: keyboard.add_hotkey('super+tab', lambda: None, suppress=True)
                except: pass
                try: keyboard.add_hotkey('alt+f4', lambda: None, suppress=True)
                except: pass

            for key in keys_to_block:
                try:
                    keyboard.block_key(key)
                except Exception:
                    pass # Ignore if key doesn't map on specific layout

        except Exception as e:
            # Re-raise to catch Wayland root issues, etc if we want to print it
            print(f"Hook warning: {e}")"""

content = re.sub(r'\n            elif system == "Linux":[\s\S]*?print\(f"Hook warning: \{e\}"\)', replacement, content)

with open('main.py', 'w') as f: f.write(content)
