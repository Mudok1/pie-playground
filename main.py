import arcade
import math
import random
from src.cell import Cell
from src.interface.grid import draw_grid 
from src.interface.vignette import Vignette
from src.interface.top_bar import TopBar
from arcade.types import LBWH

DESIGN_HEIGHT = 720 
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "pie-playground"

class PiePlayground(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True, samples=4)
        
        self.set_minimum_size(854, 480)

        arcade.enable_timings() 
        self.lines_drawn_last_frame = 0
        self.time_since_last_print = 0.0

        self.pixel_ratio = 1.0
        
        self.cells = []
        self.base_sets = {}
        
        self.camera = arcade.Camera2D()
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        self.dragging_cell = None
        self.is_panning = False

        self.mouse_x = 0
        self.mouse_y = 0


        self.bg_color = arcade.color.WHITE_SMOKE
        self.vignette = Vignette(SCREEN_WIDTH, SCREEN_HEIGHT, self.bg_color)

        self.fps_text_object = arcade.Text(
            text="FPS: 0",
            x=10,
            y=10,
            color=arcade.color.GREEN,
            font_size=14,
            bold=True
        )

        def _create_cell_callback(set_data: dict):
            w_pos = self.camera.unproject((self.width / 2, self.height / 2))
            wx, wy = w_pos[0], w_pos[1]
            
            angle = random.uniform(0, 2 * math.pi)
            radius = 50 * math.sqrt(random.random())
            offset_x = radius * math.cos(angle)
            offset_y = radius * math.sin(angle)

            new_cell = Cell(
                wx + offset_x, 
                wy + offset_y, 
                75, 
                set_data['color'], 
                set_data['name'], 
                set_data['count']
            )
            self.cells.append(new_cell)
            print(f"Celula creada: {set_data['name']}")

        self.top_bar = TopBar(self, on_set_click_callback=_create_cell_callback)
        arcade.set_background_color(self.bg_color)

    def setup(self):
        self.cells.append(Cell(200, 300, 80, (255, 100, 100), "Mujeres", 240))
        self.cells.append(Cell(400, 300, 90, (100, 100, 255), "1ra Clase", 120))
        self.base_sets['Set Prueba 1'] = {'count': 100, 'color': (255, 0, 0), 'name': "Set Prueba 1"}
        self.base_sets['Set Prueba 2'] = {'count': 200, 'color': (0, 0, 255), 'name': "Set Prueba 2"}
        self.top_bar.setup_set_buttons(self.base_sets)
        self.camera.viewport = LBWH(left=0, bottom=0, width=self.width, height=self.height)
        self.on_resize(self.width, self.height)

    def on_draw(self):
        self.clear() 
        
        with self.camera.activate():
            self.lines_drawn_last_frame = draw_grid(self.camera, self.width, self.height, self.pixel_ratio)
            
            for cell in self.cells: cell.draw()

        #UI
        self.default_camera.use()
        self.vignette.draw()
        self.top_bar.draw()
        self.fps_text_object.draw()

    def on_update(self, delta_time: float):

        # --- DEBUG 
        self.time_since_last_print += delta_time
        if self.time_since_last_print >= 2.0: # Cada 2 segundo
            fps = arcade.get_fps()
            print(f"DEBUG INFO FPS: {fps:.1f} | Líneas Grid: {self.lines_drawn_last_frame} | Células: {len(self.cells)}")
            self.fps_text_object.text = f"FPS: {fps:.0f}"
            self.time_since_last_print = 0.0

        w_pos = self.camera.unproject((self.mouse_x, self.mouse_y))
        wx, wy = w_pos[0], w_pos[1]

        for cell in self.cells: cell.update(wx, wy)
        self.top_bar.on_update(delta_time)

    def on_resize(self, width: int, height: int):
        super().on_resize(width, height) 

        self.pixel_ratio = height / DESIGN_HEIGHT
        
        self.camera.viewport = LBWH(
            left=0, 
            bottom=0, 
            width=width, 
            height=height
        )
        
        

        self.vignette.resize(width, height)
        self.top_bar.on_resize(width, height)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.mouse_x = x
        self.mouse_y = y

        #  Si click  en la UI
        if self.top_bar.on_mouse_press(x, y, button, modifiers): 
            return

        # Si click FUERA de la UI:
        
        if self.top_bar.is_expanded:
            self.top_bar.close_menu()
        
        w_pos = self.camera.unproject((x, y))
        wx, wy = w_pos[0], w_pos[1]
        
        self.dragging_cell = None
        for cell in reversed(self.cells):
            if cell.is_mouse_over(wx, wy):
                self.dragging_cell = cell
                cell.start_drag(wx, wy)
                self.is_panning = False
                return 
        
        self.is_panning = True

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        self.mouse_x = x
        self.mouse_y = y

        if self.top_bar.on_mouse_drag(x, y, dx, dy, buttons, modifiers): return
        
        if self.is_panning and not self.dragging_cell:
            scale = 1 / self.camera.zoom
            cx, cy = self.camera.position
            self.camera.position = (cx - dx * scale, cy - dy * scale)

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        self.top_bar.on_mouse_release(x, y, button, modifiers)
        if self.dragging_cell: self.dragging_cell.stop_drag(); self.dragging_cell = None
        self.is_panning = False

    def on_mouse_scroll(self, x: int, y: int, scroll_x: int, scroll_y: int):
        # Actualizar posición por si acaso
        self.mouse_x = x
        self.mouse_y = y

        zoom_factor = 1.1
        if scroll_y > 0: new_zoom = self.camera.zoom * zoom_factor
        else: new_zoom = self.camera.zoom / zoom_factor
        new_zoom = max(self.min_zoom, min(new_zoom, self.max_zoom))
        w_pos = self.camera.unproject((x, y))
        wx, wy = w_pos[0], w_pos[1]
        self.camera.zoom = new_zoom
        s_pos = self.camera.project((wx, wy))
        sx, sy = s_pos[0], s_pos[1]
        cx, cy = self.camera.position
        self.camera.position = (cx + (x - sx), cy + (y - sy))
        return False

    def on_key_press(self, s, m): pass
    def on_key_release(self, s, m): pass

if __name__ == "__main__":
    window = PiePlayground()
    window.setup()
    arcade.run()