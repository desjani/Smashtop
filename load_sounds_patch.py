import os
import random
import math
import array
import sys
import pygame

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class SoundGenerator:
    def __init__(self):
        self.sounds = {'notes': [], 'fireworks': [], 'bubbles': [], 'pops': []}
        self.style = "synth" # "synth" or "asset"
        try:
            pygame.mixer.set_num_channels(16)
            self.generate_synth_sounds()
        except Exception as e:
            print(f"Sound init failed: {e}")

    def generate_synth_sounds(self):
        self.synth_sounds = {'notes': [], 'fireworks': [], 'bubbles': [], 'pops': []}
        rate = 44100
        
        # 1. Notes (Shapes)
        notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
        duration = 0.2
        n_samples = int(rate * duration)
        for freq in notes:
            buf = array.array('h', [0] * n_samples)
            period_samples = int(rate / freq)
            for i in range(n_samples):
                if (i % period_samples) < (period_samples // 2):
                    value = 10000 
                else:
                    value = -10000
                decay = 1.0 - (i / n_samples)
                buf[i] = int(value * decay)
            self.synth_sounds['notes'].append(pygame.mixer.Sound(buffer=buf))

        # 2. Fireworks
        duration = 0.5
        for _ in range(5):
            n_samples = int(rate * duration)
            buf = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                value = random.randint(-15000, 15000)
                decay = math.exp(-6.0 * (i / n_samples))
                buf[i] = int(value * decay)
            self.synth_sounds['fireworks'].append(pygame.mixer.Sound(buffer=buf))

        # 3. Bubbles (Sea) - fast upward sine sweep
        duration = 0.15
        n_samples = int(rate * duration)
        for _ in range(4):
            buf = array.array('h', [0] * n_samples)
            base_freq = random.uniform(300, 500)
            for i in range(n_samples):
                t = i / rate
                # freq increases over time
                freq = base_freq + (2000 * (i/n_samples))
                value = int(15000 * math.sin(2 * math.pi * freq * t))
                # envelope
                decay = math.sin(math.pi * (i / n_samples)) # smooth fade in/out
                buf[i] = int(value * decay)
            self.synth_sounds['bubbles'].append(pygame.mixer.Sound(buffer=buf))

        # 4. Pops (Emoji) - fast downward sine sweep with sharp attack
        duration = 0.1
        n_samples = int(rate * duration)
        for _ in range(4):
            buf = array.array('h', [0] * n_samples)
            base_freq = random.uniform(800, 1200)
            for i in range(n_samples):
                t = i / rate
                freq = base_freq * math.exp(-15.0 * (i/n_samples))
                value = int(15000 * math.sin(2 * math.pi * freq * t))
                decay = math.exp(-10.0 * (i/n_samples))
                buf[i] = int(value * decay)
            self.synth_sounds['pops'].append(pygame.mixer.Sound(buffer=buf))

        self.apply_style()

    def set_style(self, style):
        self.style = style
        self.apply_style()

    def apply_style(self):
        self.sounds = {'notes': [], 'fireworks': [], 'bubbles': [], 'pops': []}
        
        if self.style == "asset":
            # Try loading from assets
            for category in self.sounds.keys():
                path = resource_path(f"assets/sounds/{category}")
                if os.path.exists(path):
                    for file in os.listdir(path):
                        if file.endswith('.wav') or file.endswith('.ogg'):
                            try:
                                s = pygame.mixer.Sound(os.path.join(path, file))
                                self.sounds[category].append(s)
                            except Exception: pass
            
        # Fallback to synth if assets missing or style is synth
        for cat in self.sounds.keys():
            if not self.sounds[cat]:
                self.sounds[cat] = self.synth_sounds.get(cat, [])

    def play(self, category, volume=0.5):
        try:
            pool = self.sounds.get(category, [])
            if pool:
                s = random.choice(pool)
                s.set_volume(volume)
                s.play()
        except Exception: pass
