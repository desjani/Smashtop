import tkinter as tk
import keyboard
import random
import sys
import winsound
import threading
import math
from PIL import Image, ImageDraw, ImageTk

class AnimatedObject:
    def __init__(self, canvas, x, y, color, shape_type, char=None, paint_draw=None):
        self.canvas = canvas
        self.color = color
        self.shape_type = shape_type
        self.char = char
        self.paint_draw = paint_draw # PIL ImageDraw object for paint mode
        
        # Default positioning target
        self.x = x
        self.y = y
        
        # Standard Animation properties
        self.angle = random.uniform(0, 360)
        self.spin_speed = random.choice([-10, -5, 5, 10])
        self.scale = 0.0
        self.base_size = random.randint(62, 250)
        self.state = "in" # 'in', 'active', 'out'

        # Polygon properties
        self.points_count = 0
        if self.shape_type == 'triangle': self.points_count = 3
        elif self.shape_type == 'square': self.points_count = 4
        elif self.shape_type == 'pentagon': self.points_count = 5
        elif self.shape_type == 'hexagon': self.points_count = 6
        elif self.shape_type == 'star': self.points_count = 5
        elif self.shape_type == 'paint': 
            self.paint_style = random.choice(['splat', 'splat', 'line', 'spray'])
            if self.paint_style == 'splat':
                self.points_count = random.randint(10, 16)
                self.splat_radii = [random.uniform(0.2, 1.0) for _ in range(self.points_count)]
            self.spin_speed = 0 
            self.scale = 1.0 # Paint spawns full size immediately? If we want pollock vibe, instant is better.
            self.state = "active"

        # Firework specific state
        if self.shape_type == 'firework':
            self.state = 'launch'
            self.target_y = y # Detonation height
            self.launch_x = x
            self.y = self.canvas.winfo_height() # Start at bottom
            self.vy = random.uniform(-18, -27) # Launch speed (Increased 50%)
            self.particles = []

        # Sea specific state
        if self.shape_type in ['bubble', 'fish', 'jellyfish']:
            self.vx = 0
            self.vy = 0
            if self.shape_type == 'bubble':
                self.vy = random.uniform(-2, -5)
                self.vx_wobble = random.uniform(0, 100)
            elif self.shape_type == 'fish':
                self.vx = random.choice([-5, -4, 4, 5])
                self.scale_x = 1 if self.vx > 0 else -1 # Facing
            elif self.shape_type == 'jellyfish':
                self.vy = random.uniform(-1, -3)
                self.pulse_phase = random.uniform(0, 6)

        # Weather specific state
        if self.shape_type in ['raindrop', 'snowflake', 'cloud', 'sun']:
            if self.shape_type == 'raindrop':
                self.vy = random.uniform(10, 20)
            elif self.shape_type == 'snowflake':
                self.vy = random.uniform(2, 5)
                self.vx_wobble = random.uniform(0, 100)
                self.points_count = 6
            elif self.shape_type in ['cloud', 'sun']:
                self.vx = random.uniform(0.5, 2) * random.choice([1, -1])

        self.item_id = self._create_item()

    def _create_item(self):
        if self.shape_type == 'firework':
            # Rocket head
            return self.canvas.create_oval(self.x-3, self.y-5, self.x+3, self.y+5, fill=self.color, outline=self.color)
        elif self.shape_type == 'text':
             return self.canvas.create_text(self.x, self.y, text=self.char, fill=self.color, font=("Arial", 1, "bold"))
        elif self.shape_type == 'emoji':
            return self.canvas.create_text(self.x, self.y, text=self.char, fill=self.color, font=("Arial", 20))
        elif self.shape_type == 'oval':
            return self.canvas.create_oval(self.x, self.y, self.x, self.y, outline=self.color, width=5)
        elif self.shape_type == 'paint':
             if self.paint_style == 'splat':
                item_id = self.canvas.create_polygon(0,0,0,0,0,0, fill=self.color, outline='', smooth=True)
                
                # Immediate Bake: If we have a PIL draw surface, calculate the FINAL geometry now and draw it.
                # Since splats don't move or animate much (just appear), we can draw the final state.
                if self.paint_draw:
                     # Calculate points (Duplicated logic from update(), but simplified for static stamp)
                     points = []
                     r = self.base_size / 2 # use full size
                     angle_step = 360 / self.points_count
                     for i in range(self.points_count):
                         radius_mod = self.splat_radii[i]
                         theta = math.radians(i * angle_step)
                         px = self.x + (r * radius_mod) * math.cos(theta)
                         py = self.y + (r * radius_mod) * math.sin(theta)
                         points.append((px, py))
                     self.paint_draw.polygon(points, fill=self.color)
                
                return item_id
             elif self.paint_style == 'line':
                 # Create a line with slightly random end point
                 dx = random.randint(-400, 400)
                 dy = random.randint(-400, 400)
                 item_id = self.canvas.create_line(self.x, self.y, self.x+dx, self.y+dy, fill=self.color, width=random.randint(5, 15), capstyle='round', smooth=True)
                 
                 if self.paint_draw:
                     self.paint_draw.line([(self.x, self.y), (self.x+dx, self.y+dy)], fill=self.color, width=10, joint='curve')
                 
                 return item_id
             elif self.paint_style == 'spray':
                 self.spray_dots = []
                 for _ in range(random.randint(20, 50)):
                     ox = random.randint(-80, 80)
                     oy = random.randint(-80, 80)
                     s = random.randint(2, 6)
                     d = self.canvas.create_oval(self.x+ox, self.y+oy, self.x+ox+s, self.y+oy+s, fill=self.color, outline='')
                     self.spray_dots.append(d)
                     
                     if self.paint_draw:
                         self.paint_draw.ellipse([self.x+ox, self.y+oy, self.x+ox+s, self.y+oy+s], fill=self.color)
                         
                 return self.spray_dots

        # Sea Creatures
        elif self.shape_type == 'bubble':
             return self.canvas.create_oval(self.x, self.y, self.x, self.y, outline='white', width=2)
        elif self.shape_type == 'fish':
             return self.canvas.create_polygon(0,0,0,0,0,0, fill=self.color, outline='white', width=2)
        elif self.shape_type == 'jellyfish':
             self.tentacles = []
             for i in range(5):
                 # Wavy lines below
                 t = self.canvas.create_line(self.x, self.y, self.x, self.y+40, fill='white', width=1, smooth=True)
                 self.tentacles.append({'id':t, 'offset': i*10, 'phase': random.uniform(0, 10)})
             self.bell = self.canvas.create_polygon(0,0,0,0,0,0, fill=self.color, outline='white', width=2, smooth=True)
             return self.bell
        
        # Weather
        elif self.shape_type == 'raindrop':
             return self.canvas.create_line(self.x, self.y, self.x, self.y+20, fill='cyan', width=3)
        elif self.shape_type == 'snowflake':
             # Simple cross/star
             return self.canvas.create_text(self.x, self.y, text='❄', fill='white', font=("Arial", int(self.base_size/2)))
        elif self.shape_type == 'sun':
             return self.canvas.create_oval(self.x, self.y, self.x, self.y, fill='yellow', outline='orange', width=3)
        elif self.shape_type == 'cloud':
             return self.canvas.create_oval(self.x, self.y, self.x, self.y, fill='white', outline='gray', width=0)
        else: # Regular polygon (triangle, square, pentagon, etc...)
            return self.canvas.create_polygon(0,0,0,0,0,0, outline=self.color, width=5, fill='')

    def fade_out(self):
        if self.shape_type == 'firework':
            self.state = 'out' # Force expire
        elif self.shape_type in ['bubble', 'fish', 'jellyfish']:
            # They don't fade out on command usually, they leave screen?
            # But if max objects reached, we need to remove them.
            self.state = 'out'
        elif self.state != "out":
            self.state = "out"

    def update(self):
        if self.shape_type == 'firework':
            return self.update_firework()
        
        # Sea Update Logic
        if self.shape_type in ['bubble', 'fish', 'jellyfish']:
             return self.update_sea()
        
        # Weather Update Logic
        if self.shape_type in ['raindrop', 'snowflake', 'sun', 'cloud']:
            return self.update_weather()

        # Standard Shape Update
        if self.state == "in":
            if self.shape_type == 'emoji':
                 self.scale += 0.15
                 if self.scale >= 1.2: # Overshoot
                     self.state = "settle"
                     self.scale = 1.2
            else:
                self.scale += 0.1
                if self.scale >= 1.0:
                    self.scale = 1.0
                    self.state = "active"
                    
        elif self.state == "settle": # State for bounce back
            self.scale -= 0.05
            if self.scale <= 1.0:
                self.scale = 1.0
                self.state = "active"

        elif self.state == "out":
            self.scale -= 0.05
            if self.scale <= 0:
                self.destroy()
                return False

        current_size = self.base_size * self.scale
        if self.state == "in" and self.shape_type != 'emoji':
            self.angle += self.spin_speed

        if self.shape_type == 'text':
             new_size = max(1, int(current_size))
             self.canvas.itemconfigure(self.item_id, font=("Arial", new_size, "bold"))

        elif self.shape_type == 'emoji':
             new_size = max(1, int(current_size))
             self.canvas.itemconfigure(self.item_id, font=("Arial", new_size))

        elif self.shape_type == 'oval':
            r = current_size / 2
            self.canvas.coords(self.item_id, self.x - r, self.y - r, self.x + r, self.y + r)
            self.canvas.itemconfigure(self.item_id, width=max(1, int(5 * self.scale)))

        else: # Polygon logic
            r = current_size / 2
            points = []
            rad = math.radians(self.angle)
            
            if self.shape_type == 'star':
                 steps = self.points_count * 2
                 for i in range(steps):
                     theta = rad + math.radians(-90 + i * (360/steps))
                     d = r if i % 2 == 0 else r * 0.4 
                     px = self.x + d * math.cos(theta)
                     py = self.y + d * math.sin(theta)
                     points.append(px)
                     points.append(py)
            elif self.shape_type == 'paint':
                 if self.paint_style == 'splat':
                     for i in range(self.points_count):
                        theta = rad + math.radians(i * (360/self.points_count))
                        d = r * self.splat_radii[i]
                        px = self.x + d * math.cos(theta)
                        py = self.y + d * math.sin(theta)
                        points.extend([px, py])
                     self.canvas.itemconfigure(self.item_id, width=1)
                     self.canvas.coords(self.item_id, *points)
                 # Line and spray handled at creation, no complex update needed unless expanding
                 return True

                 # Drip Logic (Simple)
                 if self.state == 'active' and random.random() < 0.05 and not hasattr(self, 'drip_id'):
                     # Start a drip
                     pass # Keeping it simple for now, standard splats are messy enough!
            else:
                offset_angle = -90 if self.points_count % 2 != 0 else 45 
                for i in range(self.points_count):
                    theta = rad + math.radians(offset_angle + i * (360/self.points_count))
                    px = self.x + r * math.cos(theta)
                    py = self.y + r * math.sin(theta)
                    points.extend([px, py])
            
            self.canvas.coords(self.item_id, *points)
            self.canvas.itemconfigure(self.item_id, width=max(1, int(5 * self.scale)))

        return True

    def update_firework(self):
        if self.state == 'launch':
            self.y += self.vy
            self.vy *= 0.99 # Reduced air resistance to reach top of screen
            self.canvas.coords(self.item_id, self.x-3, self.y-5, self.x+3, self.y+5)
            
            if self.y <= self.target_y or self.vy > -2: 
                self.explode()
        
        elif self.state == 'explode':
            alive_count = 0
            for p in self.particles:
                p['life'] -= 1
                if p['life'] > 0:
                    alive_count += 1
                    p['x'] += p['vx']
                    p['y'] += p['vy']
                    p['vy'] += 0.05 # Lower Gravity (slower fall)
                    p['vx'] *= 0.98 # Lower Drag (bigger radius)
                    p['vy'] *= 0.98
                    
                    self.canvas.coords(p['id'], p['x']-2, p['y']-2, p['x']+2, p['y']+2)
                    
                    # Twinkle - Optimization: Only do this for low particle counts or infrequently
                    if p['life'] < 20 and p['life'] % 4 == 0: # Reduced frequency
                        self.canvas.itemconfigure(p['id'], state='hidden')
                    elif p['life'] < 20 and p['life'] % 4 == 2:
                        self.canvas.itemconfigure(p['id'], state='normal')
                else:
                    self.canvas.delete(p['id'])
            
            if alive_count == 0:
                self.destroy()
                return False
            
        elif self.state == 'out':
            self.destroy()
            return False
            
        return True

    def explode(self):
        self.state = 'explode'
        self.canvas.delete(self.item_id) # Remove rocket
        
        colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'white', 'cyan', 'magenta']
        
        # Optimization: Reduced particle count for better performance with many objects
        num_particles = random.randint(20, 50) 
        
        # 70% chance of uniform color burst, 30% mixed
        explosion_color = random.choice(colors) if random.random() > 0.3 else None 
        
        burst_type = random.choice(['sphere', 'ring', 'star_burst'])
        
        for i in range(num_particles):
            particle_color = explosion_color if explosion_color else random.choice(colors)
            vx, vy = 0, 0
            
            if burst_type == 'sphere':
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(4, 10) # Increased speed
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
            elif burst_type == 'ring':
                angle = (i / num_particles) * 2 * math.pi
                speed = random.uniform(6, 9) # Increased speed
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed
            elif burst_type == 'star_burst':
                arms = 5
                angle_base = (i % arms) * (2 * math.pi / arms)
                angle = angle_base + random.uniform(-0.2, 0.2)
                speed = random.uniform(5, 12) # Increased speed
                vx = math.cos(angle) * speed
                vy = math.sin(angle) * speed

            pid = self.canvas.create_oval(self.x, self.y, self.x, self.y, fill=particle_color, outline='')
            self.particles.append({
                'id': pid,
                'x': self.x,
                'y': self.y,
                'vx': vx,
                'vy': vy,
                'life': random.randint(70, 130) # Longer life
            })

    def update_weather(self):
        # Scale logic for sun/cloud (pop in)
        if self.shape_type in ['sun', 'cloud']:
            if self.state == "in":
                self.scale += 0.05
                if self.scale >= 1.0:
                    self.scale = 1.0
                    self.state = "active"
            elif self.state == "out":
                self.scale -= 0.05
                if self.scale <= 0:
                    self.destroy()
                    return False
        else:
            self.state = "active"
            self.scale = 1.0

        current_size = self.base_size * self.scale
        
        if self.shape_type == 'raindrop':
            self.y += self.vy
            self.canvas.coords(self.item_id, self.x, self.y, self.x, self.y + 20)
        
        elif self.shape_type == 'snowflake':
            self.y += self.vy
            self.vx_wobble += 0.1
            dx = math.sin(self.vx_wobble) * 2
            self.x += dx
            self.canvas.coords(self.item_id, self.x, self.y)
            
        elif self.shape_type == 'sun':
            self.x += self.vx
            self.angle += 1
            # Sun spin ? It's a circle.. unless we draw rays. 
            # I used create_oval. Let's just move it.
            r = current_size / 2
            self.canvas.coords(self.item_id, self.x - r, self.y - r, self.x + r, self.y + r)
            
        elif self.shape_type == 'cloud':
            self.x += self.vx
            # Clouds are ovals. Simple.
            w = current_size
            h = current_size * 0.6
            self.canvas.coords(self.item_id, self.x - w/2, self.y - h/2, self.x + w/2, self.y + h/2)

        # Offscreen check
        if self.y > self.canvas.winfo_height() + 50 or self.x < -100 or self.x > self.canvas.winfo_width() + 100:
            self.destroy()
            return False
            
        return True

    def update_sea(self):
        # Scale logic
        if self.state == "in":
            self.scale += 0.05
            if self.scale >= 1.0:
                self.scale = 1.0
                self.state = "active"
        elif self.state == "out":
            self.scale -= 0.05
            if self.scale <= 0:
                self.destroy()
                return False

        current_size = self.base_size * self.scale
        
        # Movement
        if self.shape_type == 'bubble':
            self.y += self.vy
            self.vx_wobble += 0.1
            dx = math.sin(self.vx_wobble) * 2
            self.x += dx
            
            # Draw Bubble
            r = current_size / 4 # Bubbles smaller
            self.canvas.coords(self.item_id, self.x - r, self.y - r, self.x + r, self.y + r)
            
        elif self.shape_type == 'fish':
            self.x += self.vx
            # Fish Shape
            # Facing right: Tail(-1), Head(+1). Facing left: Tail(+1), Head(-1)
            # Use self.scale_x (1 or -1)
            s = current_size / 2
            d = self.scale_x 
            # Tail, Top, Nose, Bot
            points = [
                self.x - (s * d), self.y,          # Tail center (pinch?)
                self.x - (s * 1.5 * d), self.y - s*0.5, # Tail Top
                self.x - (s * 1.5 * d), self.y + s*0.5, # Tail Bot
                self.x - (s * d), self.y,          # Tail center
                self.x, self.y - s*0.5,            # Body Top
                self.x + (s * d), self.y,          # Nose
                self.x, self.y + s*0.5             # Body Bot
            ]
            self.canvas.coords(self.item_id, *points)

        elif self.shape_type == 'jellyfish':
            self.y += self.vy
            self.pulse_phase += 0.1
            pulse = 1.0 + 0.1 * math.sin(self.pulse_phase)
            
            s = current_size * 0.6 * pulse
            # Bell shape 
            points = [
                self.x - s, self.y + s*0.5, 
                self.x - s, self.y - s,     
                self.x + s, self.y - s,     
                self.x + s, self.y + s*0.5, 
                self.x, self.y 
            ]
            self.canvas.coords(self.bell, *points)
            
            # Update Tentacles
            for t in self.tentacles:
                # Wavy movement logic
                tx = self.x + random.uniform(-2, 2)
                ty_start = self.y + s*0.5
                ty_end = ty_start + 40 + s
                # Simple line, maybe wave midpoint?
                self.canvas.coords(t['id'], self.x + (t['offset']-20)*pulse, ty_start, self.x + (t['offset']-20)*pulse + math.sin(self.pulse_phase + t['phase'])*10, ty_end)

        # Offscreen check
        if self.y < -100 or self.x < -100 or self.x > self.canvas.winfo_width() + 100:
            self.destroy()
            return False
            
        return True

    def destroy(self):
        if self.shape_type == 'firework':
            if hasattr(self, 'particles'):
                for p in self.particles: 
                    try: self.canvas.delete(p['id'])
                    except: pass
            # Try delete rocket if it still exists
            try: self.canvas.delete(self.item_id)
            except: pass
        elif self.shape_type == 'jellyfish':
             try: self.canvas.delete(self.bell)
             except: pass
             if hasattr(self, 'tentacles'):
                for t in self.tentacles: 
                    try: self.canvas.delete(t['id']) 
                    except: pass
        elif self.shape_type == 'paint' and hasattr(self, 'paint_style') and self.paint_style == 'spray':
             if hasattr(self, 'spray_dots'):
                for d in self.spray_dots: 
                    try: self.canvas.delete(d)
                    except: pass
        else:
            try: self.canvas.delete(self.item_id)
            except: pass

class SmashtopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smashtop")
        
        # specific configurations for full screen and focus
        self.root.attributes('-fullscreen', True)
        self.root.focus_force()
        self.root.bind('<Escape>', lambda e: None) # Disable default escape behavior if any

        # State
        self.sound_enabled = tk.BooleanVar(value=True)
        self.theme = tk.StringVar(value="Shapes") # Options: "Shapes", "Fireworks"
        self.max_objects = tk.IntVar(value=50)
        self.bg_color_var = tk.StringVar(value="black")
        self.objects = []
        self.paint_temp_objects = [] # Objects waiting to be baked
        self.last_paint_update = 0

        # Canvas for drawing
        self.canvas = tk.Canvas(self.root, bg=self.bg_color_var.get(), highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)

        # Bind events
        self.root.bind('<Key>', self.on_key_press)
        
        # Complex key combinations
        # Note: 'keyboard' library handles global hooks, but we can also check modifiers in tkinter events
        # using 'keyboard' for system lockout is better.

        self.setup_system_lockout()
        
        # Instructions on screen temporarily
        self.label = self.canvas.create_text(
            self.root.winfo_screenwidth() // 2, 
            self.root.winfo_screenheight() // 2, 
            text="Smashtop Initialized.\nType keys to play!",
            fill="white", font=("Arial", 24), justify='center'
        )

        # Permanent instructions at bottom
        instr_text = "Shortcuts: Ctrl+Shift+Q to Quit | Ctrl+Alt+Shift+O for Settings"
        self.instr_label = tk.Label(self.root, text=instr_text, fg="gray", bg="black", font=("Arial", 10))
        self.instr_label.place(relx=0.5, rely=0.95, anchor="center")

        # Quit Button
        quit_btn = tk.Button(self.root, text="Triple Click to Quit", bg="#222", fg="white", font=("Arial", 8))
        quit_btn.place(relx=0.5, y=0, anchor="n")
        quit_btn.bind("<Triple-Button-1>", lambda e: self.exit_app())

        self.setup_paint_layer()
        self.animation_loop()

    def setup_paint_layer(self):
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        self.paint_image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.paint_draw = ImageDraw.Draw(self.paint_image)
        self.tk_paint_image = ImageTk.PhotoImage(self.paint_image)
        # Place at bottom of stack (but above background color)
        self.paint_canvas_item = self.canvas.create_image(0, 0, image=self.tk_paint_image, anchor="nw")

    def animation_loop(self):
        # Filter alive objects
        self.objects = [obj for obj in self.objects if obj.update()]
        
        # Check limits logic (Disable for Paint mode)
        if self.theme.get() != 'Paint':
            target_max = self.max_objects.get()
            # Count non-dying objects
            active = [o for o in self.objects if o.state != 'out']
            if len(active) > target_max:
                # Fade out oldest active
                active[0].fade_out()
        
        # Paint Mode "Baking" Logic
        # Strategy: Objects are created as vectors (fast). 
        # We also draw them to the PIL image (invisible). 
        # Periodically, we update the background image and delete vectors.
        import time
        now = time.time()
        BAKE_INTERVAL = 2.0 # Seconds between heavy updates
        BAKE_COUNT = 50 # Or if too many objects accumulate

        if self.theme.get() == "Paint":
            need_bake = False
            if len(self.paint_temp_objects) > BAKE_COUNT:
                need_bake = True
            elif len(self.paint_temp_objects) > 0 and (now - self.last_paint_update > BAKE_INTERVAL):
                need_bake = True
            
            if need_bake:
                try:
                    self.tk_paint_image = ImageTk.PhotoImage(self.paint_image)
                    self.canvas.itemconfigure(self.paint_canvas_item, image=self.tk_paint_image)
                    
                    # Delete the vectors
                    for obj in self.paint_temp_objects:
                        obj.destroy() # Uses canvas.delete(item_id)
                        if obj in self.objects:
                            self.objects.remove(obj)
                    
                    self.paint_temp_objects = []
                    self.last_paint_update = now
                except Exception as e:
                    print(f"Bake Error: {e}")

        # Ensure app stays on top (combat overlays like Game Bar) unless settings are open
        settings_open = hasattr(self, 'settings_win') and self.settings_win.winfo_exists()
        if not settings_open:
            self.root.attributes('-topmost', True)
        else:
            self.root.attributes('-topmost', False) # Allow settings to float above

        self.root.after(30, self.animation_loop)

    def setup_system_lockout(self):
        # This will need administrative privileges to block system keys effectively on Windows
        try:
            # 1. Register operational hotkeys FIRST so they work even if we block other things
            # Use root.after to ensure these run on the main Tkinter thread
            keyboard.add_hotkey('ctrl+shift+q', lambda: self.root.after(0, self.exit_app), suppress=True)
            keyboard.add_hotkey('ctrl+alt+shift+o', lambda: self.root.after(0, self.open_settings), suppress=True)

            # 2. Block Windows keys entirely (and Menu key)
            # This disables the Start Menu and most Windows shortcuts
            for key in ['left windows', 'right windows', 'menu']:
                try:
                    keyboard.block_key(key)
                except Exception:
                    pass

            # 3. Block specific disruptive combos involving Alt
            # We don't block 'alt' completely so valid hotkeys (like ours) still work
            try:
                keyboard.add_hotkey('alt+tab', lambda: None, suppress=True)
                keyboard.add_hotkey('alt+f4', lambda: None, suppress=True)
            except Exception:
                pass
            
        except ImportError:
            print("Keyboard module not found. System lockout will not work.")
        except Exception as e:
            print(f"Error setting up lockout: {e}")

    def on_key_press(self, event):
        # Generate visual response
        self.play_sound()
        self.add_object(event)

    def add_object(self, event):
        char = event.char
        colors = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'cyan', 'magenta']
        main_x = random.randint(0, self.root.winfo_screenwidth())
        main_y = random.randint(0, self.root.winfo_screenheight())
        # Clear previous text if it's the welcome message
        self.canvas.delete(self.label)
        
        current_theme = self.theme.get()
        loop_count = 1
        
        if current_theme == "Paint":
            loop_count = random.randint(1, 10)
        
        for _ in range(loop_count):
            if loop_count > 1:
                x = random.randint(0, self.root.winfo_screenwidth())
                y = random.randint(0, self.root.winfo_screenheight())
            else:
                x = main_x
                y = main_y

            shape_type = ""
            current_char = char
            
            if current_theme == "Fireworks":
                shape_type = "firework"
            elif current_theme == "Emoji":
                shape_type = 'emoji'
                # Range of some common emojis
                emojis = [
                    '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃', '😉', '😊', '😇',
                    '🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯', '🦁', '🐮', '🐷',
                    '🍏', '🍎', '🍐', '🍊', '🍋', '🍌', '🍉', '🍇', '🍓', '🍈', '🍒', '🍑', '🍍',
                    '🚗', '🚕', '🚙', '🚌', '🚎', '🏎', '🚓', '🚑', '🚒', '🚐', '🚚', '🚛', '🚜',
                    '⚽', '🏀', '🏈', '⚾', '🥎', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🥅', '🏒',
                    '🌈', '☀️', '⭐', '🌟', '🌙', '☁️', '❄️', '🔥', '🎈', '🎁', '🎂', '🎨', '🎺',
                    '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞'
                ]
                current_char = random.choice(emojis)
            elif current_theme == "Paint":
                shape_type = 'paint'
            elif current_theme == "Sea":
                shape_type = random.choice(['bubble', 'bubble', 'fish', 'fish', 'jellyfish'])
            else:
                if current_char and current_char.isalnum():
                    shape_type = 'text'
                    current_char = current_char.upper()
                else:
                    shape_type = random.choice(['oval', 'triangle', 'square', 'pentagon', 'hexagon', 'star'])

            # Pass paint_draw reference if in paint mode
            p_draw = self.paint_draw if current_theme == "Paint" else None
            
            obj = AnimatedObject(self.canvas, x, y, random.choice(colors), shape_type, current_char, paint_draw=p_draw)
            self.objects.append(obj)
            
            if current_theme == "Paint":
                self.paint_temp_objects.append(obj)

    def play_sound(self):
        if not self.sound_enabled.get():
            return
            
        def _beep():
            # Cheery Major Scale Frequencies (C4 to C6 roughly)
            notes = [261, 293, 329, 349, 392, 440, 493, 523, 587, 659, 698, 783, 880]
            freq = random.choice(notes)
            duration = 100 # ms
            try:
                winsound.Beep(freq, duration)
            except RuntimeError:
                pass # Can happen if sound is already playing or system issue

        threading.Thread(target=_beep, daemon=True).start()

            
    def open_settings(self):
        # Check if settings window already exists
        if hasattr(self, 'settings_win') and self.settings_win.winfo_exists():
            self.settings_win.lift()
            return

        self.settings_win = tk.Toplevel(self.root)
        self.settings_win.title("Smashtop Settings")
        self.settings_win.geometry("300x400")
        # Center the window
        cx = self.root.winfo_screenwidth() // 2 - 150
        cy = self.root.winfo_screenheight() // 2 - 200
        self.settings_win.geometry(f"+{cx}+{cy}")
        self.settings_win.attributes('-topmost', True)
        self.settings_win.focus_force()

        tk.Label(self.settings_win, text="Settings", font=("Arial", 14, "bold")).pack(pady=10)

        # Sound Toggle
        tk.Checkbutton(self.settings_win, text="Enable Sounds", variable=self.sound_enabled, font=("Arial", 12)).pack(anchor='w', padx=20)

        tk.Label(self.settings_win, text="Theme:", font=("Arial", 12, "bold")).pack(anchor='w', padx=20, pady=(10, 0))
        
        # Theme Selection
        tk.Radiobutton(self.settings_win, text="Shapes & Letters", variable=self.theme, value="Shapes", font=("Arial", 12)).pack(anchor='w', padx=20)
        tk.Radiobutton(self.settings_win, text="Fireworks", variable=self.theme, value="Fireworks", font=("Arial", 12)).pack(anchor='w', padx=20)
        tk.Radiobutton(self.settings_win, text="Emoji Pop", variable=self.theme, value="Emoji", font=("Arial", 12)).pack(anchor='w', padx=20)
        tk.Radiobutton(self.settings_win, text="Paint Splatter", variable=self.theme, value="Paint", font=("Arial", 12)).pack(anchor='w', padx=20)
        tk.Radiobutton(self.settings_win, text="Under the Sea", variable=self.theme, value="Sea", font=("Arial", 12)).pack(anchor='w', padx=20)
        
        # Background Color
        tk.Label(self.settings_win, text="Background:", font=("Arial", 12, "bold")).pack(anchor='w', padx=20, pady=(10, 0))
        colors_frame = tk.Frame(self.settings_win)
        colors_frame.pack(anchor='w', padx=20)
        
        for name, col in [("Black", "black"), ("White", "white"), ("Navy", "navy"), ("Dark Gray", "#222222")]:
            tk.Radiobutton(colors_frame, text=name, variable=self.bg_color_var, value=col, 
                          command=self.update_background, font=("Arial", 10)).pack(anchor='w')

        tk.Label(self.settings_win, text="Max Objects:", font=("Arial", 12, "bold")).pack(anchor='w', padx=20, pady=(10,0))
        tk.Scale(self.settings_win, from_=1, to=100, orient='horizontal', variable=self.max_objects).pack(fill='x', padx=20)

        tk.Button(self.settings_win, text="Close", command=self.close_settings, bg="#dddddd", font=("Arial", 10)).pack(pady=20)
        self.settings_win.protocol("WM_DELETE_WINDOW", self.close_settings)

    def update_background(self):
        new_color = self.bg_color_var.get()
        self.canvas.configure(bg=new_color)
        
        # Contrast adjustment for text
        text_color = "black" if new_color == "white" else "white"
        
        # Update persistent instructions
        if hasattr(self, 'instr_label'):
             instr_fg = "black" if new_color == "white" else "gray"
             self.instr_label.configure(bg=new_color, fg=instr_fg)

    def close_settings(self):
        if hasattr(self, 'settings_win') and self.settings_win:
            self.settings_win.destroy()
        
        # Clear all objects from screen
        for obj in self.objects:
            obj.destroy()
        self.objects = []
        # Clear Paint List
        self.paint_temp_objects = []
        self.canvas.delete("all") # Ensure canvas is clean
        
        # Reset Paint Layer
        self.setup_paint_layer()

        # Restore instructions
        txt_fill = "black" if self.bg_color_var.get() == "white" else "white"
        self.label = self.canvas.create_text(
            self.root.winfo_screenwidth() // 2, 
            self.root.winfo_screenheight() // 2, 
            text="Smashtop Ready!\nType keys to play!",
            fill=txt_fill, font=("Arial", 24), justify='center'
        )
        self.root.focus_force()

    def exit_app(self):
        # Unblock keys
        try:
            keyboard.unhook_all()
        except:
            pass
        self.root.quit()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = SmashtopApp(root)
    root.mainloop()
