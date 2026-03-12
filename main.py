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
        from backgrounds import generate_fireworks_bg, generate_sea_bg
        self.bg_surface_fireworks, self.fg_surface_fireworks = generate_fireworks_bg(self.width, self.height)
        self.bg_surface_sea = generate_sea_bg(self.width, self.height)




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
        from spawner import spawn_object as _spawn_object
        _spawn_object(self, event)

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
