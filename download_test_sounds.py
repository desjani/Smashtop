import wave
import math
import struct
import os

def create_sine_wave(filepath, freq_func, duration, sample_rate=44100):
    n_samples = int(duration * sample_rate)
    with wave.open(filepath, 'w') as f:
        f.setnchannels(1) # mono
        f.setsampwidth(2) # 2 bytes per sample (16 bit)
        f.setframerate(sample_rate)
        
        for i in range(n_samples):
            t = i / sample_rate
            freq = freq_func(i, n_samples)
            value = int(15000 * math.sin(2 * math.pi * freq * t))
            # envelope
            decay = 1.0 - (i / n_samples)
            value = int(value * decay)
            data = struct.pack('<h', value)
            f.writeframesraw(data)

os.makedirs('assets/sounds/pops', exist_ok=True)
os.makedirs('assets/sounds/bubbles', exist_ok=True)
os.makedirs('assets/sounds/notes', exist_ok=True)
os.makedirs('assets/sounds/fireworks', exist_ok=True)

# Generate a pop
create_sine_wave('assets/sounds/pops/pop1.wav', lambda i, n: 800 * math.exp(-10.0 * (i/n)), 0.1)
# Generate a bubble
create_sine_wave('assets/sounds/bubbles/bubble1.wav', lambda i, n: 300 + (1500 * (i/n)), 0.15)
# Note
create_sine_wave('assets/sounds/notes/note1.wav', lambda i, n: 440, 0.2)
# Since we can't easily emulate noise in `create_sine_wave` without random, we'll skip fireworks 
# or just use a low freq sub-bass
create_sine_wave('assets/sounds/fireworks/boom1.wav', lambda i, n: 100 * math.exp(-2.0 * (i/n)), 0.5)

print("Generated dummy asset files!")
