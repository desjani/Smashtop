import pygame

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

