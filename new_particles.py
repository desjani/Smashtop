
class SpaceParticle(EmojiParticle):
    def __init__(self, x, y, char, emoji_renderer):
        super().__init__(x, y, char, emoji_renderer)
        # Slow zero-G drift floating mechanics
        self.vx = random.uniform(-100, 100)
        self.vy = random.uniform(-100, 100)
        self.rot_speed = random.uniform(-20, 20)
        self.rotation = 0
        self.state = "drift"
        self.lifetime = 255
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.rotation += self.rot_speed * dt
        self.lifetime -= 25 * dt # Very slow fade out
        if self.lifetime <= 0:
            self.alive = False
            
    def draw(self, surface):
        if self.lifetime <= 0: return
        try:
            s_img = pygame.transform.scale(self.image, (int(self.size), int(self.size)))
            rotated = pygame.transform.rotate(s_img, self.rotation)
            rotated.set_alpha(int(max(0, self.lifetime)))
            rect = rotated.get_rect(center=(self.x, self.y))
            surface.blit(rotated, rect)
        except Exception: pass

class AnimalParticle(EmojiParticle):
    def __init__(self, x, y, char, emoji_renderer, floor_y):
        super().__init__(x, y, char, emoji_renderer)
        self.vy = random.uniform(-400, -100) # jump up
        self.vx = random.uniform(-200, 200)
        self.gravity = 800
        self.floor_y = floor_y
        self.lifetime = 255
        self.bounces = 0
        self.target_scale = 1.0
        self.state = "bounce"
        
    def update(self, dt):
        self.vy += self.gravity * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Floor collision
        if self.y + (self.size / 2) >= self.floor_y:
            self.y = self.floor_y - (self.size / 2)
            self.vy = -self.vy * 0.5 # dampening
            self.bounces += 1
            
        if self.bounces >= 3:
            self.lifetime -= 150 * dt
            if self.lifetime <= 0:
                self.alive = False

    def draw(self, surface):
        if self.lifetime <= 0: return
        try:
            scaled = pygame.transform.scale(self.image, (int(self.size), int(self.size)))
            if self.bounces >= 3:
                scaled.set_alpha(int(max(0, self.lifetime)))
            rect = scaled.get_rect(center=(self.x, self.y))
            surface.blit(scaled, rect)
        except Exception: pass
