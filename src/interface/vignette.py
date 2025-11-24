import arcade
import arcade.shape_list

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

        c_solid = (r, g, b, 255)
        c_trans = (r, g, b, 0)
        
        w = self.width
        h = self.height
        tx = self.thickness_x
        ty = self.thickness_y

        # Top
        p_top = [
            (0, h - ty),  # BL
            (w, h - ty),  # BR
            (w, h),       # TR
            (0, h)        # TL
        ]
        c_top = [c_trans, c_trans, c_solid, c_solid]
        
        # Bottom
        p_bot = [
            (0, 0),       # BL
            (w, 0),       # BR
            (w, ty),      # TR
            (0, ty)       # TL
        ]
        c_bot = [c_solid, c_solid, c_trans, c_trans]
        
        # Left
        p_left = [
            (0, 0),       # BL
            (tx, 0),      # BR
            (tx, h),      # TR
            (0, h)        # TL
        ]
        c_left = [c_solid, c_trans, c_trans, c_solid]
        
        # Right
        p_right = [
            (w - tx, 0),  # BL
            (w, 0),       # BR
            (w, h),       # TR
            (w - tx, h)   # TL
        ]
        c_right = [c_trans, c_solid, c_solid, c_trans]
        
        # Use arcade.shape_list.create_rectangles_filled_with_colors
        self.shape_list.append(arcade.shape_list.create_rectangles_filled_with_colors(p_top, c_top))
        self.shape_list.append(arcade.shape_list.create_rectangles_filled_with_colors(p_bot, c_bot))
        self.shape_list.append(arcade.shape_list.create_rectangles_filled_with_colors(p_left, c_left))
        self.shape_list.append(arcade.shape_list.create_rectangles_filled_with_colors(p_right, c_right))

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.thickness_x = int(self.width * self.current_thickness_ratio)
        self.thickness_y = int(self.height * self.current_thickness_ratio)
        self.refresh()

    def draw(self):
        if self.shape_list:
            self.shape_list.draw()