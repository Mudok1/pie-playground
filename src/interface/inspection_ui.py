import arcade
import arcade.gui

class InspectionUI:
    def __init__(self, window: arcade.Window, on_close_callback):
        self.window = window
        self.on_close = on_close_callback
        
        self.ui_manager = arcade.gui.UIManager(window)
        self.ui_manager.enable()
        
        # UI State
        self.visible = False
        
        # Layout
        self.root_layout = arcade.gui.UIAnchorLayout()
        self.ui_manager.add(self.root_layout)
        
        # Close Button (Top-Right)
        style_close = {
            "font_name": ("calibri", "arial"),
            "font_size": 12,
            "font_color": arcade.color.WHITE,
            "bg_color": arcade.color.RED,
            "border_color": arcade.color.DARK_RED,
            "border_width": 1,
        }
        
        self.btn_close = arcade.gui.UIFlatButton(text="X", width=30, height=30, style={"normal": style_close, "hover": style_close, "press": style_close})
        self.btn_close.on_click = self._on_close_click
        
        self.root_layout.add(
            child=self.btn_close,
            anchor_x="right",
            align_x=-20,
            anchor_y="top",
            align_y=-20
        )
        
        # Placeholder Rects (calculated in resize)
        self.right_panel_rect = None
        self.bottom_left_panel_rect = None
        
        self.on_resize(window.width, window.height)

    def enable(self):
        self.visible = True
        self.ui_manager.enable()

    def disable(self):
        self.visible = False
        self.ui_manager.disable()

    def _on_close_click(self, event):
        if self.on_close:
            self.on_close()

    def on_resize(self, width, height):
        # Right Panel: 40% width, full height (minus padding)
        rp_w = width * 0.4
        rp_h = height * 0.9
        rp_x = width - rp_w - 20
        rp_y = (height - rp_h) / 2
        self.right_panel_rect = (rp_x, rp_y, rp_w, rp_h)
        
        # Bottom Left Panel: 50% width, 20% height
        bl_w = width * 0.5
        bl_h = height * 0.2
        bl_x = 20
        bl_y = 20
        self.bottom_left_panel_rect = (bl_x, bl_y, bl_w, bl_h)

    def draw(self):
        if not self.visible:
            return
            
        def draw_rect_poly(x, y, w, h, color, outline_color=None):
            # x, y is bottom-left corner
            p1 = (x, y)
            p2 = (x + w, y)
            p3 = (x + w, y + h)
            p4 = (x, y + h)
            arcade.draw_polygon_filled([p1, p2, p3, p4], color)
            if outline_color:
                arcade.draw_line_strip([p1, p2, p3, p4, p1], outline_color, 2)

        # Draw Panels
        # Right Panel (UpSet Plot Placeholder)
        if self.right_panel_rect:
            x, y, w, h = self.right_panel_rect
            draw_rect_poly(x, y, w, h, (240, 240, 240, 200), arcade.color.GRAY)
            cx = x + w / 2
            cy = y + h / 2
            arcade.draw_text("UPSET PLOT", cx, cy, arcade.color.BLACK, 20, anchor_x="center", anchor_y="center")
            
        # Bottom Left Panel (Formula Placeholder)
        if self.bottom_left_panel_rect:
            x, y, w, h = self.bottom_left_panel_rect
            draw_rect_poly(x, y, w, h, (240, 240, 240, 200), arcade.color.GRAY)
            cx = x + w / 2
            cy = y + h / 2
            arcade.draw_text("Fórmula: |A ∪ B| = |A| + |B| - |A ∩ B|", cx, cy, arcade.color.BLACK, 16, anchor_x="center", anchor_y="center")

        # Draw UI Manager (Buttons)
        self.ui_manager.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.visible:
            return False
        return self.ui_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.visible:
            return False
        return self.ui_manager.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.visible:
            return False
        return self.ui_manager.on_mouse_release(x, y, button, modifiers)
