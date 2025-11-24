import arcade
import arcade.gui
from src.interface.ui_helpers import get_rounded_rect_points
import math

# Constantes de Operación
OP_INTERSECT = "INTERSECT"
OP_DIFFERENCE = "DIFFERENCE"
OP_UNION = "UNION"

class TopBar:
    def __init__(self, window: arcade.Window, on_set_click_callback, on_op_change_callback):
        self.window = window
        self.on_set_click = on_set_click_callback
        self.on_op_change = on_op_change_callback

        self.ui_manager = arcade.gui.UIManager(window=self.window)
        self.ui_manager.enable()

        # --- 1. ESTILO AZUL (No seleccionado) ---
        style_blue = {
            "font_name": ("calibri", "arial"),
            "font_size": 12,
            "font_color": arcade.color.WHITE,
            "bg_color": (40, 40, 80), 
            "border_color": arcade.color.WHITE,
            "border_width": 1,
        }
        
        self.btn_style = {
            "normal": style_blue,
            "hover": {**style_blue, "bg_color": (60, 60, 100)}, # Azul más claro
            "press": {**style_blue, "bg_color": arcade.color.BLACK},
            "disabled": style_blue
        }
        
        # --- 2. ESTILO VERDE (Seleccionado) ---
        # Definimos un estilo base verde
        style_green = {
            "font_name": ("calibri", "arial"),
            "font_size": 12,
            "font_color": arcade.color.WHITE,
            "bg_color": arcade.color.FOREST_GREEN, 
            "border_color": arcade.color.LIGHT_GREEN,
            "border_width": 2, # Borde más grueso para destacar
        }

        # ¡IMPORTANTE! Aplicamos el verde a NORMAL, HOVER y PRESS
        # Así se mantendrá verde aunque pases el mouse por encima
        self.active_style = {
            "normal": style_green,
            "hover": {**style_green, "bg_color": arcade.color.KELLY_GREEN}, # Verde más claro al pasar mouse
            "press": {**style_green, "bg_color": arcade.color.DARK_GREEN},
            "disabled": style_green
        }

        self.root_layout = arcade.gui.UIAnchorLayout()
        self.ui_manager.add(self.root_layout)

        # --- 3. BOTONES ---
        self.tools_box = arcade.gui.UIBoxLayout(vertical=False, space_between=5)

        self.btn_intersect = arcade.gui.UIFlatButton(text="∩", width=40, height=30, style=self.btn_style)
        self.btn_intersect.on_click = lambda e: self.set_operation(OP_INTERSECT)
        
        self.btn_union = arcade.gui.UIFlatButton(text="∪", width=40, height=30, style=self.btn_style)
        self.btn_union.on_click = lambda e: self.set_operation(OP_UNION)
        
        self.btn_difference = arcade.gui.UIFlatButton(text="-", width=40, height=30, style=self.btn_style)
        self.btn_difference.on_click = lambda e: self.set_operation(OP_DIFFERENCE)

        self.tools_box.add(self.btn_intersect)
        self.tools_box.add(self.btn_union)
        self.tools_box.add(self.btn_difference)

        self.root_layout.add(
            child=self.tools_box,
            anchor_x="left",
            align_x=40, 
            anchor_y="top",
            align_y=-15
        )

        self.expand_button = arcade.gui.UIFlatButton(text="SETS", width=80, height=30, style=self.btn_style)
        self.expand_button.on_click = self.toggle_expand
        
        self.root_layout.add(
            child=self.expand_button,
            anchor_x="right",
            align_x=-40, 
            anchor_y="top",
            align_y=-15
        )

        # CONTENEDOR PRINCIPAL
        self.sets_main_container = arcade.gui.UIBoxLayout(vertical=True, space_between=10)

        self.current_op = OP_INTERSECT
        self.is_expanded = False
        self.colapsada_height = 60
        self.current_height = self.colapsada_height
        self.target_height = self.colapsada_height
        self.rows_count = 0
        
        self.bg_color = (255, 255, 255, 230) 
        self.border_radius = 20
        
        # Seleccionar inicial
        self.set_operation(OP_INTERSECT)
        self.on_resize(window.width, window.height)

    def set_operation(self, op):
        """ Cambia operación y actualiza estilos visuales """
        self.current_op = op
        self.on_op_change(op)

        # Resetear todos a azul
        self.btn_intersect.style = self.btn_style
        self.btn_union.style = self.btn_style
        self.btn_difference.style = self.btn_style

        # Poner verde el activo
        if op == OP_INTERSECT:
            self.btn_intersect.style = self.active_style
        elif op == OP_UNION:
            self.btn_union.style = self.active_style
        elif op == OP_DIFFERENCE:
            self.btn_difference.style = self.active_style
            
        # Forzar actualización visual del Manager
        # Esto es clave para que el cambio se vea al instante
        self.ui_manager.trigger_render()

    def setup_set_buttons(self, base_sets: dict):
        self.sets_main_container.clear()
        items = list(base_sets.items())
        self.rows_count = math.ceil(len(items) / 4)
        if self.rows_count < 1: self.rows_count = 1

        current_row_box = None
        for i, (set_name, set_data) in enumerate(items):
            if i % 4 == 0:
                current_row_box = arcade.gui.UIBoxLayout(vertical=False, space_between=10)
                self.sets_main_container.add(current_row_box)
            
            btn = arcade.gui.UIFlatButton(text=set_name, width=150, height=40, style=self.btn_style)
            def get_handler(d): return lambda e: self.on_set_click(d)
            btn.on_click = get_handler(set_data)
            
            if current_row_box:
                current_row_box.add(btn)

        self.on_resize(self.window.width, self.window.height)

    def toggle_expand(self, event):
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            row_height_total = 50 
            self.target_height = 80 + (self.rows_count * row_height_total)
            self.expand_button.text = "CERRAR"
            self.root_layout.add(child=self.sets_main_container, anchor_x="center", anchor_y="top", align_y=-65)
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
        self.root_layout.padding = (0, margin_side, 0, margin_side)
        self.ui_manager.on_resize(width, height)

    def draw(self):
        cy = self.window.height - (self.current_height / 2) - 10
        points = get_rounded_rect_points(self.center_x, cy, self.width, self.current_height, self.border_radius)
        arcade.draw_polygon_filled(points, self.bg_color)
        self.ui_manager.draw()

    def close_menu(self):
        if self.is_expanded: self.toggle_expand(None)

    # Eventos
    def on_mouse_press(self, x, y, button, modifiers): return self.ui_manager.on_mouse_press(x, y, button, modifiers)
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers): return self.ui_manager.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
    def on_mouse_release(self, x, y, button, modifiers): return self.ui_manager.on_mouse_release(x, y, button, modifiers)
    def on_key_press(self, s, m): pass
    def on_key_release(self, s, m): pass