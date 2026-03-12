import pygame
import random
import sys
import math
import platform
import threading
import array
import struct
import json
import os
from typing import List, Tuple, Dict, Optional

# Optional imports for system locking
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False


from utils import random_color, resource_path, COLORS
from managers import FontManager, EmojiRenderer
from audio import SoundGenerator

# Constants
WIDTH, HEIGHT = 0, 0 # Will be set on init
FPS = 60
BACKGROUND_COLORS = {
    "Black": (0, 0, 0),
    "White": (255, 255, 255),
    "Navy": (0, 0, 128),
    "Dark Gray": (34, 34, 34)
}

from particles import (Particle, ShapeParticle, TextParticle, EmojiParticle, 
                       FireworkParticle, BubbleParticle, FishParticle, JellyfishParticle, 
                       SharkParticle, WhaleParticle, DolphinParticle)


class SmashtopGame:
    def __init__(self):
        pygame.init()
        # Init mixer with specific settings for low latency
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
        except Exception:
            try:
                pygame.mixer.init()
            except Exception as e:
                print(f"Warning: Audio device could not be loaded: {e}. Sound will be disabled.")

        # Settings Defaults
        self.theme = "Shapes" # Shapes, Fireworks, Emoji, Paint, Sea
        self.sound_enabled = True
        self.sound_style = "synth" # "synth" or "asset"
        self.volume = 0.5
        self.max_objects = 50
        self.display_mode = "borderless" # "borderless" or "fullscreen"
        
        # Display setup
        self.num_displays = pygame.display.get_num_displays()
        self.current_display_index = 0
        
        # Background Surfaces (cached)
        self.bg_surface_fireworks = None
        self.fg_surface_fireworks = None
        self.bg_surface_sea = None

        # Load saved settings
        self.load_settings()

        self.setup_display()
        
        pygame.display.set_caption("Smashtop")
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.particles = []
        self.font_manager = FontManager()
        self.emoji_renderer = EmojiRenderer()
        self.sound_generator = SoundGenerator()
        self.sound_generator.set_style(self.sound_style)
        
        # Lockout state
        self.locked = True
        self.setup_hooks()
        
        # UI state
        self.show_settings = False
        self.settings_font = pygame.font.SysFont("arial", 24)
        
        # Input state
        self.held_keys = {}

    def load_settings(self):
        try:
            if os.path.exists("smashtop_settings.json"):
                with open("smashtop_settings.json", "r") as f:
                    data = json.load(f)
                    self.theme = data.get("theme", self.theme)
                    self.max_objects = data.get("max_objects", self.max_objects)
                    self.current_display_index = data.get("display_index", 0)
                    self.display_mode = data.get("display_mode", "borderless")
                    self.volume = data.get("volume", 0.5)
                    self.sound_enabled = data.get("sound_enabled", True)
                    self.sound_style = data.get("sound_style", "synth")

                    # Validate display index
                    if self.current_display_index >= self.num_displays:
                        self.current_display_index = 0
                        
        except Exception as e:
            print(f"Failed to load settings: {e}")

    def save_settings(self):
        try:
            data = {
                "theme": self.theme,
                "max_objects": self.max_objects,
                "display_index": self.current_display_index,
                "display_mode": self.display_mode,
                "volume": self.volume,
                "sound_enabled": self.sound_enabled,
                "sound_style": self.sound_style
            }
            with open("smashtop_settings.json", "w") as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def setup_display(self):
        # Determine flags based on mode
        flags = pygame.NOFRAME
        if self.display_mode == "fullscreen":
            flags |= pygame.FULLSCREEN

        # Use (0,0) to use the desktop resolution of the specified display
        try:
            self.screen = pygame.display.set_mode((0, 0), flags, display=self.current_display_index)
        except Exception as e:
            print(f"Failed to set display mode on monitor {self.current_display_index} with mode {self.display_mode}: {e}")
            # Fallback to default
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN | pygame.NOFRAME)
            
        w, h = self.screen.get_size()
        self.width = w
        self.height = h
        
        # Lock mouse to window to prevent accidental clicking outside
        pygame.event.set_grab(True)
        
        # Regenerate backgrounds for new size
        self.generate_backgrounds()

    def generate_backgrounds(self):
        w, h = self.width, self.height
        
        # --- Helper: Smooth Vertical Gradient ---
        def create_gradient(top_col, bot_col, height):
            # Create a 1xheight surface and fill it with gradient
            # We'll use intermediate steps
            grad = pygame.Surface((1, height))
            for y in range(height):
                t = y / height
                r = int(top_col[0] * (1-t) + bot_col[0] * t)
                g = int(top_col[1] * (1-t) + bot_col[1] * t)
                b = int(top_col[2] * (1-t) + bot_col[2] * t)
                grad.set_at((0, y), (r, g, b))
            return grad

        # --- Fireworks ---
        # BG: Dark sky with stars
        # High Def smooth gradient from Deep Black-Blue to slightly lighter horizon
        grad_surf = create_gradient((2, 0, 10), (10, 10, 40), h)
        self.bg_surface_fireworks = pygame.transform.smoothscale(grad_surf, (w, h))

        # Stars (Various sizes and brightness)
        for _ in range(300):
            sx = random.randint(0, w)
            sy = random.randint(0, int(h * 0.75))
            brightness = random.randint(100, 255)
            size = 1 if random.random() > 0.05 else 2
            pygame.draw.circle(self.bg_surface_fireworks, (brightness, brightness, brightness), (sx, sy), size)

        # Moon (Glowy)
        mx, my = int(w * 0.8), int(h * 0.2)
        # Glow
        for i in range(20, 0, -1):
            alpha = 5 + i * 2
            glow_s = pygame.Surface((i*6, i*6), pygame.SRCALPHA)
            pygame.draw.circle(glow_s, (200, 200, 255, 10), (i*3, i*3), i*3)
            self.bg_surface_fireworks.blit(glow_s, (mx - i*3, my - i*3))
        # Moon Body
        pygame.draw.circle(self.bg_surface_fireworks, (240, 240, 255), (mx, my), 30)
        # Craters
        pygame.draw.circle(self.bg_surface_fireworks, (200, 200, 220), (mx - 10, my+5), 6)
        pygame.draw.circle(self.bg_surface_fireworks, (210, 210, 230), (mx + 8, my-8), 4)

        # FG: Detailed Grass hills and trees
        self.fg_surface_fireworks = pygame.Surface((w, h), pygame.SRCALPHA)
        
        # Hills (Sine Wave Silhouettes)
        # Back hill layer (darker)
        poly_pts = [(0, h)]
        for i in range(0, w+1, 20):
            # Complex noise sum
            y_off = math.sin(i * 0.005) * 50 + math.sin(i * 0.02) * 20
            poly_pts.append((i, int(h - 100 - y_off)))
        poly_pts.append((w, h))
        pygame.draw.polygon(self.fg_surface_fireworks, (5, 15, 10), poly_pts)
        
        # Front hill layer (slightly lighter)
        poly_pts_2 = [(0, h)]
        for i in range(0, w+1, 20):
            y_off = math.sin(i * 0.003 + 2) * 40 + math.sin(i * 0.05) * 10
            poly_pts_2.append((i, int(h - 50 - y_off)))
        poly_pts_2.append((w, h))
        pygame.draw.polygon(self.fg_surface_fireworks, (10, 25, 15), poly_pts_2)

        # Detailed Trees (Recursive-ish shape)
        def draw_pine(surf, x, y, scale):
            col = (15, 30, 20)
            # Trunk
            pygame.draw.rect(surf, (20, 15, 10), (x - 4*scale, y, 8*scale, 20*scale))
            # Tiers of leaves
            tiers = 5
            for i in range(tiers):
                w_tier = (50 - i*8) * scale
                h_tier = 25 * scale
                y_tier = y - (i * 15 * scale) - 10*scale
                points = [
                    (x - w_tier, y_tier + h_tier),
                    (x, y_tier),
                    (x + w_tier, y_tier + h_tier)
                ]
                pygame.draw.polygon(surf, col, points)
                
        # Forest flank
        for i in range(8):
            scale = random.uniform(1.2, 1.8)
            draw_pine(self.fg_surface_fireworks, random.randint(20, 250), h - 40, scale)
            
        for i in range(8):
            scale = random.uniform(1.2, 1.8)
            draw_pine(self.fg_surface_fireworks, w - random.randint(20, 250), h - 40, scale)

        # --- Sea ---
        # HD Water Gradient
        top_sea = (50, 200, 230) # Caribbean Blue top
        mid_sea = (0, 100, 160)
        bot_sea = (0, 10, 40)    # Deep Abyss
        
        # Create 2-stage gradient
        grad1 = create_gradient(top_sea, mid_sea, int(h/2))
        grad2 = create_gradient(mid_sea, bot_sea, h - int(h/2))
        
        grad_full = pygame.Surface((1, h))
        grad_full.blit(grad1, (0,0))
        grad_full.blit(grad2, (0, int(h/2)))
        
        self.bg_surface_sea = pygame.transform.smoothscale(grad_full, (w, h))
        
        # Light Rays (God Rays)
        ray_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for i in range(10):
            x_start = random.randint(0, w)
            width = random.randint(20, 100)
            angle = random.uniform(-0.2, 0.2) # Radians tilt
            
            # Draw a long polygon ray
            pts = [
                (x_start, 0),
                (x_start + width, 0),
                (x_start + width + math.sin(angle)*h, h),
                (x_start + math.sin(angle)*h, h)
            ]
            # Faint white/cyan
            pygame.draw.polygon(ray_surf, (200, 255, 255, 15), pts)
        self.bg_surface_sea.blit(ray_surf, (0,0))

        # Sandy Floor (with noise texture)
        sand_h = 100
        sand_col = (210, 195, 140)
        
        # Draw base sand
        pygame.draw.rect(self.bg_surface_sea, sand_col, (0, h-sand_h, w, sand_h))
        # Use sine waves for dunes
        poly_sand = [(0, h)]
        for i in range(0, w+1, 10):
            dy = math.sin(i * 0.01) * 20 + math.sin(i*0.05) * 5
            poly_sand.append((i, int(h - sand_h - dy)))
        poly_sand.append((w, h))
        pygame.draw.polygon(self.bg_surface_sea, sand_col, poly_sand)
        
        # Add sand noise (speckles) for texture
        for i in range(3000):
            sx = random.randint(0, w)
            sy = random.randint(h - sand_h - 20, h)
            # Simple check if inside sand area (roughly)
            if sy > int(h - sand_h + math.sin(sx * 0.01) * 20): 
                shade = random.randint(-20, 20)
                r = max(0, min(255, sand_col[0] + shade))
                g = max(0, min(255, sand_col[1] + shade))
                b = max(0, min(255, sand_col[2] + shade))
                self.bg_surface_sea.set_at((sx, sy), (r,g,b))
        
        # Organic Seaweed / Coral
        def draw_seaweed(surf, x, y, tallness):
            pts = []
            segments = 10
            sway = random.uniform(0, 100) # static phase
            for i in range(segments):
                # snake up
                seg_y = y - (i * tallness / segments)
                seg_x = x + math.sin(sway + i * 0.5) * 10
                pts.append((seg_x, seg_y))
            
            # Widen the strand
            pygame.draw.lines(surf, (40, 140, 60), False, pts, 4)

        for i in range(15):
            x = random.randint(0, w)
            # Find probable floor y
            floor_y = h - sand_h + math.sin(x * 0.01) * 20 - 20 # Offset slightly down into sand
            if floor_y < h:
                draw_seaweed(self.bg_surface_sea, x, h, random.randint(50, 150))
                
        # Rocks/Coral Clumps
        for i in range(8):
            cx = random.randint(50, w-50)
            cy = h - sand_h + math.sin(cx * 0.01) * 20 + 20
            # Draw a cluster of circles
            for j in range(5):
                r = random.randint(10, 30)
                off_x = random.randint(-20, 20)
                off_y = random.randint(-10, 10)
                col = random.choice([(180, 100, 100), (100, 100, 120), (160, 80, 140)])
                pygame.draw.circle(self.bg_surface_sea, col, (cx+off_x, int(cy+off_y)), r)




    def setup_hooks(self):
        if not KEYBOARD_AVAILABLE:
            return
        
        system = platform.system()
        try:
            # Block system keys on Windows
            if system == "Windows":
                # Block windows keys
                keyboard.block_key('left windows')
                keyboard.block_key('right windows')
                keyboard.block_key('menu')
            elif system == "Darwin": # macOS
                # macOS usually requires Accessibility permissions for global hooks.
                # If we are packaged as .app, the OS should prompt the user.
                try:
                    # Cmd+Tab, Cmd+Space are hard to block without lower level APIs,
                    # but we can try to swallow other inputs or just rely on fullscreen.
                    pass 
                except Exception:
                    pass
        except Exception as e:
            print(f"Hook warning: {e}")

    def play_sound(self):
        if not self.sound_enabled: return
        
        if self.theme == "Sea":
            self.sound_generator.play('bubbles', self.volume)
        elif self.theme == "Emoji":
            self.sound_generator.play('pops', self.volume)
        elif self.theme == "Fireworks":
            self.sound_generator.play('fireworks', self.volume * 0.5) # slightly quieter launch
        else:
            self.sound_generator.play('notes', self.volume)

    def play_firework_sound(self):
        if not self.sound_enabled: return
        self.sound_generator.play('fireworks', self.volume)

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
                    self.held_keys.clear()
                    self.show_settings = not self.show_settings
                elif event.key == pygame.K_s and is_ctrl and is_shift and is_alt: # Alt shortcut
                     self.held_keys.clear()
                     self.show_settings = not self.show_settings
                
                elif self.show_settings:
                    self.handle_settings_input(event)
                else:
                    self.spawn_object(event)
                    # Start repeating
                    self.held_keys[event.key] = {
                        'event': event,
                        'next_time': pygame.time.get_ticks() + 400
                    }
            
            elif event.type == pygame.KEYUP:
                if event.key in self.held_keys:
                    del self.held_keys[event.key]

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
        
        # Removed K_c (Color Cycle) as backgrounds are now theme-locked
            
        elif event.key == pygame.K_m:
             self.current_display_index = (self.current_display_index + 1) % self.num_displays
             self.setup_display()
             changed = True

        elif event.key == pygame.K_f:
             # Toggle display mode
             if self.display_mode == "borderless":
                 self.display_mode = "fullscreen"
             else:
                 self.display_mode = "borderless"
             self.setup_display()
             changed = True

        elif event.key == pygame.K_UP:
             self.max_objects += 10
             if self.max_objects > 500: self.max_objects = 500
             self.save_settings()
        elif event.key == pygame.K_DOWN:
             self.max_objects -= 10
             if self.max_objects < 10: self.max_objects = 10
             self.save_settings()
        
        elif event.key == pygame.K_RIGHT:
             self.volume += 0.1
             if self.volume > 1.0: self.volume = 1.0
             self.play_sound() # Test sound
             self.save_settings()
        elif event.key == pygame.K_LEFT:
             self.volume -= 0.1
             if self.volume < 0.0: self.volume = 0.0
             self.play_sound() # Test sound
             self.save_settings()

        elif event.key == pygame.K_s:
             self.sound_enabled = not self.sound_enabled
             self.save_settings()

        elif event.key == pygame.K_a:
             self.sound_style = "asset" if self.sound_style == "synth" else "synth"
             self.sound_generator.set_style(self.sound_style)
             self.play_sound() # Test sound
             self.save_settings()

        elif event.key == pygame.K_ESCAPE:
            self.show_settings = False

        if changed:
            self.particles.clear()
            self.save_settings()

    def spawn_object(self, event):
        # Play generic sound unless it's Fireworks mode (handled on explosion)
        if self.theme != "Fireworks":
            self.play_sound()
            
        x = random.randint(100, self.width - 100)
        y = random.randint(100, self.height - 100)
        
        # Limit objects (Only for persistent modes like Shapes and Emoji)
        if self.theme in ["Shapes", "Emoji"]:
            # Count only particles that are not already fading out
            active_particles = [p for p in self.particles if p.state != "out"]
            if len(active_particles) >= self.max_objects:
                 # Kill the oldest active particle
                 if active_particles:
                     active_particles[0].kill()

        if self.theme == "Fireworks":
            self.add_particle(FireworkParticle(x, y, self))
        elif self.theme == "Sea":
             # Weighted selection for species
             # Higher weight = more frequent spawn
             choices = [
                 ('baby',   50), # Bubble
                 ('fish',   30),
                 ('jelly',  7),  # Jelly
                 ('shark',  7),  # Shark
                 ('whale',  1),  # Whale
                 ('dolphin', 5)  # Dolphin
             ]
             
             # Extract lists for choices
             keys = [c[0] for c in choices]
             weights = [c[1] for c in choices]
             
             choice = random.choices(keys, weights=weights, k=1)[0]

             if choice == 'baby':
                 self.add_particle(BubbleParticle(x, self.height + 50))
             elif choice == 'fish':
                 spawn_x = -50 if random.random() > 0.5 else self.width + 50
                 self.add_particle(FishParticle(spawn_x, y, random_color()))
             elif choice == 'jelly':
                 self.add_particle(JellyfishParticle(x, self.height + 50, random_color()))
             elif choice == 'shark':
                 spawn_x = -200 if random.random() > 0.5 else self.width + 200
                 self.add_particle(SharkParticle(spawn_x, y))
             elif choice == 'whale':
                 spawn_x = -300 if random.random() > 0.5 else self.width + 300
                 self.add_particle(WhaleParticle(spawn_x, y)) 
             elif choice == 'dolphin':
                 spawn_x = -200 if random.random() > 0.5 else self.width + 200
                 self.add_particle(DolphinParticle(spawn_x, y))  

        elif self.theme == "Emoji":
            try:
                # Expanded Emoji List (Prettiest ones, excludes basic numbers/letters)
                emojis = [
                    '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊', '😇',
                    '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷',
                    '🍏', '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🍈', '🍒', '🍑', '🍍',
                    '🚗', '🚕', '🚙', '🚌', '🚎', '🏎', '🚓', '🚑', '🚒', '🚐', '🚚', '🚛', '🚜',
                    '⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🥅', '🏒',
                    '🌈', '☀️', '⭐', '🌟', '🌙', '☁️', '❄️', '🔥', '🎈', '🎁', '🎂', '🎨', '🎺',
                    '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞',
                    '🌺', '🌻', '🌼', '🌷', '🦋', '🐝', '🐞', '🍄', '🌍', '🌎', '🌏', '🪐',
                    '🚀', '🛸', '🚁', '🚂', '🚢', '🚤', '⛵', '🛥️', '🛳️', '⛴️', '🚁', '🛩️',
                    '🍔', '🍟', '🍕', '🌭', '🥪', '🌮', '🌯', '🥗', '🍿', '🥫', '🍱', '🍘', '🍙'
                ]
                # Always pick a pretty emoji, ignoring the actual typed character
                char = random.choice(emojis)

                self.add_particle(EmojiParticle(x, y, char, self.emoji_renderer))
            except Exception as e:
                print(f"Error appending EmojiParticle: {e}")
        else: # Shapes
            if event.unicode and event.unicode.strip() and event.unicode.isalnum():
                self.add_particle(TextParticle(x, y, random_color(), event.unicode.upper(), self.font_manager))
            else:
                shape = random.choice(['oval', 'triangle', 'square', 'pentagon', 'star'])
                self.add_particle(ShapeParticle(x, y, random_color(), shape))

    def update(self, dt):
        # Handle repeats
        current_time = pygame.time.get_ticks()
        # Use list() to iterate over keys safely in case dictionary changes size (though unlikely here)
        for key in list(self.held_keys.keys()):
            data = self.held_keys[key]
            if current_time >= data['next_time']:
                self.spawn_object(data['event'])
                data['next_time'] = current_time + 100 # Repeat every 100ms

        # Filter alive
        self.particles = [p for p in self.particles if p.alive]
        
        # Limit objects to prevent lag (e.g., from fireworks)
        if len(self.particles) > self.max_objects:
            self.particles = self.particles[-self.max_objects:]

        for p in self.particles:
            p.update(dt)

    def draw(self):
        # Draw Background based on theme
        if self.theme == "Fireworks":
            if self.bg_surface_fireworks is not None:
                self.screen.blit(self.bg_surface_fireworks, (0,0))
        elif self.theme == "Sea":
            if self.bg_surface_sea is not None:
                self.screen.blit(self.bg_surface_sea, (0,0))
        else:
            # Shapes / Emoji -> Dark Grey
            self.screen.fill((40, 40, 45))
        
        # Draw particles
        for p in self.particles:
            p.draw(self.screen)
        
        # Foreground Elements (Fireworks only)
        if self.theme == "Fireworks":
            if self.fg_surface_fireworks is not None:
                self.screen.blit(self.fg_surface_fireworks, (0,0))

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
                f"[Up/Down] Max Objects (Shapes/Emoji): {self.max_objects}",
                f"[M] Monitor: {self.current_display_index + 1} / {self.num_displays}",
                f"[F] Display Mode: {self.display_mode.capitalize()}",
                f"[Left/Right] Volume: {int(self.volume * 100)}%",
                f"[S] Sound: {'On' if self.sound_enabled else 'Off'}",
                f"[A] Audio Style: {self.sound_style.capitalize()}",
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
        try:
            while self.running:
                dt = self.clock.tick(FPS) / 1000.0 # DT in seconds
                self.handle_input()
                self.update(dt)
                self.draw()
                
                # Ensure focus
                if platform.system() == "Windows" and not self.show_settings:
                     # Check if we lost focus? Pygame handles this mostly by grabbing input
                     pass
        finally:
            self.save_settings()
            pygame.quit()
            if KEYBOARD_AVAILABLE:
                try: keyboard.unhook_all()
                except Exception: pass
            sys.exit()

if __name__ == "__main__":
    game = SmashtopGame()
    game.run()
