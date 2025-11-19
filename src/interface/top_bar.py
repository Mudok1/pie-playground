import arcade
import arcade.gui
from src.interface.ui_helpers import get_rounded_rect_points
import math

class TopBar:
    def __init__(self, window: arcade.Window, on_set_click_callback):
        self.window = window
        self.on_set_click = on_set_click_callback

        self.ui_manager = arcade.gui.UIManager(window=self.window)
        self.ui_manager.enable()

        base_style = {
            "font_name": ("calibri", "arial"),
            "font_size": 12,
            "font_color": arcade.color.WHITE,
            "bg_color": (40, 40, 80), 
            "border_color": arcade.color.WHITE,
            "border_width": 1,
        }
        self.btn_style = {
            "normal": base_style,
            "hover": {**base_style, "bg_color": (60, 60, 100)},
            "press": {**base_style, "bg_color": arcade.color.BLACK},
            "disabled": base_style
        }

        self.root_layout = arcade.gui.UIAnchorLayout()
        self.ui_manager.add(self.root_layout)

        self.expand_button = arcade.gui.UIFlatButton(text="SETS", width=80, height=30, style=self.btn_style)
        self.expand_button.on_click = self.toggle_expand
        
        self.root_layout.add(
            child=self.expand_button,
            anchor_x="right",
            align_x=-40, 
            anchor_y="top",
            align_y=-15
        )

        # CONTENEDOR PRINCIPAL DE conjuntosS
        self.sets_main_container = arcade.gui.UIBoxLayout(vertical=True, space_between=10)

        self.is_expanded = False
        self.colapsada_height = 60
        self.expandida_height = 120
        self.current_height = self.colapsada_height
        self.target_height = self.colapsada_height
        self.rows_count = 0
        
        self.bg_color = (255, 255, 255, 230) 
        self.border_radius = 20
        
        self.on_resize(window.width, window.height)

    def setup_set_buttons(self, base_sets: dict):
        """ Crea filas de botones manualmente """
        self.sets_main_container.clear()
        
        items = list(base_sets.items())
        self.rows_count = math.ceil(len(items) / 4)
        if self.rows_count < 1: self.rows_count = 1

        current_row_box = None
        
        for i, (set_name, set_data) in enumerate(items):
            # Si es el inicio de una fila creamos una nueva box horizontal
            if i % 4 == 0:
                current_row_box = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
                self.sets_main_container.add(current_row_box)
            
            btn = arcade.gui.UIFlatButton(text=set_name, width=150, height=40, style=self.btn_style)
            def get_handler(d): return lambda e: self.on_set_click(d)
            btn.on_click = get_handler(set_data)
            
            # Añadir el botón a la fila actual
            if current_row_box:
                current_row_box.add(btn)

        self.on_resize(self.window.width, self.window.height)

    def toggle_expand(self, event):
        self.is_expanded = not self.is_expanded
        
        if self.is_expanded:
            # Calcular altura necesaria para la barrita 
            row_height_total = 50 
            self.target_height = 80 + (self.rows_count * row_height_total)
            
            self.expand_button.text = "CERRAR"
            
            self.root_layout.add(
                child=self.sets_main_container,
                anchor_x="center",
                anchor_y="top", 
                align_y=-65 
            )
        else:
            self.target_height = self.colapsada_height
            self.expand_button.text = "SETS"
            self.root_layout.remove(self.sets_main_container)

    def on_update(self, delta_time):
        diff = self.target_height - self.current_height
        if abs(diff) > 0.5: self.current_height += diff * 0.2

    def on_resize(self, width, height):
        self.width = min(width * 0.95, 1200)
        self.center_x = width / 2
        
        margin_side = (width - self.width) / 2
        if margin_side < 0: margin_side = 0
        
        # Padding  para que nada se salga de la barra 
        self.root_layout.padding = (0, margin_side, 0, margin_side)
        
        self.ui_manager.on_resize(width, height)

    def draw(self):
        # Fondo
        cy = self.window.height - (self.current_height / 2) - 10
        points = get_rounded_rect_points(self.center_x, cy, self.width, self.current_height, self.border_radius)
        arcade.draw_polygon_filled(points, self.bg_color)
        
        # UI
        self.ui_manager.draw()

    def close_menu(self):
        if self.is_expanded:
            self.is_expanded = False
            self.target_height = self.colapsada_height
            self.expand_button.text = "SETS"
            if self.sets_main_container in self.root_layout.children:
                self.root_layout.remove(self.sets_main_container)

    # Eventos
    def on_mouse_press(self, x, y, button, modifiers): return self.ui_manager.on_mouse_press(x, y, button, modifiers)
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers): return self.ui_manager.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
    def on_mouse_release(self, x, y, button, modifiers): return self.ui_manager.on_mouse_release(x, y, button, modifiers)
    def on_key_press(self, s, m): pass
    def on_key_release(self, s, m): pass