import arcade
import arcade.shape_list
import math

class Vignette:
    def __init__(self, width: int, height: int, color: tuple):
        self.width = width
        self.height = height
        self.base_color = color
        self.shape_list = None
        
        # Dark mode state
        self.is_dark_mode = False
        self.dark_color = (20, 20, 20)
        
        # Current color (RGB only)
        self.current_color = list(color[:3])
        self.target_color = list(color[:3])
        
        # Thickness ratios
        self.normal_thickness_ratio = 0.15
        self.dark_thickness_ratio = 0.08
        self.current_thickness_ratio = self.normal_thickness_ratio
        self.target_thickness_ratio = self.normal_thickness_ratio
        
        self.thickness_x = int(width * self.current_thickness_ratio)
        self.thickness_y = int(height * self.current_thickness_ratio)
        
        self.refresh()

    def set_dark_mode(self, enabled: bool):
        self.is_dark_mode = enabled
        if enabled:
            self.target_color = list(self.dark_color)
            self.target_thickness_ratio = self.dark_thickness_ratio
        else:
            self.target_color = list(self.base_color[:3])
            self.target_thickness_ratio = self.normal_thickness_ratio

    def update(self, delta_time: float):
        # Lerp color
        color_changed = False
        for i in range(3):
            diff = self.target_color[i] - self.current_color[i]
            if abs(diff) > 0.5:
                self.current_color[i] += diff * 0.1
                color_changed = True

        # Lerp thickness
        thickness_diff = self.target_thickness_ratio - self.current_thickness_ratio
        thickness_changed = False
        if abs(thickness_diff) > 0.001:
            self.current_thickness_ratio += thickness_diff * 0.1
            self.thickness_x = int(self.width * self.current_thickness_ratio)
            self.thickness_y = int(self.height * self.current_thickness_ratio)
            thickness_changed = True
            
        if color_changed or thickness_changed:
            self.refresh()

    def refresh(self):
        self.shape_list = arcade.shape_list.ShapeElementList()
        
        r = int(self.current_color[0])
        g = int(self.current_color[1])
        b = int(self.current_color[2])

        # Use a lower alpha to allow the background to show through (Infinite feel)
        # 150 is approx 60% opacity.
        alpha = 150 
        
        c_solid = (r, g, b, alpha)
        c_trans = (r, g, b, 0)
        
        w = self.width
        h = self.height
        tx = self.thickness_x
        ty = self.thickness_y

        # --- Side Rectangles (Linear Gradients) ---
        # Top (between corners)
        p_top = [
            (tx, h - ty),      # BL
            (w - tx, h - ty),  # BR
            (w - tx, h),       # TR
            (tx, h)            # TL
        ]
        c_top = [c_trans, c_trans, c_solid, c_solid]
        
        # Bottom (between corners)
        p_bot = [
            (tx, 0),           # BL
            (w - tx, 0),       # BR
            (w - tx, ty),      # TR
            (tx, ty)           # TL
        ]
        c_bot = [c_solid, c_solid, c_trans, c_trans]
        
        # Left (between corners)
        p_left = [
            (0, ty),           # BL
            (tx, ty),          # BR
            (tx, h - ty),      # TR
            (0, h - ty)        # TL
        ]
        c_left = [c_solid, c_trans, c_trans, c_solid]
        
        # Right (between corners)
        p_right = [
            (w - tx, ty),      # BL
            (w, ty),           # BR
            (w, h - ty),       # TR
            (w - tx, h - ty)   # TL
        ]
        c_right = [c_trans, c_solid, c_solid, c_trans]

        self.shape_list.append(arcade.shape_list.create_rectangles_filled_with_colors(p_top, c_top))
        self.shape_list.append(arcade.shape_list.create_rectangles_filled_with_colors(p_bot, c_bot))
        self.shape_list.append(arcade.shape_list.create_rectangles_filled_with_colors(p_left, c_left))
        self.shape_list.append(arcade.shape_list.create_rectangles_filled_with_colors(p_right, c_right))

        # --- Corner Fans (Radial Gradients) ---
        # We approximate a quarter-circle gradient using a triangle fan.
        steps = 10
        
        def add_corner_fan(center_x, center_y, start_angle, end_angle, radius_x, radius_y, corner_x, corner_y):
            # Center point is transparent
            # Outer arc is solid
            # We also draw a solid fan from the screen corner to the arc to fill the gap.
            
            angle_step = (end_angle - start_angle) / steps
            
            for i in range(steps):
                a1 = start_angle + i * angle_step
                a2 = start_angle + (i + 1) * angle_step
                
                p1 = (center_x, center_y)
                p2 = (center_x + math.cos(a1) * radius_x, center_y + math.sin(a1) * radius_y)
                p3 = (center_x + math.cos(a2) * radius_x, center_y + math.sin(a2) * radius_y)
                
                # Gradient Triangle: Center (Trans) -> Arc (Solid)
                self.shape_list.append(arcade.shape_list.create_triangles_filled_with_colors(
                    [p1, p2, p3],
                    [c_trans, c_solid, c_solid]
                ))
                
                # Filler Triangle: Corner (Solid) -> Arc (Solid)
                # This fills the space between the rounded arc and the square screen corner
                self.shape_list.append(arcade.shape_list.create_triangles_filled_with_colors(
                    [(corner_x, corner_y), p2, p3],
                    [c_solid, c_solid, c_solid]
                ))

        # Top-Left Corner
        # Center: (tx, h-ty), Corner: (0, h)
        add_corner_fan(tx, h - ty, math.pi/2, math.pi, tx, ty, 0, h)
        
        # Top-Right Corner
        # Center: (w-tx, h-ty), Corner: (w, h)
        add_corner_fan(w - tx, h - ty, 0, math.pi/2, tx, ty, w, h)
        
        # Bottom-Right Corner
        # Center: (w-tx, ty), Corner: (w, 0)
        add_corner_fan(w - tx, ty, 3*math.pi/2, 2*math.pi, tx, ty, w, 0)
        
        # Bottom-Left Corner
        # Center: (tx, ty), Corner: (0, 0)
        add_corner_fan(tx, ty, math.pi, 3*math.pi/2, tx, ty, 0, 0)

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.thickness_x = int(self.width * self.current_thickness_ratio)
        self.thickness_y = int(self.height * self.current_thickness_ratio)
        self.refresh()

    def draw(self):
        if self.shape_list:
            self.shape_list.draw()