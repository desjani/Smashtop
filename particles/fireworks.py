import pygame
import math
import random
from utils import random_color
from .base import Particle

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
        # Play explosion sound
        self.game.play_firework_sound()
        
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

