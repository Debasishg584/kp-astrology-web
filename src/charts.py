import tkinter as tk
import math
import random
import os
from typing import Any, Dict
from PIL import Image, ImageTk # type: ignore
from src.utils import get_resource_path # type: ignore
from src.translations import convert_number # type: ignore

class ChartDrawer:
    def __init__(self, canvas: Any):
        self.canvas: Any = canvas # Use Any to satisfy strict canvas interactions
        self.center_x: int = 0
        self.center_y: int = 0
        self.radius: int = 0
        self.images: Dict[str, Any] = {} # Cache images so they don't disappear
        
        # Distance from center (0.1 = close, 1.0 = edge)
        self.orbit_map = {
            "Moon": 0.30, "Mercury": 0.38, "Venus": 0.45, "Sun": 0.52,
            "Mars": 0.60, "Jupiter": 0.68, "Saturn": 0.75,
            "Rahu": 0.82, "Ketu": 0.82, "Uranus": 0.88, "Neptune": 0.94, "Pluto": 0.98
        }

    def load_image(self, name: str, size: tuple = (30, 30)) -> Any:
        """Safe image loader. Returns None if file is missing."""
        if name in self.images: return self.images[name]
        
        # Robust path finding for assets
        try:
            path = get_resource_path(os.path.join("assets", name))
        except Exception:
            path = os.path.join("assets", name)
        
        if not os.path.exists(path):
            # Fail silently to console, don't crash app
            print(f"⚠️ Warning: Image not found at {path}") 
            return None 
            
        try:
            pil_img = Image.open(path)
            # High-quality resize
            pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            self.images[name] = tk_img
            return tk_img
        except Exception as e:
            print(f"❌ Error loading {name}: {e}")
            return None

    def draw_base_chart(self):
        """Draws the background, stars, orbits, and center human."""
        canvas = self.canvas
        if not canvas: return
        
        canvas.delete("all")
        w_val: int = int(canvas.winfo_width())
        h_val: int = int(canvas.winfo_height())
        
        # Fallback if window hasn't fully loaded yet
        if w_val < 50: w_val = 1200 
        if h_val < 50: h_val = 800
        
        self.center_x, self.center_y = int(w_val // 2), int(h_val // 2)
        self.radius = int(min(w_val, h_val) // 2 - 40)
        cx, cy = self.center_x, self.center_y
        r_outer = float(self.radius)

        # 1. COSMIC VOID BACKGROUND
        canvas.create_rectangle(0, 0, float(w_val*2), float(h_val*2), fill="#050510", outline="")
        
        # 2. ELEGANT TINY SPIRAL GALAXIES
        for _ in range(18):  # Fewer, more elegant galaxies
            gx: int = random.randint(30, max(31, int(w_val) - 30))
            gy: int = random.randint(30, max(31, int(h_val) - 30))
            
            # Very small galaxy sizes (tiny and subtle)
            base_size = random.choice([3, 4, 5, 6])
            
            # Rotation angle for this galaxy
            rotation = random.uniform(0, 360)
            
            # Draw delicate spiral arms using small dots
            num_arms = 2
            dots_per_arm = random.randint(6, 10)
            
            for arm in range(num_arms):
                arm_start = rotation + (arm * 180)  # 2 arms, 180° apart
                
                for dot in range(dots_per_arm):
                    # Spiral formula: r increases as angle increases
                    t = dot / dots_per_arm
                    spiral_angle = arm_start + (t * 180)  # Arm curves 180°
                    spiral_radius = base_size * (0.3 + t * 2.5)
                    
                    rad = math.radians(spiral_angle)
                    dx = gx + spiral_radius * math.cos(rad)
                    dy = gy + spiral_radius * math.sin(rad)
                    
                    # Dots fade as they go outward
                    alpha_sim = int(180 - t * 120)
                    dot_color = f"#{alpha_sim:02x}{alpha_sim:02x}{int(alpha_sim*1.2):02x}"
                    
                    dot_size = max(1, int((1 - t) * 2))
                    canvas.create_oval(
                        dx - dot_size, dy - dot_size,
                        dx + dot_size, dy + dot_size,
                        fill=dot_color, outline=""
                    )
            
            # Tiny bright core (very subtle glow)
            core_glow = base_size * 0.8
            canvas.create_oval(
                gx - core_glow, gy - core_glow,
                gx + core_glow, gy + core_glow,
                fill="#1a1a2e", outline=""
            )
            
            # Bright center point
            canvas.create_oval(
                gx - 1.5, gy - 1.5,
                gx + 1.5, gy + 1.5,
                fill="#c8c8ff", outline=""
            )
            canvas.create_oval(
                gx - 0.5, gy - 0.5,
                gx + 0.5, gy + 0.5,
                fill="#ffffff", outline=""
            )
        
        # Twinkling stars at varying distances
        for _ in range(100):
            sx: int = random.randint(0, max(1, int(w_val)))
            sy: int = random.randint(0, max(1, int(h_val)))
            brightness = random.choice([40, 60, 80, 100, 140, 180, 220])
            sz = 1 if brightness < 100 else random.choice([1, 2])
            col = f"#{brightness:02x}{brightness:02x}{min(255, brightness + 20):02x}"
            canvas.create_oval(sx, sy, sx+sz, sy+sz, fill=col, outline="")

        # 3. ORBIT RINGS
        sorted_radii = sorted(list(set(self.orbit_map.values())))
        for r_factor in sorted_radii:
            r = r_outer * r_factor
            canvas.create_oval(
                cx - r, cy - r,
                cx + r, cy + r,
                outline="#303050", dash=(2, 6), width=1
            )
            
        # 4. OUTER ZODIAC RING
        canvas.create_oval(
            cx - r_outer, cy - r_outer,
            cx + r_outer, cy + r_outer,
            outline="#00E5FF", width=2
        )

        # 5. CENTER IMAGE (Human) — larger for visual focus
        human_img = self.load_image("human.png", size=(64, 64))
        if human_img:
            canvas.create_image(cx, cy, image=human_img)
        else:
            # Fallback Symbol
            canvas.create_text(cx, cy, text="🧘", fill="white", font=("Arial", 36))

    def draw_full_chart(self, planets, cusps):
        """Draws House Lines and Planets on top of the base chart."""
        self.draw_base_chart()
        canvas = self.canvas
        if not canvas: return
        
        cx, cy = self.center_x, self.center_y
        r_outer = self.radius

        # --- DRAW HOUSE CUSPS ---
        for i in range(1, 13):
            angle_deg = cusps[i]
            rad = math.radians(angle_deg)
            
            # Line coordinates
            x_end = cx + r_outer * math.cos(rad)
            y_end = cy - r_outer * math.sin(rad)
            
            # Draw faint house line
            canvas.create_line(cx, cy, x_end, y_end, fill="#444466", width=1)
            
            # Draw Cusp Number (Outside ring) — larger font for readability
            x_txt = cx + (r_outer + 22) * math.cos(rad)
            y_txt = cy - (r_outer + 22) * math.sin(rad)
            canvas.create_text(x_txt, y_txt, text=convert_number(str(i)), fill="#00E5FF", font=("Segoe UI", 11, "bold"))

        # --- DRAW PLANETS ---
        for planet, longitude in planets.items():
            # 1. Position
            r_factor = self.orbit_map.get(planet, 0.90)
            current_radius = r_outer * r_factor
            rad = math.radians(float(longitude))
            
            x = cx + current_radius * math.cos(rad)
            y = cy - current_radius * math.sin(rad)
            
            # 2. Draw Image — larger icons for prominence
            sz = (48, 48) if planet in ["Sun", "Jupiter"] else (34, 34)
            p_img = self.load_image(f"{planet}.png", size=sz)
            
            if p_img:
                canvas.create_image(x, y, image=p_img)
                # Degree label — slightly larger
                canvas.create_text(x, y+24, text=convert_number(f"{int(float(longitude))}°"), fill="#CCCCDD", font=("Segoe UI", 9))
            else:
                # Fallback Dot
                canvas.create_oval(x-6, y-6, x+6, y+6, fill="yellow", outline="white")
                canvas.create_text(x, y-17, text=str(planet)[:2], fill="white", font=("Arial", 9, "bold"))

        canvas.update()