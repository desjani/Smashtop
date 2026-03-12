import pygame
import random
import math

def create_gradient(top_col, bot_col, height):
    grad = pygame.Surface((1, height))
    for y in range(height):
        t = y / height
        r = int(top_col[0] * (1-t) + bot_col[0] * t)
        g = int(top_col[1] * (1-t) + bot_col[1] * t)
        b = int(top_col[2] * (1-t) + bot_col[2] * t)
        grad.set_at((0, y), (r, g, b))
    return grad

def generate_fireworks_bg(w, h):
    # Background
    grad_surf = create_gradient((2, 0, 10), (10, 10, 40), h)
    bg = pygame.transform.smoothscale(grad_surf, (w, h))

    # Stars
    for _ in range(300):
        sx = random.randint(0, w)
        sy = random.randint(0, int(h * 0.75))
        brightness = random.randint(100, 255)
        size = 1 if random.random() > 0.05 else 2
        pygame.draw.circle(bg, (brightness, brightness, brightness), (sx, sy), size)

    # Moon
    mx, my = int(w * 0.8), int(h * 0.2)
    for i in range(20, 0, -1):
        alpha = 5 + i * 2
        glow_s = pygame.Surface((i*6, i*6), pygame.SRCALPHA)
        pygame.draw.circle(glow_s, (200, 200, 255, 10), (i*3, i*3), i*3)
        bg.blit(glow_s, (mx - i*3, my - i*3))
    pygame.draw.circle(bg, (240, 240, 255), (mx, my), 30)
    pygame.draw.circle(bg, (200, 200, 220), (mx - 10, my+5), 6)
    pygame.draw.circle(bg, (210, 210, 230), (mx + 8, my-8), 4)

    # Foreground
    fg = pygame.Surface((w, h), pygame.SRCALPHA)
    
    # Hills
    poly_pts = [(0, h)]
    for i in range(0, w+1, 20):
        y_off = math.sin(i * 0.005) * 50 + math.sin(i * 0.02) * 20
        poly_pts.append((i, int(h - 100 - y_off)))
    poly_pts.append((w, h))
    pygame.draw.polygon(fg, (5, 15, 10), poly_pts)
    
    poly_pts_2 = [(0, h)]
    for i in range(0, w+1, 20):
        y_off = math.sin(i * 0.003 + 2) * 40 + math.sin(i * 0.05) * 10
        poly_pts_2.append((i, int(h - 50 - y_off)))
    poly_pts_2.append((w, h))
    pygame.draw.polygon(fg, (10, 25, 15), poly_pts_2)

    def draw_pine(surf, x, y, scale):
        col = (15, 30, 20)
        pygame.draw.rect(surf, (20, 15, 10), (x - 4*scale, y, 8*scale, 20*scale))
        tiers = 5
        for i in range(tiers):
            w_tier = (50 - i*8) * scale
            h_tier = 25 * scale
            y_tier = y - (i * 15 * scale) - 10*scale
            points = [(x - w_tier, y_tier + h_tier), (x, y_tier), (x + w_tier, y_tier + h_tier)]
            pygame.draw.polygon(surf, col, points)
            
    for i in range(8):
        scale = random.uniform(1.2, 1.8)
        draw_pine(fg, random.randint(20, 250), h - 40, scale)
        
    for i in range(8):
        scale = random.uniform(1.2, 1.8)
        draw_pine(fg, w - random.randint(20, 250), h - 40, scale)
        
    return bg, fg

def generate_sea_bg(w, h):
    top_sea = (50, 200, 230)
    mid_sea = (0, 100, 160)
    bot_sea = (0, 10, 40)
    
    grad1 = create_gradient(top_sea, mid_sea, int(h/2))
    grad2 = create_gradient(mid_sea, bot_sea, h - int(h/2))
    
    grad_full = pygame.Surface((1, h))
    grad_full.blit(grad1, (0,0))
    grad_full.blit(grad2, (0, int(h/2)))
    
    bg = pygame.transform.smoothscale(grad_full, (w, h))
    
    ray_surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for i in range(10):
        x_start = random.randint(0, w)
        width = random.randint(20, 100)
        angle = random.uniform(-0.2, 0.2)
        pts = [
            (x_start, 0),
            (x_start + width, 0),
            (x_start + width + math.sin(angle)*h, h),
            (x_start + math.sin(angle)*h, h)
        ]
        pygame.draw.polygon(ray_surf, (200, 255, 255, 15), pts)
    bg.blit(ray_surf, (0,0))

    sand_h = 100
    sand_col = (210, 195, 140)
    
    pygame.draw.rect(bg, sand_col, (0, h-sand_h, w, sand_h))
    poly_sand = [(0, h)]
    for i in range(0, w+1, 10):
        dy = math.sin(i * 0.01) * 20 + math.sin(i*0.05) * 5
        poly_sand.append((i, int(h - sand_h - dy)))
    poly_sand.append((w, h))
    pygame.draw.polygon(bg, sand_col, poly_sand)
    
    for i in range(3000):
        sx = random.randint(0, w)
        sy = random.randint(h - sand_h - 20, h)
        if sy > int(h - sand_h + math.sin(sx * 0.01) * 20): 
            shade = random.randint(-20, 20)
            r = max(0, min(255, sand_col[0] + shade))
            g = max(0, min(255, sand_col[1] + shade))
            b = max(0, min(255, sand_col[2] + shade))
            bg.set_at((sx, sy), (r,g,b))
            
    def draw_seaweed(surf, x, y, tallness):
        pts = []
        segments = 10
        sway = random.uniform(0, 100)
        for i in range(segments):
            seg_y = y - (i * tallness / segments)
            seg_x = x + math.sin(sway + i * 0.5) * 10
            pts.append((seg_x, seg_y))
        pygame.draw.lines(surf, (40, 140, 60), False, pts, 4)

    for i in range(15):
        x = random.randint(0, w)
        floor_y = h - sand_h + math.sin(x * 0.01) * 20 - 20
        if floor_y < h:
            draw_seaweed(bg, x, h, random.randint(50, 150))
            
    for i in range(8):
        cx = random.randint(50, w-50)
        cy = h - sand_h + math.sin(cx * 0.01) * 20 + 20
        for j in range(5):
            r = random.randint(10, 30)
            off_x = random.randint(-20, 20)
            off_y = random.randint(-10, 10)
            col = random.choice([(180, 100, 100), (100, 100, 120), (160, 80, 140)])
            pygame.draw.circle(bg, col, (cx+off_x, int(cy+off_y)), r)
            
    return bg
