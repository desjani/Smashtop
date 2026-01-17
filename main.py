import pygame
import random
import sys
import math
import platform
import threading
import array
import struct
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
        self.spin_speed = random.choice([-100, -50, 50, 100])
        self.angle = 0
        self.angle_target = 0

    def update(self, dt):
        super().update(dt)
        # While growing, spin fast
        if self.state == "in":
            self.angle += self.spin_speed * dt
        # Once active, settle to 0
        elif self.state == "active":
            # Simple lerp to 0
            if abs(self.angle) > 1:
                self.angle *= 0.90 # Decay angle
            else:
                self.angle = 0

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
        
        scaled = pygame.transform.scale(self.image, (curr_size, curr_size))
        rect = scaled.get_rect(center=(self.x, self.y))
        surface.blit(scaled, rect)

class FireworkParticle(Particle):
    def __init__(self, x, target_y, game_ref):
        super().__init__(x, game_ref.height, random_color())
        self.target_y = target_y
        self.game = game_ref
        self.vy = -1200 # Faster launch
        self.state = "launch"

    def update(self, dt):
        if self.state == "launch":
            self.y += self.vy * dt
            self.vy *= 0.99  # Less drag
            
            # Explode if reached target OR if we slowed down too much
            if self.y <= self.target_y or self.vy > -100:
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
        if alpha > 10:
           pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)

# --- Sea Theme Classes ---

class BubbleParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, (200, 200, 255))
        self.vy = random.uniform(-100, -250)
        self.wobble_phase = random.uniform(0, 100)
        self.size = random.randint(10, 80) # More varied size (was 20-60)
        
    def update(self, dt):
        super().update(dt)
        self.y += self.vy * dt
        self.wobble_phase += 5 * dt
        self.x += math.sin(self.wobble_phase) * 100 * dt
        
        if self.y < -50: self.alive = False

    def draw(self, surface):
        s = int(self.size * self.scale)
        if s > 2:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(s/2), 2)
            # Shine
            pygame.draw.circle(surface, (255,255,255), (int(self.x - s/6), int(self.y - s/6)), int(s/8))

class FishParticle(Particle):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.vx = random.choice([-200, -150, 150, 200])
        self.direction = 1 if self.vx > 0 else -1
        self.size = random.randint(40, 140) # Varied (was 60-120)

    def update(self, dt):
        super().update(dt)
        self.x += self.vx * dt
        screen_w = pygame.display.get_surface().get_width()
        if (self.vx > 0 and self.x > screen_w + 100) or (self.vx < 0 and self.x < -100):
            self.alive = False

    def draw(self, surface):
        s = self.size * self.scale
        d = self.direction
        x, y = self.x, self.y
        
        # Simple Fish Polygon
        # Body
        body_pts = [
            (x + 30*d*self.scale, y),
            (x - 30*d*self.scale, y - 20*self.scale),
            (x - 30*d*self.scale, y + 20*self.scale)
        ]
        # Tail
        tail_pts = [
            (x - 30*d*self.scale, y),
            (x - 50*d*self.scale, y - 25*self.scale),
            (x - 50*d*self.scale, y + 25*self.scale)
        ]
        
        pygame.draw.polygon(surface, self.color, body_pts)
        pygame.draw.polygon(surface, self.color, tail_pts)
        pygame.draw.circle(surface, (255,255,255), (int(x + 15*d*self.scale), int(y - 5*self.scale)), int(4*self.scale))

class JellyfishParticle(Particle):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.vy = random.uniform(-60, -120) # Increased speed (was -30 to -80)
        self.size = random.randint(50, 200) # Varied size (was 80-150)
        self.pulse_phase = random.uniform(0, 10)
        
    def update(self, dt):
        super().update(dt)
        self.y += self.vy * dt
        self.pulse_phase += 5 * dt
        if self.y < -150: self.alive = False

    def draw(self, surface):
        s = self.size * self.scale
        pulse = 1.0 + 0.1 * math.sin(self.pulse_phase)
        w = int(s * pulse)
        h = int(s * 0.8 * pulse)
        
        rect = pygame.Rect(self.x - w/2, self.y - h/2, w, h)
        pygame.draw.arc(surface, self.color, rect, 0, math.pi, 5)
        pygame.draw.line(surface, self.color, (self.x - w/2, self.y), (self.x + w/2, self.y), 2)
        
        # Tentacles
        for i in range(3):
            off = (i - 1) * (w/4)
            start = (self.x + off, self.y)
            end_y = self.y + h + (math.sin(self.pulse_phase + i)*10)
            pygame.draw.line(surface, self.color, start, (self.x + off + math.sin(self.pulse_phase)*5, end_y), 2)

class SharkParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, (100, 100, 100)) # Dark Gray
        self.vx = random.choice([-300, -250, 250, 300]) # Fast
        self.direction = 1 if self.vx > 0 else -1
        self.size = random.randint(150, 250)

    def update(self, dt):
        super().update(dt)
        self.x += self.vx * dt
        screen_w = pygame.display.get_surface().get_width()
        if (self.vx > 0 and self.x > screen_w + 200) or (self.vx < 0 and self.x < -200):
            self.alive = False

    def draw(self, surface):
        x, y = self.x, self.y
        d = self.direction
        s = self.scale
        
        # Shark Shape
        # Main Body (Oval-ish polygon)
        pts = [
            (x + 80*d*s, y),       # Nose
            (x + 20*d*s, y - 30*s), # Top head
            (x - 20*d*s, y - 40*s), # Dorsal start
            (x - 40*d*s, y - 70*s), # Dorsal fin top
            (x - 60*d*s, y - 30*s), # Dorsal end
            (x - 100*d*s, y),       # Tail base
            (x - 140*d*s, y - 40*s), # Top tail
            (x - 140*d*s, y + 40*s), # Bot tail
            (x - 100*d*s, y + 10*s), # Tail base bot
            (x - 20*d*s, y + 30*s),  # Belly
            (x + 40*d*s, y + 20*s),  # Chin
        ]
        pygame.draw.polygon(surface, self.color, pts)
        # Eye
        pygame.draw.circle(surface, (255,255,255), (int(x + 50*d*s), int(y - 10*s)), int(5*s))

class WhaleParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, (50, 60, 100)) # Dark Blue
        self.vx = random.choice([-100, -80, 80, 100]) # Slow
        self.direction = 1 if self.vx > 0 else -1
        self.size = random.randint(250, 400) # Big

    def update(self, dt):
        super().update(dt)
        self.x += self.vx * dt
        screen_w = pygame.display.get_surface().get_width()
        if (self.vx > 0 and self.x > screen_w + 300) or (self.vx < 0 and self.x < -300):
            self.alive = False

    def draw(self, surface):
        x, y = self.x, self.y
        d = self.direction
        s = self.scale
        
        # Simple Whale Shape
        pts = [
            (x + 100*d*s, y + 20*s),   # Nose
            (x + 40*d*s, y - 60*s),    # Head top
            (x - 60*d*s, y - 60*s),    # Back
            (x - 120*d*s, y - 10*s),   # Tail base
            (x - 180*d*s, y - 40*s),   # Tail fin top
            (x - 180*d*s, y + 40*s),   # Tail fin bot
            (x - 120*d*s, y + 30*s),   # Belly tail
            (x + 20*d*s, y + 60*s),    # Belly
        ]
        pygame.draw.polygon(surface, self.color, pts)
        # Eye
        pygame.draw.circle(surface, (255,255,255), (int(x + 60*d*s), int(y - 10*s)), int(4*s))

class DolphinParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, (150, 150, 200)) # Light Blue/Gray
        self.vx = random.choice([-200, -180, 180, 200])
        self.direction = 1 if self.vx > 0 else -1
        self.size = random.randint(120, 180)
        self.y_start = y
        self.time = 0

    def update(self, dt):
        super().update(dt)
        self.time += dt
        self.x += self.vx * dt
        # Swim motion (sine wave)
        self.y = self.y_start + math.sin(self.time * 3) * 50
        
        screen_w = pygame.display.get_surface().get_width()
        if (self.vx > 0 and self.x > screen_w + 200) or (self.vx < 0 and self.x < -200):
            self.alive = False

    def draw(self, surface):
        x, y = self.x, self.y
        d = self.direction
        s = self.scale
        
        # Dolphin Shape
        pts = [
            (x + 60*d*s, y),       # Beak
            (x + 30*d*s, y - 20*s), # Forehead
            (x + 0*d*s, y - 25*s),  # Head top
            (x - 20*d*s, y - 40*s), # Dorsal fin top
            (x - 40*d*s, y - 25*s), # Mid back
            (x - 90*d*s, y - 5*s),  # Tail base
            (x - 120*d*s, y - 20*s), # Tail top
            (x - 120*d*s, y + 20*s), # Tail bot
            (x - 60*d*s, y + 15*s),  # Belly back
            (x + 0*d*s, y + 15*s),   # Belly
            (x + 40*d*s, y + 5*s),   # Throat
        ]
        pygame.draw.polygon(surface, self.color, pts)
        pygame.draw.circle(surface, (255,255,255), (int(x + 35*d*s), int(y - 5*s)), int(3*s))

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
            # Create a larger canvas to avoid clipping. 
            # Emojis can have wild bounding boxes especially with combined glyphs (ZWJ stats)
            # Using size * 2 ensures enough padding.
            w, h = int(size * 2), int(size * 2)
            
            img = Image.new("RGBA", (w, h), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            # Draw centered
            draw.text((w/2, h/2), char, font=pil_font, embedded_color=True, anchor="mm")
            
            # Crop it back down (optional, but saves texture memory)
            bbox = img.getbbox()
            if bbox:
                img = img.crop(bbox)
            
            # Convert to Pygame
            raw_str = img.tobytes("raw", "RGBA")
            return pygame.image.fromstring(raw_str, img.size, "RGBA")
        except Exception as e:
            # print(f"Emoji render error: {e}")
            f = pygame.font.SysFont("arial", int(size/2))
            return f.render(char, True, (255,255,255))

class SoundGenerator:
    def __init__(self):
        self.sounds = []
        try:
            pygame.mixer.set_num_channels(16) # Allow many overlapping sounds
            self.generate_scale()
        except Exception as e:
            print(f"Sound init failed: {e}")

    def generate_scale(self):
        # Generate C major scale notes roughly
        # Frequencies: C4...C6
        notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
        rate = 44100
        duration = 0.15 # seconds
        
        for freq in notes:
            # Generate one cycle of square wave
            # period = rate / freq
            # But plain array approach is easier filling the whole buffer
            
            n_samples = int(rate * duration)
            buf = array.array('h', [0] * n_samples)
            
            # Simple square wave
            period_samples = int(rate / freq)
            for i in range(n_samples):
                # value: max volume (32767) or min (-32768)
                # Square wave: high for half period, low for half
                if (i % period_samples) < (period_samples // 2):
                    value = 10000 
                else:
                    value = -10000
                
                # Apply simple decay envelope to avoid clicking
                decay = 1.0 - (i / n_samples)
                buf[i] = int(value * decay)
                
            self.sounds.append(pygame.mixer.Sound(buffer=buf))

    def play_random(self):
        if not self.sounds: return
        try:
            s = random.choice(self.sounds)
            s.set_volume(0.3)
            s.play()
        except: pass

class SmashtopGame:
    def __init__(self):
        pygame.init()
        # Init mixer with specific settings for low latency
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        except:
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
        self.sound_generator = SoundGenerator()
        
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
        self.sound_generator.play_random()

    def add_particle(self, particle):
        self.particles.append(particle)

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
        changed = False
        # Very simple settings navigation
        if event.key == pygame.K_1 and self.theme != "Shapes": 
            self.theme = "Shapes"
            changed = True
        elif event.key == pygame.K_2 and self.theme != "Fireworks": 
            self.theme = "Fireworks"
            changed = True
        elif event.key == pygame.K_3 and self.theme != "Emoji": 
            self.theme = "Emoji"
            changed = True
        elif event.key == pygame.K_4 and self.theme != "Sea": 
            self.theme = "Sea"
            changed = True
        
        elif event.key == pygame.K_c: 
            # Cycle colors
            keys = list(BACKGROUND_COLORS.keys())
            idx = keys.index(self.bg_name)
            self.bg_name = keys[(idx + 1) % len(keys)]
            changed = True
            
        elif event.key == pygame.K_UP:
             self.max_objects += 10
             if self.max_objects > 500: self.max_objects = 500
        elif event.key == pygame.K_DOWN:
             self.max_objects -= 10
             if self.max_objects < 10: self.max_objects = 10
        
        elif event.key == pygame.K_ESCAPE:
            self.show_settings = False

        if changed:
            self.particles.clear()

    def spawn_object(self, event):
        self.play_sound()
        x = random.randint(100, self.width - 100)
        y = random.randint(100, self.height - 100)
        
        # Limit objects (Only for persistent modes like Shapes and Emoji)
        if self.theme in ["Shapes", "Emoji"] and len(self.particles) > self.max_objects:
            # Kill oldest
            self.particles[0].kill()
        
        if self.theme == "Fireworks":
            self.particles.append(FireworkParticle(x, y, self))
        elif self.theme == "Sea":
             # New logic: Ensure even proportion of species
             # Species list: Bubble, Fish, Jellyfish, Shark, Whale, Dolphin
             species = ['baby', 'fish', 'jelly', 'shark', 'whale', 'dolphin']
             
             # Check current population (simple count)
             # This is a bit expensive O(N) every keypress but N is small (<50)
             counts = {k:0 for k in species}
             for p in self.particles:
                 if isinstance(p, BubbleParticle): counts['baby'] += 1
                 elif isinstance(p, FishParticle): counts['fish'] += 1
                 elif isinstance(p, JellyfishParticle): counts['jelly'] += 1
                 elif isinstance(p, SharkParticle): counts['shark'] += 1
                 elif isinstance(p, WhaleParticle): counts['whale'] += 1
                 elif isinstance(p, DolphinParticle): counts['dolphin'] += 1
            
             # Find least represented
             min_count = min(counts.values())
             candidates = [k for k, v in counts.items() if v <= min_count]
             choice = random.choice(candidates)

             if choice == 'baby':
                 self.particles.append(BubbleParticle(x, self.height + 50))
             elif choice == 'fish':
                 spawn_x = -50 if random.random() > 0.5 else self.width + 50
                 self.particles.append(FishParticle(spawn_x, y, random_color()))
             elif choice == 'jelly':
                 self.particles.append(JellyfishParticle(x, self.height + 50, random_color()))
             elif choice == 'shark':
                 spawn_x = -200 if random.random() > 0.5 else self.width + 200
                 self.particles.append(SharkParticle(spawn_x, y))
             elif choice == 'whale':
                 spawn_x = -300 if random.random() > 0.5 else self.width + 300
                 self.particles.append(WhaleParticle(spawn_x, y)) 
             elif choice == 'dolphin':
                 spawn_x = -200 if random.random() > 0.5 else self.width + 200
                 self.particles.append(DolphinParticle(spawn_x, y))  

        elif self.theme == "Emoji":
            try:
                char = event.unicode
                # Expanded Emoji List
                emojis = [
                    '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊', '😇',
                    '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷',
                    '🍏', '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🍈', '🍒', '🍑', '🍍',
                    '🚗', '🚕', '🚙', '🚌', '🚎', '🏎', '🚓', '🚑', '🚒', '🚐', '🚚', '🚛', '🚜',
                    '⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🥅', '🏒',
                    '🌈', '☀️', '⭐', '🌟', '🌙', '☁️', '❄️', '🔥', '🎈', '🎁', '🎂', '🎨', '🎺',
                    '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞'
                ]
                if not char or not char.strip():
                   char = random.choice(emojis)
                # Just pick random emojis 80% of time for fun
                if random.random() > 0.2:
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
                f"[4] Theme: Sea {'(Active)' if self.theme == 'Sea' else ''}",
                "",
                f"[C] Background: {self.bg_name}",
                f"[Up/Down] Max Objects (Shapes/Emoji): {self.max_objects}",
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
