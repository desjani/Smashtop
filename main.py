import pygame
import random
import sys
import math
import platform
import threading
from typing import List, Tuple, Dict, Optional

# Optional imports for system locking
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

# Optional PIL for better text/emoji rendering
try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Constants
WIDTH, HEIGHT = 0, 0 # Will be set on init
FPS = 60
BACKGROUND_COLORS = {
    "Black": (0, 0, 0),
    "White": (255, 255, 255),
    "Navy": (0, 0, 128),
    "Dark Gray": (34, 34, 34)
}

COLORS = [
    (255, 0, 0),    # Red
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (255, 255, 0),  # Yellow
    (128, 0, 128),  # Purple
    (255, 165, 0),  # Orange
    (0, 255, 255),  # Cyan
    (255, 0, 255)   # Magenta
]

def random_color():
    return random.choice(COLORS)

class Particle:
    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.alive = True
        self.scale = 0.1
        self.target_scale = 1.0
        self.state = "in" # in, active, out
        self.lifetime = 255
        self.fade_speed = 5

    def update(self, dt):
        if self.state == "in":
            self.scale = min(self.target_scale, self.scale + 2.0 * dt)
            if self.scale >= self.target_scale:
                self.state = "active"
        elif self.state == "out":
            self.scale -= 2.0 * dt
            if self.scale <= 0:
                self.alive = False

    def draw(self, surface):
        pass

    def kill(self):
        self.state = "out"

class ShapeParticle(Particle):
    def __init__(self, x, y, color, shape_type):
        super().__init__(x, y, color)
        self.shape_type = shape_type # oval, triangle, square, pentagon, hexagon, star
        self.angle = random.uniform(0, 360)
        self.spin_speed = random.choice([-60, -30, 30, 60])
        self.size = random.randint(62, 250)

    def update(self, dt):
        super().update(dt)
        self.angle += self.spin_speed * dt

    def draw(self, surface):
        current_size = self.size * self.scale
        if current_size <= 0: return

        if self.shape_type == 'oval':
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(current_size/2), width=5)
        else:
            self._draw_polygon(surface, current_size)

    def _draw_polygon(self, surface, size):
        points = []
        sides = 3
        if self.shape_type == 'square': sides = 4
        elif self.shape_type == 'pentagon': sides = 5
        elif self.shape_type == 'hexagon': sides = 6
        
        radius = size / 2
        
        if self.shape_type == 'star':
            points = []
            inner_radius = radius * 0.4
            for i in range(10):
                curr_r = radius if i % 2 == 0 else inner_radius
                angle_rad = math.radians(self.angle + i * 36)
                px = self.x + math.cos(angle_rad) * curr_r
                py = self.y + math.sin(angle_rad) * curr_r
                points.append((px, py))
            pygame.draw.lines(surface, self.color, True, points, width=5)
            # pygame.draw.polygon(surface, self.color, points, width=5) # Closed simple polygon
        else:
            angle_step = 360 / sides
            for i in range(sides):
                angle_rad = math.radians(self.angle + i * angle_step)
                px = self.x + math.cos(angle_rad) * radius
                py = self.y + math.sin(angle_rad) * radius
                points.append((px, py))
            pygame.draw.polygon(surface, self.color, points, width=5)

class TextParticle(Particle):
    def __init__(self, x, y, color, char, font_manager):
        super().__init__(x, y, color)
        self.char = char
        self.font_manager = font_manager
        self.size = random.randint(100, 250)
        self.spin_speed = random.choice([-20, 20])
        self.angle = 0

    def update(self, dt):
        super().update(dt)
        self.angle += self.spin_speed * dt

    def draw(self, surface):
        s = self.size * self.scale
        if s < 10: return
        
        surf = self.font_manager.render(self.char, int(s), self.color)
        if surf:
            # Rotate
            rotated_surf = pygame.transform.rotate(surf, self.angle)
            rect = rotated_surf.get_rect(center=(self.x, self.y))
            surface.blit(rotated_surf, rect)

class EmojiParticle(Particle):
    def __init__(self, x, y, char, emoji_renderer):
        super().__init__(x, y, (255,255,255))
        self.char = char
        self.renderer = emoji_renderer # Helper to render emoji to surface
        self.size = random.randint(100, 200)
        self.image = self.renderer.render(self.char, self.size)
        self.target_scale = 1.2
    
    def update(self, dt):
        super().update(dt)
        if self.state == "in" and self.scale >= 1.2:
             self.state = "settle"
        elif self.state == "settle":
             self.scale -= 1.0 * dt
             if self.scale <= 1.0:
                 self.scale = 1.0
                 self.state = "active"
    
    def draw(self, surface):
        if not self.image: return
        # Scale image
        curr_size = int(self.size * self.scale)
        if curr_size <= 1: return
        
        # Performance: Scale only if size changed significantly? 
        # For now, just scale every frame (pygame is fast enough for <50 objects)
        scaled = pygame.transform.scale(self.image, (curr_size, curr_size))
        rect = scaled.get_rect(center=(self.x, self.y))
        surface.blit(scaled, rect)

class FireworkParticle(Particle):
    def __init__(self, x, target_y, game_ref):
        super().__init__(x, game_ref.height, random_color())
        self.target_y = target_y
        self.game = game_ref
        self.vy = -800 # Pixels per second
        self.state = "launch"

    def update(self, dt):
        if self.state == "launch":
            self.y += self.vy * dt
            self.vy *= 0.98 # Drag
            
            if self.y <= self.target_y or self.vy > -50:
                self.explode()
        elif self.state == "out":
            self.alive = False

    def explode(self):
        self.state = "out"
        num_particles = random.randint(30, 60)
        color = self.color if random.random() > 0.3 else None
        
        for _ in range(num_particles):
            p = ExplosionParticle(self.x, self.y, color or random_color())
            self.game.add_particle(p)
    
    def draw(self, surface):
        if self.state == "launch":
            pygame.draw.line(surface, self.color, (self.x, self.y), (self.x, self.y + 20), 4)

class ExplosionParticle(Particle):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(100, 400)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = random.uniform(1.0, 2.0)
        self.gravity = 200

    def update(self, dt):
        self.life -= dt
        if self.life <= 0:
            self.alive = False
            return
        
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.vx *= 0.99

    def draw(self, surface):
        alpha = int((self.life / 2.0) * 255)
        if alpha < 0: alpha = 0
        # Pygame doesn't do alpha on primitives easily without a surface
        # We'll just draw small circles
        if alpha > 10:
           pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)

class FontManager:
    def __init__(self):
        self.fonts = {}
        # Try to find a nice system font
        self.font_name = pygame.font.get_default_font()

    def render(self, text, size, color):
        key = (size)
        if key not in self.fonts:
            self.fonts[key] = pygame.font.Font(self.font_name, size)
        
        return self.fonts[key].render(text, True, color)

class EmojiRenderer:
    def __init__(self):
        self.font = None
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
                font_path = "NotoColorEmoji.ttf" # might vary
            
            try:
                self.font_path = font_path
            except:
                self.font_path = None
    
    def render(self, char, size):
        if not PIL_AVAILABLE:
            # Fallback for no PIL: simple rendered text
            f = pygame.font.SysFont("segoeuiemoji", size)
            return f.render(char, True, (255,255,255))
        
        try:
            pil_font = ImageFont.truetype(self.font_path, size)
            # Get size
            bbox = pil_font.getbbox(char)
            # w = bbox[2]
            # h = bbox[3] # This often underestimates for emojis, hardcode square usually safe
            w, h = size + 20, size + 20
            
            img = Image.new("RGBA", (w, h), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            # Draw centered
            draw.text((w/2, h/2), char, font=pil_font, embedded_color=True, anchor="mm")
            
            # Convert to Pygame
            raw_str = img.tobytes("raw", "RGBA")
            return pygame.image.fromstring(raw_str, img.size, "RGBA")
        except Exception as e:
            # print(f"Emoji render error: {e}")
            f = pygame.font.SysFont("arial", int(size/2))
            return f.render(char, True, (255,255,255))

class SmashtopGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Display setup
        info = pygame.display.Info()
        self.width = info.current_w
        self.height = info.current_h
        # self.flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
        # On some systems, explicit resolution is safer than (0,0)
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN | pygame.NOFRAME)
        pygame.display.set_caption("Smashtop")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Settings
        self.bg_name = "Black"
        self.theme = "Shapes" # Shapes, Fireworks, Emoji, Paint, Sea
        self.sound_enabled = True
        self.max_objects = 50
        
        self.particles = []
        self.font_manager = FontManager()
        self.emoji_renderer = EmojiRenderer()
        
        # Lockout state
        self.locked = True
        self.setup_hooks()
        
        # UI state
        self.show_settings = False
        self.settings_font = pygame.font.SysFont("arial", 24)

    def setup_hooks(self):
        if not KEYBOARD_AVAILABLE:
            return
        
        # Block system keys on Windows
        if platform.system() == "Windows":
            try:
                # Block windows keys
                keyboard.block_key('left windows')
                keyboard.block_key('right windows')
                keyboard.block_key('menu')
                # We can't easily block Alt-Tab securely without low-level hooks, 
                # but 'keyboard' does a decent job if we just swallow the events or set the app to topmost
                # Pygame fullscreen usually captures Alt-Tab if 'exclusive' type modes are used, 
                # but modern Windows DWM is smart. 
                # We rely on being topmost and capturing focus.
            except Exception as e:
                print(f"Hook warning: {e}")

    def play_sound(self):
        if not self.sound_enabled: return
        # Generate simple sound? Pygame mixer uses Sound objects.
        # Generating sound buffers in code is possible but complex.
        # We'll rely on a simple synthesizer approach using numpy if available or just skip for now 
        # to focus on visual perf.
        # Simplest: Just reuse winsound if on windows for "beep" since it's easy, 
        # but that blocks? No, winsound.Beep blocks. winsound.MessageBeep is async but limited.
        # Better: Create a few standard beep Sound objects using array.
        pass # Todo: proper sound synth

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                # Safety Exits
                mods = pygame.key.get_mods()
                is_ctrl = mods & pygame.KMOD_CTRL
                is_shift = mods & pygame.KMOD_SHIFT
                is_alt = mods & pygame.KMOD_ALT
                
                if event.key == pygame.K_q and is_ctrl and is_shift:
                    self.running = False
                elif event.key == pygame.K_o and is_ctrl and is_shift and is_alt:
                    self.show_settings = not self.show_settings
                elif event.key == pygame.K_s and is_ctrl and is_shift and is_alt: # Alt shortcut
                     self.show_settings = not self.show_settings
                
                elif self.show_settings:
                    self.handle_settings_input(event)
                else:
                    self.spawn_object(event)

    def handle_settings_input(self, event):
        # Very simple settings navigation
        if event.key == pygame.K_1: self.theme = "Shapes"
        elif event.key == pygame.K_2: self.theme = "Fireworks"
        elif event.key == pygame.K_3: self.theme = "Emoji"
        
        elif event.key == pygame.K_c: 
            # Cycle colors
            keys = list(BACKGROUND_COLORS.keys())
            idx = keys.index(self.bg_name)
            self.bg_name = keys[(idx + 1) % len(keys)]
        
        elif event.key == pygame.K_ESCAPE:
            self.show_settings = False

    def spawn_object(self, event):
        x = random.randint(100, self.width - 100)
        y = random.randint(100, self.height - 100)
        
        # Limit objects
        if len(self.particles) > self.max_objects:
            # Kill oldest
            self.particles[0].kill()
        
        if self.theme == "Fireworks":
            self.particles.append(FireworkParticle(x, y, self))
        elif self.theme == "Emoji":
            try:
                char = event.unicode
                # If char is not printable or empty, pick random emoji
                emojis = ['😀', '🐶', '🐱', '🍎', '⚽', '🚗', '🌈']
                if not char or not char.strip():
                   char = random.choice(emojis)
                # But typically we want big emojis even for letters? 
                # Let's just pick random emojis for now if in emoji mode
                char = random.choice(emojis)
                self.particles.append(EmojiParticle(x, y, char, self.emoji_renderer))
            except: pass
        else: # Shapes
            if event.unicode and event.unicode.strip() and event.unicode.isalnum():
                self.particles.append(TextParticle(x, y, random_color(), event.unicode.upper(), self.font_manager))
            else:
                shape = random.choice(['oval', 'triangle', 'square', 'pentagon', 'star'])
                self.particles.append(ShapeParticle(x, y, random_color(), shape))

    def update(self, dt):
        # Filter alive
        self.particles = [p for p in self.particles if p.alive]
        for p in self.particles:
            p.update(dt)

    def draw(self):
        bg = BACKGROUND_COLORS[self.bg_name]
        self.screen.fill(bg)
        
        # Draw particles
        for p in self.particles:
            p.draw(self.screen)
        
        # Overlay settings
        if self.show_settings:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0,0,0, 180))
            self.screen.blit(overlay, (0,0))
            
            menu_text = [
                "SETTINGS (Press keys to change)",
                "-----------------------------",
                f"[1] Theme: Shapes {'(Active)' if self.theme == 'Shapes' else ''}",
                f"[2] Theme: Fireworks {'(Active)' if self.theme == 'Fireworks' else ''}",
                f"[3] Theme: Emoji {'(Active)' if self.theme == 'Emoji' else ''}",
                "",
                f"[C] Background: {self.bg_name}",
                "",
                "[Esc] Close Menu",
                "[Ctrl+Shift+Q] Quit Game"
            ]
            
            y = 100
            for line in menu_text:
                surf = self.settings_font.render(line, True, (255, 255, 255))
                rect = surf.get_rect(center=(self.width/2, y))
                self.screen.blit(surf, rect)
                y += 40
        else:
             # Draw quiet exit instruction
             inst = self.settings_font.render("Ctrl+Shift+Q to Quit | Ctrl+Alt+Shift+O for Settings", True, (100, 100, 100))
             rect = inst.get_rect(center=(self.width/2, self.height - 30))
             self.screen.blit(inst, rect)

        pygame.display.flip()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0 # DT in seconds
            self.handle_input()
            self.update(dt)
            self.draw()
            
            # Ensure focus
            if platform.system() == "Windows" and not self.show_settings:
                 # Check if we lost focus? Pygame handles this mostly by grabbing input
                 pass

        pygame.quit()
        if KEYBOARD_AVAILABLE:
            try: keyboard.unhook_all()
            except: pass
        sys.exit()

if __name__ == "__main__":
    game = SmashtopGame()
    game.run()
