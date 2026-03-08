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
                shortcuts = [
                    'alt+tab', 'super+space', 'super+l', 'super+d', 'super+m', 'super+tab', 
                    'alt+f4', 'ctrl+alt+t', 'super+a', 'super+w', 'super+s', 'super+v'
                ]
                for shortcut in shortcuts:
                    try:
                        keyboard.add_hotkey(shortcut, lambda: None, suppress=True)
                    except:
                        pass
                
            # Actually process the keys_to_block array populated by Windows/Mac/Linux blocks
            for key in keys_to_block:
                try:
                    keyboard.block_key(key)
                except Exception:
                    pass # Ignore if key doesn't map on specific layout

        except Exception as e:
            # Note: on Linux requires sudo to actually block keys via this module
            print(f"Hook warning: {e}")"""

# find the linux block that got potentially cut off and properly terminate it before `play_sound`
content = re.sub(r'\n            elif system == "Linux":[\s\S]*?(?=    def play_sound\(self, event=None\):)', replacement + '\n\n', content)

with open('main.py', 'w') as f: f.write(content)
