        elif self.theme == "Space":
            try:
                emojis = ['🚀', '🛸', '🪐', '🌍', '🌙', '⭐', '☄️', '🛰️', '👽', '👨‍🚀']
                char = random.choice(emojis)
                self.add_particle(SpaceParticle(x, y, char, self.emoji_renderer))
            except Exception as e:
                print(f"Error appending SpaceParticle: {e}")
        elif self.theme == "Animals":
            try:
                emojis = ['🐶', '🐱', '🐭', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷', '🐸', '🐵', '🐔', '🦄', '🐣', '🐍', '🐙']
                char = random.choice(emojis)
                self.add_particle(AnimalParticle(x, y, char, self.emoji_renderer, self.height))
            except Exception as e:
                print(f"Error appending AnimalParticle: {e}")
        elif self.theme == "Piano":
            try:
                emojis = ['🎵', '🎶', '🎹', '🎼', '🎸', '🎺', '🎻', '🥁']
                char = random.choice(emojis)
                self.add_particle(EmojiParticle(x, y, char, self.emoji_renderer))
            except Exception as e:
                print(f"Error appending PianoParticle: {e}")
