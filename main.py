import arcade
import math
import random
from src.cell import Cell
from src.interface.grid import draw_grid 
from src.interface.vignette import Vignette
from src.interface.top_bar import TopBar, OP_INTERSECT, OP_DIFFERENCE, OP_UNION
from src.base_sets.set_calculator import get_titanic_sets
from src.utils.colors import generate_beautiful_color
from src.utils.passenger_display import print_passenger_details
from src.interface.inspection_ui import InspectionUI
from arcade.types import LBWH

DESIGN_HEIGHT = 720 
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "pie-playground"

EMBARKED_MAP = {
    'C': 'Cherbourg',
    'Q': 'Queenstown',
    'S': 'Southampton'
}

class PiePlayground(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, resizable=True, samples=4)
        
        self.set_minimum_size(854, 480)

        arcade.enable_timings() 
        self.lines_drawn_last_frame = 0
        self.time_since_last_print = 0.0

        self.total_time = 0.0
        self.pixel_ratio = 1.0
        
        self.cells = []
        self.base_sets = {}
        self.passenger_lookup = {}
        
        self.camera = arcade.Camera2D()
        self.min_zoom = 0.5
        self.max_zoom = 3.0
        self.dragging_cell = None
        self.is_panning = False

        self.mouse_x = 0
        self.mouse_y = 0

        self.current_operation = OP_INTERSECT

        # Inspection Mode
        self.is_inspecting = False
        self.inspected_cell = None
        
        # Camera Targets (Initialized to current)
        self.camera_target_pos = self.camera.position
        self.camera_target_zoom = 1.0
        self.camera_original_pos = self.camera.position
        self.camera_original_zoom = 1.0

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
                set_data['count'],
                set_data.get('data', set())
            )
            self.cells.append(new_cell)
            print(f"Celula creada: {set_data['name']}")
            
            # Use utility function for printing
            print_passenger_details(
                set_data.get('data', set()),
                self.passenger_lookup,
                EMBARKED_MAP,
                f"Datos"
            )

        def _op_change_callback(new_op):
            self.current_operation = new_op
            print(f"Operación cambiada a: {new_op}")


        self.top_bar = TopBar(self, on_set_click_callback=_create_cell_callback, on_op_change_callback=_op_change_callback)
        
        # Inspection UI
        self.inspection_ui = InspectionUI(self, on_close_callback=self.exit_inspection_mode)
        self.inspection_ui.disable()  # Start disabled
        
        arcade.set_background_color(self.bg_color)

    def setup(self):
        self.cells.append(Cell(200, 300, 80, (255, 100, 100), "Mujeres", 240))
        self.cells.append(Cell(400, 300, 90, (100, 100, 255), "1ra Clase", 120))
        self.base_sets['Set Prueba 1'] = {'count': 100, 'color': (255, 0, 0), 'name': "Set Prueba 1"}
        self.base_sets['Set Prueba 2'] = {'count': 200, 'color': (0, 0, 255), 'name': "Set Prueba 2"}
        
        # Merge Titanic sets
        titanic_sets, passenger_lookup = get_titanic_sets()
        self.base_sets.update(titanic_sets)
        self.passenger_lookup = passenger_lookup
        
        self.top_bar.setup_set_buttons(self.base_sets)
        self.camera.viewport = LBWH(left=0, bottom=0, width=self.width, height=self.height)
        self.on_resize(self.width, self.height)

    def on_draw(self):
        self.clear() 
        
        with self.camera.activate():
            self.lines_drawn_last_frame = draw_grid(self.camera, self.width, self.height, self.pixel_ratio)
            self.draw_link()
            for cell in self.cells: cell.draw()

        #UI
        self.default_camera.use()
        self.vignette.draw()
        
        if not self.is_inspecting:
            self.top_bar.draw()
        else:
            self.inspection_ui.draw()
            
        self.fps_text_object.draw()

    def on_update(self, delta_time: float):

        self.total_time += delta_time
        # --- DEBUG 
        self.time_since_last_print += delta_time
        if self.time_since_last_print >= 2.0: # Cada 2 segundo
            fps = arcade.get_fps()
            print(f"DEBUG INFO FPS: {fps:.1f} | Líneas Grid: {self.lines_drawn_last_frame} | Células: {len(self.cells)}")
            self.fps_text_object.text = f"FPS: {fps:.0f}"
            self.time_since_last_print = 0.0

        # Update vignette for transitions
        self.vignette.update(delta_time)

        # Camera transitions (Always active for smooth feel)
        # Smooth camera lerp
        current_pos = self.camera.position
        target_pos = self.camera_target_pos
        diff_x = target_pos[0] - current_pos[0]
        diff_y = target_pos[1] - current_pos[1]
        
        # Only lerp if significant difference (stops jitter)
        if abs(diff_x) > 0.5 or abs(diff_y) > 0.5:
            self.camera.position = (
                current_pos[0] + diff_x * 0.1,
                current_pos[1] + diff_y * 0.1
            )
        
        # Smooth zoom lerp
        zoom_diff = self.camera_target_zoom - self.camera.zoom
        if abs(zoom_diff) > 0.001:
            self.camera.zoom += zoom_diff * 0.1

        # Only update physics if not inspecting
        if not self.is_inspecting:
            w_pos = self.camera.unproject((self.mouse_x, self.mouse_y))
            wx, wy = w_pos[0], w_pos[1]
    
            for cell in self.cells: cell.update(wx, wy)
    
            self.update_collisions_and_merge()
    
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
        self.inspection_ui.on_resize(width, height)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        self.mouse_x = x
        self.mouse_y = y

        # If in inspection mode, handle inspection UI
        if self.is_inspecting:
            if self.inspection_ui.on_mouse_press(x, y, button, modifiers):
                return
            # Click outside inspection UI exits inspection mode
            self.exit_inspection_mode()
            return

        #  Si click  en la UI
        if self.top_bar.on_mouse_press(x, y, button, modifiers): 
            return

        # Si click FUERA de la UI:
        if self.top_bar.is_expanded:
            self.top_bar.close_menu()
        
        w_pos = self.camera.unproject((x, y))
        wx, wy = w_pos[0], w_pos[1]
        
        # Right-click (button 4 or arcade.MOUSE_BUTTON_RIGHT) to enter inspection mode
        if button == arcade.MOUSE_BUTTON_RIGHT:
            for cell in reversed(self.cells):
                if cell.is_mouse_over(wx, wy):
                    self.enter_inspection_mode(cell)
                    return

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

        if self.is_inspecting:
            self.inspection_ui.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
            return

        if self.top_bar.on_mouse_drag(x, y, dx, dy, buttons, modifiers): return
        
        if self.is_panning and not self.dragging_cell:
            scale = 1 / self.camera.zoom
            cx, cy = self.camera.position
            new_pos = (cx - dx * scale, cy - dy * scale)
            self.camera.position = new_pos
            # Update target so it doesn't snap back
            self.camera_target_pos = new_pos

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if self.is_inspecting:
            self.inspection_ui.on_mouse_release(x, y, button, modifiers)
            return

        self.top_bar.on_mouse_release(x, y, button, modifiers)
        if self.dragging_cell:
            self.dragging_cell.stop_drag()
            self.dragging_cell = None
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
        new_pos = (cx + (x - sx), cy + (y - sy))
        self.camera.position = new_pos
        
        # Update targets
        self.camera_target_zoom = new_zoom
        self.camera_target_pos = new_pos
        
        return False

    def on_key_press(self, symbol, modifiers):
        # ESC to exit inspection mode
        if symbol == arcade.key.ESCAPE and self.is_inspecting:
            self.exit_inspection_mode()

    def on_key_release(self, s, m): pass

    def draw_link(self):
        # Recorremos para ver cercanía (solo efectos visuales)
        # Optimización: No comprobar todos con todos si son muchos, pero para <50 está bien.
        
        for i, cell_a in enumerate(self.cells):
            for j in range(i + 1, len(self.cells)):
                cell_b = self.cells[j]
                
                dist = math.dist((cell_a.x, cell_a.y), (cell_b.x, cell_b.y))
                # Distancia para activar el efecto visual (un poco lejos)
                visual_threshold = (cell_a.target_radius + cell_b.target_radius) * 2.0
                
                if dist < visual_threshold:
                    # 1. Activar vibración en AMBAS células (variable según distancia)
                    # Intensity 0 a 1
                    intensity = 1 - (dist / visual_threshold) 
                    
                    # Actualizamos el nivel de excitación (tomamos el máximo para no sobrescribir si ya está más excitada por otra)
                    cell_a.excitation_level = max(cell_a.excitation_level, intensity)
                    cell_b.excitation_level = max(cell_b.excitation_level, intensity)
                    
                    # 2. Dibujar línea "eléctrica"
                    # Más gruesa cuanto más cerca
                    width = intensity * 8 * self.pixel_ratio
                    
                    pulse = (math.sin(self.total_time * 20) + 1) * 0.5 # 0 a 1 rápido
                    alpha = int(intensity * 200 * pulse) + 50
                    
                    #Color según operación
                    if self.current_operation == OP_INTERSECT:
                        color = (50, 50, 50, alpha) # Gris oscuro
                    elif self.current_operation == OP_UNION:
                        color = (50, 100, 200, alpha) # Azul
                    else:  # DIFFERENCE
                        color = (220, 50, 50, alpha) # Rojo
                    
                    if width > 1:
                        arcade.draw_line(cell_a.x, cell_a.y, cell_b.x, cell_b.y, color, width)


    def update_collisions_and_merge(self):
        """ 
        Detecta colisiones y fusiona. 
        """

        cells_to_remove = []
        cells_to_add = []
        processed_indices = set() # Para no procesar la misma pareja dos veces

        for i, cell_a in enumerate(self.cells):
            if i in processed_indices: continue
            
            for j in range(i + 1, len(self.cells)):
                if j in processed_indices: continue
                
                cell_b = self.cells[j]
                
                dist = math.dist((cell_a.x, cell_a.y), (cell_b.x, cell_b.y))
                # Umbral de fusión (tienen que solaparse un poco)
                merge_threshold = (cell_a.target_radius + cell_b.target_radius) * 0.6
                
                if dist < merge_threshold:
                    # --- FUSIÓN DETECTADA ---
                    
                    # Calcular datos de la nueva célula
                    mid_x = (cell_a.x + cell_b.x) / 2
                    mid_y = (cell_a.y + cell_b.y) / 2
                    
                    # Color aleatorio vibrante
                    new_color = generate_beautiful_color()
                    
                    # Símbolo de operación
                    if self.current_operation == OP_INTERSECT:
                        op_symbol = "∩"
                    elif self.current_operation == OP_UNION:
                        op_symbol = "∪"
                    else:
                        op_symbol = "-"
                    
                    new_name = f"{cell_a.name} {op_symbol} {cell_b.name}"
                    
                    # Realizar operación de conjuntos
                    if self.current_operation == OP_INTERSECT:
                        new_data = cell_a.data & cell_b.data
                    elif self.current_operation == OP_UNION:
                        new_data = cell_a.data | cell_b.data
                    else:  # OP_DIFFERENCE
                        new_data = cell_a.data - cell_b.data
                        
                    new_count = len(new_data)
                    
                    # Crear hija
                    child_cell = Cell(mid_x, mid_y, 70, new_color, "Mix", new_count, new_data)
                    child_cell.name = "Set" # Nombre corto visual
                    
                    print(f"Operación {op_symbol} realizada.")
                    
                    # Use utility function for printing
                    print_passenger_details(
                        new_data,
                        self.passenger_lookup,
                        EMBARKED_MAP,
                        "Resultado"
                    )
                    
                    # Conservar un poco de la inercia del choque
                    child_cell.physics_vel_x = (cell_a.physics_vel_x + cell_b.physics_vel_x) * 0.5
                    child_cell.physics_vel_y = (cell_a.physics_vel_y + cell_b.physics_vel_y) * 0.5
                    
                    cells_to_add.append(child_cell)
                    
                    # Marcar padres para borrar
                    cells_to_remove.append(cell_a)
                    cells_to_remove.append(cell_b)
                    processed_indices.add(i)
                    processed_indices.add(j)
                    
                    # Solo una fusión por frame por pareja
                    break

        # Aplicar cambios a la lista principal
        for c in cells_to_remove:
            if c in self.cells:
                self.cells.remove(c)
        
        for c in cells_to_add:
            self.cells.append(c)
    
    def enter_inspection_mode(self, cell):
        """Enter inspection mode for a specific cell"""
        print(f"Entering inspection mode for: {cell.name}")
        self.is_inspecting = True
        self.inspected_cell = cell
        
        # Save current camera state
        self.camera_original_pos = self.camera.position
        self.camera_original_zoom = self.camera.zoom
        
        # Calculate target camera position (upper-left quadrant)
        # Cell should be centered at (width * 0.25, height * 0.75)
        target_screen_x = self.width * 0.25
        target_screen_y = self.height * 0.75
        
        # Camera position is the center of the viewport
        # We want the cell's world position to appear at target screen position
        self.camera_target_pos = (
            cell.x - (target_screen_x - self.width / 2) / 2.0,
            cell.y - (target_screen_y - self.height / 2) / 2.0
        )
        self.camera_target_zoom = 2.0
        
        # Enable dark mode vignette
        self.vignette.set_dark_mode(True)
        
        # Disable top bar, enable inspection UI
        self.inspection_ui.enable()
    
    def exit_inspection_mode(self):
        """Exit inspection mode and return to normal view"""
        if not self.is_inspecting:
            return
        
        print("Exiting inspection mode")
        self.is_inspecting = False
        self.inspected_cell = None
        
        # Restore camera to original position
        self.camera_target_pos = self.camera_original_pos
        self.camera_target_zoom = self.camera_original_zoom
        
        # Disable dark mode vignette
        self.vignette.set_dark_mode(False)
        
        # Disable inspection UI
        self.inspection_ui.disable()

if __name__ == "__main__":
    window = PiePlayground()
    window.setup()
    arcade.run()