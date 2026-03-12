import random
from utils import random_color
from particles import (Particle, ShapeParticle, TextParticle, EmojiParticle, 
                       FireworkParticle, BubbleParticle, FishParticle, JellyfishParticle, 
                       SharkParticle, WhaleParticle, DolphinParticle)

def spawn_object(game, event):
    # Play generic sound unless it's Fireworks mode (handled on explosion)
    if game.theme != "Fireworks":
        game.play_sound()
        
    x = random.randint(100, game.width - 100)
    y = random.randint(100, game.height - 100)
    
    # Limit objects (Only for persistent modes like Shapes and Emoji)
    if game.theme in ["Shapes", "Emoji"]:
        # Count only particles that are not already fading out
        active_particles = [p for p in game.particles if p.state != "out"]
        if len(active_particles) >= game.max_objects:
             # Kill the oldest active particle
             if active_particles:
                 active_particles[0].kill()

    if game.theme == "Fireworks":
        game.add_particle(FireworkParticle(x, y, game))
    elif game.theme == "Sea":
         choices = [
             ('baby',   50),
             ('fish',   30),
             ('jelly',  7),
             ('shark',  7),
             ('whale',  1),
             ('dolphin', 5)
         ]
         
         keys = [c[0] for c in choices]
         weights = [c[1] for c in choices]
         choice = random.choices(keys, weights=weights, k=1)[0]

         if choice == 'baby':
             game.add_particle(BubbleParticle(x, game.height + 50))
         elif choice == 'fish':
             spawn_x = -50 if random.random() > 0.5 else game.width + 50
             game.add_particle(FishParticle(spawn_x, y, random_color()))
         elif choice == 'jelly':
             game.add_particle(JellyfishParticle(x, game.height + 50, random_color()))
         elif choice == 'shark':
             spawn_x = -200 if random.random() > 0.5 else game.width + 200
             game.add_particle(SharkParticle(spawn_x, y))
         elif choice == 'whale':
             spawn_x = -300 if random.random() > 0.5 else game.width + 300
             game.add_particle(WhaleParticle(spawn_x, y)) 
         elif choice == 'dolphin':
             spawn_x = -200 if random.random() > 0.5 else game.width + 200
             game.add_particle(DolphinParticle(spawn_x, y))  

    elif game.theme == "Emoji":
        try:
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
            char = random.choice(emojis)
            game.add_particle(EmojiParticle(x, y, char, game.emoji_renderer))
        except Exception as e:
            print(f"Error appending EmojiParticle: {e}")
    else: # Shapes
        if event.unicode and event.unicode.strip() and event.unicode.isalnum():
            game.add_particle(TextParticle(x, y, random_color(), event.unicode.upper(), game.font_manager))
        else:
            shape = random.choice(['oval', 'triangle', 'square', 'pentagon', 'star'])
            game.add_particle(ShapeParticle(x, y, random_color(), shape))
