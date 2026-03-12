import pygame
import math
import random
from utils import random_color
from .base import Particle

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
        curr_size = self.size * self.scale
        if curr_size <= 1: return
        
        # Preserve aspect ratio
        w, h = self.image.get_size()
        if w == 0 or h == 0: return
        aspect = w / h
        
        # Determine dimensions based on max side to match target "size"
        if w > h:
            new_w = int(curr_size)
            new_h = int(curr_size / aspect)
        else:
            new_h = int(curr_size)
            new_w = int(curr_size * aspect)
            
        if new_w <= 0 or new_h <= 0: return

        scaled = pygame.transform.scale(self.image, (new_w, new_h))
        rect = scaled.get_rect(center=(self.x, self.y))
        surface.blit(scaled, rect)

