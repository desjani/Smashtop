        # 5. Space - smooth sine twinkle
        duration = 0.4
        n_samples = int(rate * duration)
        for _ in range(4):
            buf = array.array('h', [0] * n_samples)
            base_freq = random.uniform(800, 1500)
            for i in range(n_samples):
                t = i / rate
                # soft vibrato
                freq = base_freq + 20 * math.sin(2 * math.pi * 5 * t)
                value = int(12000 * math.sin(2 * math.pi * freq * t))
                decay = math.exp(-3.0 * (i/n_samples))
                buf[i] = int(value * decay)
            self.synth_sounds['space'].append(pygame.mixer.Sound(buffer=buf))

        # 6. Animals - quirky short square bounce
        duration = 0.15
        n_samples = int(rate * duration)
        for _ in range(4):
            buf = array.array('h', [0] * n_samples)
            base_freq = random.uniform(150, 400)
            for i in range(n_samples):
                t = i / rate
                freq = base_freq * (1.0 + 0.5 * math.sin(2 * math.pi * 15 * t))
                period = int(rate / freq) if freq > 0 else 1
                value = 10000 if (i % period) < (period // 2) else -10000
                decay = 1.0 - (i / n_samples)
                buf[i] = int(value * decay)
            self.synth_sounds['animals'].append(pygame.mixer.Sound(buffer=buf))

        # 7. Piano - pentatonic sine bells
        piano_notes = [261.63, 293.66, 329.63, 392.00, 440.00, 523.25, 587.33, 659.25, 783.99, 880.00]
        duration = 0.8
        n_samples = int(rate * duration)
        for freq in piano_notes:
            buf = array.array('h', [0] * n_samples)
            for i in range(n_samples):
                t = i / rate
                value = int(15000 * math.sin(2 * math.pi * freq * t))
                decay = math.exp(-4.0 * (i/n_samples))
                buf[i] = int(value * decay)
            self.synth_sounds['piano'].append(pygame.mixer.Sound(buffer=buf))
