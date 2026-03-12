import pygame
import math
import random
from utils import random_color
from .base import Particle

class BubbleParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, (200, 200, 255))
        # Increased speed by ~25% (was -100 to -250)
        self.vy = random.uniform(-125, -315)
        self.wobble_phase = random.uniform(0, 100)
        self.size = random.randint(10, 80) # More varied size (was 20-60)
        
    def update(self, dt):
        super().update(dt)
        self.y += self.vy * dt
        self.wobble_phase += 5 * dt
        # Increased horizontal sway amplitude to 150 (was 100) for more motion
        self.x += math.sin(self.wobble_phase) * 150 * dt
        
        if self.y < -50: self.alive = False

    def draw(self, surface):
        s = int(self.size * self.scale)
        if s > 2:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(s/2), 2)
            # Shine
            pygame.draw.circle(surface, (255,255,255), (int(self.x - s/6), int(self.y - s/6)), int(s/8))

class FishParticle(Particle):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.vx = random.choice([-200, -150, 150, 200])
        self.direction = 1 if self.vx > 0 else -1
        self.size = random.randint(40, 140)
        self.anim_offset = random.uniform(0, 100)
        
        # Make a darker shade for details
        r, g, b = self.color
        self.dark_color = (max(0, r-50), max(0, g-50), max(0, b-50))
        self.light_color = (min(255, r+50), min(255, g+50), min(255, b+50))

    def update(self, dt):
        super().update(dt)
        self.x += self.vx * dt
        self.anim_offset += dt * 10
        screen_w = pygame.display.get_surface().get_width()
        if (self.vx > 0 and self.x > screen_w + 100) or (self.vx < 0 and self.x < -100):
            self.alive = False

    def draw(self, surface):
        s = self.size * self.scale
        d = self.direction
        x, y = self.x, self.y
        
        # Tail wag calculation
        wag = math.sin(self.anim_offset) * 10 * s / 100.0
        
        # Tail (Triangle that wags)
        tail_center_x = x - 35*d*self.scale
        tail_pts = [
            (tail_center_x, y),
            (tail_center_x - 20*d*self.scale, y - (25*self.scale) + wag),
            (tail_center_x - 20*d*self.scale, y + (25*self.scale) + wag)
        ]
        pygame.draw.polygon(surface, self.dark_color, tail_pts)
        
        # Fins (Dorsal and Pectoral)
        # Dorsal
        pygame.draw.polygon(surface, self.dark_color, [
            (x - 10*d*self.scale, y - 15*self.scale),
            (x + 10*d*self.scale, y - 15*self.scale),
            (x - 5*d*self.scale, y - 35*self.scale)
        ])
        
        # Body (Ellipse)
        # Pygame ellipse is axis aligned, so we can't rotate it easily without a surface
        # But a circle/oval works fine for a simple fish. 
        body_rect = pygame.Rect(0, 0, 70*self.scale, 50*self.scale)
        body_rect.center = (int(x), int(y))
        pygame.draw.ellipse(surface, self.color, body_rect)
        
        # Eye (White sclera, Black pupil)
        eye_x = x + 15*d*self.scale
        eye_y = y - 10*self.scale
        pygame.draw.circle(surface, (255,255,255), (int(eye_x), int(eye_y)), int(6*self.scale))
        pygame.draw.circle(surface, (0,0,0), (int(eye_x + 1*d*self.scale), int(eye_y)), int(2*self.scale))
        
        # Side Fin (Wagging slightly)
        fin_wag = math.cos(self.anim_offset) * 5 * s / 100.0
        pygame.draw.polygon(surface, self.light_color, [
             (x - 5*d*self.scale, y + 5*self.scale),
             (x + 5*d*self.scale, y + 5*self.scale),
             (x - 5*d*self.scale, y + 20*self.scale + fin_wag)
        ])

class JellyfishParticle(Particle):
    def __init__(self, x, y, color):
        super().__init__(x, y, color)
        self.vy = random.uniform(-60, -120)
        self.size = random.randint(50, 200)
        self.pulse_phase = random.uniform(0, 10)
        
        # Semi-transparent colors using alpha (requires new surface)
        r, g, b = color
        self.head_color = (r, g, b)
        self.tentacle_color = (max(0, r-30), max(0, g-30), max(0, b-30))

    def update(self, dt):
        super().update(dt)
        self.y += self.vy * dt
        self.pulse_phase += 5 * dt
        if self.y < -150: self.alive = False

    def draw(self, surface):
        s = self.size * self.scale
        pulse = 1.0 + 0.1 * math.sin(self.pulse_phase)
        w = int(s * pulse)
        h = int(s * 0.8 * pulse)
        
        # Draw Tentacles (Sine waves)
        curr_y = self.y + h/4
        for i in range(5): # 5 tentacles
            off_x = (i - 2) * (w/5)
            pts = []
            for j in range(10): # segments
                seg_y = curr_y + (j * s/5)
                # Wiggle
                wiggle = math.sin(self.pulse_phase + (j*0.5) + i) * (10 * self.scale)
                pts.append((self.x + off_x + wiggle, seg_y))
            
            if len(pts) > 1:
                pygame.draw.lines(surface, self.tentacle_color, False, pts, max(1, int(3*self.scale)))

        # Draw Head (Half Ellipse / Arc)
        rect = pygame.Rect(self.x - w/2, self.y - h/2, w, h)
        pygame.draw.arc(surface, self.head_color, rect, 0, math.pi, max(2, int(6*self.scale)))
        # Fill the top (dome) roughly
        # We can simulate fill by drawing smaller arcs or using polygon for top half
        # Or just a circle clipped? 
        # Polygon is easiest for "filled chord"
        chord_pts = [
             (self.x - w/2, self.y),
             (self.x - w/2*0.7, self.y - h*0.4),
             (self.x, self.y - h/2),
             (self.x + w/2*0.7, self.y - h*0.4),
             (self.x + w/2, self.y)
        ]
        pygame.draw.polygon(surface, self.head_color, chord_pts)
        
        # Details (spots on head)
        pygame.draw.circle(surface, (255,255,255), (int(self.x - w/4), int(self.y - h/4)), int(3*self.scale))
        pygame.draw.circle(surface, (255,255,255), (int(self.x + w/4), int(self.y - h/3)), int(2*self.scale))

class SharkParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, (120, 130, 140)) # Slate Gray
        self.vx = random.choice([-300, -250, 250, 300])
        self.direction = 1 if self.vx > 0 else -1
        self.size = random.randint(150, 250)
        self.anim_offset = 0

    def update(self, dt):
        super().update(dt)
        self.x += self.vx * dt
        self.anim_offset += dt * 8
        screen_w = pygame.display.get_surface().get_width()
        if (self.vx > 0 and self.x > screen_w + 200) or (self.vx < 0 and self.x < -200):
            self.alive = False

    def draw(self, surface):
        x, y = self.x, self.y
        d = self.direction
        s = self.scale
        
        # Animated Tail part
        tail_wag = math.sin(self.anim_offset) * 15 * s
        
        # Shark Body (Two parts: rigid front, moving tail)
        # Front Body
        front_pts = [
             (x + 100*d*s, y),       # Nose
             (x + 20*d*s, y - 35*s), # Top Head
             (x - 50*d*s, y - 35*s), # Back
             (x - 50*d*s, y + 35*s), # Belly (thick)
             (x + 40*d*s, y + 25*s)  # Throat
        ]
        pygame.draw.polygon(surface, self.color, front_pts)
        
        # Dorsal Fin
        pygame.draw.polygon(surface, (100,110,120), [
            (x - 20*d*s, y - 35*s),
            (x - 50*d*s, y - 90*s), # High Tip
            (x - 60*d*s, y - 35*s)
        ])
        
        # Rear Body + Tail (connected to back of front body roughly at x-50)
        rear_x = x - 50*d*s
        tail_tip_x = rear_x - 80*d*s
        tail_tip_y = y + tail_wag
        
        rear_pts = [
            (rear_x, y - 35*s),
            (tail_tip_x, tail_tip_y - 10*s), # Tail base top
            (tail_tip_x - 40*d*s, tail_tip_y - 50*s), # Fin Top
            (tail_tip_x - 20*d*s, tail_tip_y), # Fin Notch
            (tail_tip_x - 40*d*s, tail_tip_y + 40*s), # Fin Bot
            (tail_tip_x, tail_tip_y + 10*s), # Tail base bot
            (rear_x, y + 35*s) 
        ]
        pygame.draw.polygon(surface, self.color, rear_pts)
        
        # Belly Color (Lighter patch on bottom)
        pygame.draw.polygon(surface, (180,190,200), [
            (x + 40*d*s, y+24*s),
            (x - 50*d*s, y+34*s),
            (x - 40*d*s, y+5*s)
        ])
        
        # Gill Slits
        for i in range(3):
            gx = x - (i*10 + 10)*d*s
            pygame.draw.line(surface, (50,50,60), (gx, y-10*s), (gx, y+10*s), max(1, int(2*s)))

        # Eye
        pygame.draw.circle(surface, (255,255,255), (int(x + 60*d*s), int(y - 10*s)), int(5*s))
        pygame.draw.circle(surface, (0,0,0), (int(x + 62*d*s), int(y - 10*s)), int(2*s))

class WhaleParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, (60, 70, 110)) # Dark Blue-ish
        self.vx = random.choice([-125, -100, 100, 125]) # Increased speed by 25% (was 80, 100)
        self.direction = 1 if self.vx > 0 else -1
        self.size = random.randint(250, 400)
        self.anim_offset = 0
        self.spout_particles = [] # [(x, y, life)]

    def update(self, dt):
        super().update(dt)
        self.x += self.vx * dt
        self.anim_offset += dt * 3 # Slow wag
        
        # Spout logic: Random bursts
        if random.random() < 0.05: # 5% chance per frame
            num_drops = random.randint(3, 8)
            for _ in range(num_drops):
                self.spout_particles.append({
                    'x': 0, # Relative to spout hole
                    'y': 0,
                    'vx': random.uniform(-30, 30),
                    'vy': random.uniform(-100, -200),
                    'life': 1.0 
                })
        
        # Update spout particles
        for p in self.spout_particles:
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] += 300 * dt # Gravity
            p['life'] -= dt
        
        self.spout_particles = [p for p in self.spout_particles if p['life'] > 0]
        
        screen_w = pygame.display.get_surface().get_width()
        if (self.vx > 0 and self.x > screen_w + 300) or (self.vx < 0 and self.x < -300):
            self.alive = False

    def draw(self, surface):
        x, y = self.x, self.y
        d = self.direction
        s = self.scale
        
        tail_wag = math.sin(self.anim_offset) * 10 * s
        
        # Whale Shape (Bulbous Head, Tapered Tail)
        
        # Construct custom polygon for cleaner shape
        pts = [
            (x + 120*d*s, y + 20*s),   # Nose/Jaw
            (x + 100*d*s, y - 30*s),   # Upper Jaw
            (x + 40*d*s, y - 70*s),    # Forehead (Blowhole area)
            (x - 80*d*s, y - 60*s),    # Back
            (x - 140*d*s, y - 10*s),   # Tail Base Top
            
            # Tail Fin (Wags)
            (x - 190*d*s, y - 40*s + tail_wag),   # Tail Tip Top
            (x - 180*d*s, y + tail_wag),          # Tail Notch
            (x - 190*d*s, y + 40*s + tail_wag),   # Tail Tip Bot
            
            (x - 140*d*s, y + 30*s),   # Tail Base Bot
            (x + 20*d*s, y + 70*s),    # Belly
        ]
        
        # Draw Body
        pygame.draw.polygon(surface, self.color, pts)
        
        # Belly Lines (Grooves)
        for i in range(4):
            off_y = i * 10 * s
            start = (x + 20*d*s, y + 30*s + off_y)
            end = (x - 60*d*s, y + 30*s + off_y*0.8)
            pygame.draw.line(surface, (40,50,90), start, end, max(1, int(2*s)))

        # Eye
        pygame.draw.circle(surface, (255,255,255), (int(x + 70*d*s), int(y - 0*s)), int(4*s))
        pygame.draw.circle(surface, (0,0,0), (int(x + 72*d*s), int(y - 0*s)), int(2*s))
        
        # Draw Side Fin
        fin_drag = math.sin(self.anim_offset) * 5 * s
        fin_pts = [
            (x - 20*d*s, y + 20*s),
            (x + 10*d*s, y + 20*s),
            (x - 30*d*s, y + 60*s + fin_drag)
        ]
        pygame.draw.polygon(surface, (50,60,100), fin_pts)

        # Draw Water Spout
        spout_origin_x = x + 40*d*s
        spout_origin_y = y - 70*s
        for p in self.spout_particles:
            px = spout_origin_x + p['x']*s
            py = spout_origin_y + p['y']*s
            alpha_col = int(p['life']*255)
            if alpha_col > 0:
                 rad = max(1, int(4 * p['life'] * s))
                 pygame.draw.circle(surface, (200, 240, 255), (int(px), int(py)), rad)

class DolphinParticle(Particle):
    def __init__(self, x, y):
        super().__init__(x, y, (140, 160, 220)) # Lighter Blue/Gray
        self.vx = random.choice([-200, -180, 180, 200])
        self.direction = 1 if self.vx > 0 else -1
        self.size = random.randint(120, 180)
        self.y_start = y
        self.time = 0

    def update(self, dt):
        super().update(dt)
        self.time += dt
        self.x += self.vx * dt
        # Swim motion: stronger leaps
        self.y = self.y_start + math.sin(self.time * 4) * 60
        
        screen_w = pygame.display.get_surface().get_width()
        if (self.vx > 0 and self.x > screen_w + 200) or (self.vx < 0 and self.x < -200):
            self.alive = False

    def draw(self, surface):
        x, y = self.x, self.y
        d = self.direction
        s = self.scale
        
        # Body rotation based on swim angle (derivative of sine wave)
        # y = A sin(wt) -> y' = Aw cos(wt)
        # angle ~ atan(y')
        angle = math.atan2(math.cos(self.time * 4) * 60, 40) # rough approx factor
        
        # When moving left (d=-1), we flip the X coordinates via 'd'.
        # If dolphin is pitching UP (angle > 0) and moving Right -> Nose points Right-Up.
        # If dolphin is pitching UP and moving Left -> Nose should point Left-Up.
        # Drawing logic rotates model (Nose Right), then scales x by d.
        # Rot(Up) -> Nose Right-Up.
        # Flip X -> Nose Left-Up. 
        # So we use the same pitch angle regardless of direction.
        pitch = angle
        
        cos_a = math.cos(pitch)
        sin_a = math.sin(pitch)
        
        def rot(px, py):
            # Rotate (px, py) around (0,0) by pitch
            return (px * cos_a - py * sin_a, px * sin_a + py * cos_a)

        # Base Shape Points (Model Space)
        raw_pts = [
            (60, 0),       # Beak tip
            (30, -15),     # Melon (forehead)
            (0, -20),      # Top head
            (-15, -35),    # Dorsal fin top
            (-30, -20),    # Dorsal fin base back
            (-80, -5),     # Tail base
            (-110, -20),   # Tail fin top
            (-100, 0),     # Tail notch
            (-110, 20),    # Tail fin bot
            (-80, 5),      # Tail base bot
            (0, 15),       # Belly
            (30, 5),       # Throat
        ]
        
        final_pts = []
        for (rx, ry) in raw_pts:
            # Scale
            sx = rx * s
            sy = ry * s
            # Rotate
            rx_rot, ry_rot = rot(sx, sy)
            # Translate & Flip
            final_pts.append((x + rx_rot * d, y + ry_rot))

        pygame.draw.polygon(surface, self.color, final_pts)
        
        # Eye (manual placement logic similar to points)
        ex, ey = 35*s, -5*s
        erx, ery = rot(ex, ey)
        eye_pos = (int(x + erx * d), int(y + ery))
        pygame.draw.circle(surface, (255,255,255), eye_pos, int(3*s))
        pygame.draw.circle(surface, (0,0,0), eye_pos, int(1*s))
        
        # Side Fin
        fx, fy = 0, 10*s
        frx, fry = rot(fx, fy)
        fin_pos = (x + frx*d, y + fry)
        
        # Simple fin line/tri
        fin_tip_x, fin_tip_y = -15*s, 30*s
        ftrx, ftry = rot(fin_tip_x, fin_tip_y)
        
        pygame.draw.line(surface, (100, 120, 180), fin_pos, (x + ftrx*d, y + ftry), max(2, int(4*s)))



