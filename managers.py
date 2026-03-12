import pygame
import os
import platform

# Optional PIL for better text/emoji rendering
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class FontManager:
    def __init__(self):
        self.fonts = {}
        self.surfaces = {}
        # Try to find a nice system font
        self.font_name = pygame.font.get_default_font()

    def render(self, text, size, color):
        if size not in self.fonts:
            self.fonts[size] = pygame.font.Font(self.font_name, size)
            
        surf_key = (text, size, color)
        if surf_key not in self.surfaces:
            self.surfaces[surf_key] = self.fonts[size].render(text, True, color)
        
        return self.surfaces[surf_key]

class EmojiRenderer:
    def __init__(self):
        self.font = None
        self.cache = {}
        if PIL_AVAILABLE:
            # Try to load a known emoji font
            # Windows: "seguiemj.ttf"
            # Mac: "Apple Color Emoji.ttc"
            # Linux: "NotoColorEmoji.ttf"
            font_path = "arial.ttf" # Fallback
            
            system = platform.system()
            if system == "Windows":
                font_path = "seguiemj.ttf"
            elif system == "Darwin":
                font_path = "/System/Library/Fonts/Apple Color Emoji.ttc"
            elif system == "Linux":
                # Try finding a color emoji font, or use local if downloaded
                font_paths_to_try = [
                    "NotoColorEmoji.ttf",
                    "/usr/share/fonts/google-noto-color-emoji-fonts/Noto-COLRv1.ttf",
                    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
                ]
                for p in font_paths_to_try:
                    if os.path.exists(p):
                        font_path = p
                        break

            try:
                self.font_path = font_path
            except Exception:
                self.font_path = None
    
    def render(self, char, size):
        cache_key = (char, size)
        if cache_key in self.cache:
            return self.cache[cache_key]

        if not PIL_AVAILABLE:
            # Fallback for no PIL: simple rendered text
            font_name = "segoeuiemoji" if platform.system() == "Windows" else "applecoloremoji"
            f = pygame.font.SysFont(font_name, size)
            if not f: # double fallback
                 f = pygame.font.SysFont("arial", size)
            result = f.render(char, True, (255,255,255))
            self.cache[cache_key] = result
            return result
        
        try:
            # Check if font path is absolute and exists, if not let Pillow try to find it
            if self.font_path and os.path.isabs(self.font_path) and not os.path.exists(self.font_path):
                 # Path is absolute but missing, fallback
                 self.font_path = "arial.ttf" 
            
            # CBDT/CBLC colored emoji fonts require an exact pixel size matching their internal bitmaps (often 109px)
            # We render it at fixed resolution, then scale it down/up using Pillow.
            base_size = 109
            
            try:
                # Type safe font path to avoid 'str | None' errors
                fp = self.font_path if self.font_path else "arial.ttf"
                pil_font = ImageFont.truetype(fp, base_size)
            except Exception:
                # Full fallback to default font and generic size
                pil_font = ImageFont.load_default()
            
            # Create a larger canvas to avoid clipping. 
            w, h = int(base_size * 3), int(base_size * 3)
            
            img = Image.new("RGBA", (w, h), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            # Draw centered
            draw.text((w/2, h/2), char, font=pil_font, embedded_color=True, anchor="mm")
            
            # Crop it back down (optional, but saves texture memory)
            bbox = img.getbbox()
            if bbox:
                img = img.crop(bbox)
            
            # Scale to requested size while preserving aspect ratio
            img_w, img_h = img.size
            if img_w > 0 and img_h > 0:
                aspect = img_w / img_h
                if img_w > img_h:
                    target_w, target_h = size, int(size / aspect)
                else:
                    target_h, target_w = size, int(size * aspect)
                img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # Convert to Pygame
            raw_str = img.tobytes("raw", "RGBA")
            result = pygame.image.fromstring(raw_str, img.size, "RGBA")
            self.cache[cache_key] = result
            return result
        except Exception as e:
            print(f"Emoji render error: {e}")
            f = pygame.font.SysFont("arial", int(size/2))
            result = f.render(char, True, (255,255,255))
            self.cache[cache_key] = result
            return result


