import arcade
import math
import random

class Cell:
    def __init__(self, x, y, radius, col, name, count, data=None, **kwargs):
        self.x = x
        self.y = y
        
        # Calcular tamaño basado en count con mínimo de 60
        min_radius = 60
        max_radius = 150
        # Escala logarítmica para mejor distribución visual
        if count > 0:
            scale = math.log(count + 1) / math.log(1000)  # Normalizado para counts hasta ~1000
            calculated_radius = min_radius + (max_radius - min_radius) * scale
            self.radius = max(min_radius, min(calculated_radius, max_radius))
        else:
            self.radius = min_radius
            
        self.target_radius = self.radius
        self.color = col
        self.name = name
        self.count = count
        self.data = data if data is not None else set()
        self.parents = kwargs.get('parents', [])
        self.operation = kwargs.get('operation', None)

        #animacion
        self.current_radius = 0.1 
        self.scale_speed = 0.0

        # Colores
        r, g, b = self.color
        self.dark_color = (int(r * 0.7), int(g * 0.7), int(b * 0.7))
        
        self.phase_offset = random.uniform(0, 100)
        self.is_dragging = False
        self.offset_x = 0
        self.offset_y = 0
        self.prev_x = x
        self.prev_y = y
        self.stretch_vel_x = 0.0
        self.stretch_vel_y = 0.0
        self.physics_vel_x = 0.0
        self.physics_vel_y = 0.0
        self.drag_vel_x = 0.0
        self.drag_vel_y = 0.0
        self.time = 0.0

        self.excitation_level = 0.0 # 0.0 a 1.0

        # Tamaño de fuente proporcional al radio
        font_size = int(self.target_radius * 0.22)
        if font_size < 10: font_size = 10
        
        # Crear dos objetos de texto separados para mejor separación visual
        self.name_text = arcade.Text(
            text=self.name,
            x=self.x,
            y=self.y + font_size * 0.6,  # Arriba
            color=arcade.color.BLACK,
            font_size=font_size,
            font_name=("calibri", "arial"),
            anchor_x="center",
            anchor_y="center",
            align="center",
            bold=True
        )
        
        self.count_text = arcade.Text(
            text=str(self.count),
            x=self.x,
            y=self.y - font_size * 0.6,  # Abajo
            color=arcade.color.BLACK,
            font_size=int(font_size * 0.9),  # Ligeramente más pequeño
            font_name=("calibri", "arial"),
            anchor_x="center",
            anchor_y="center",
            align="center",
            bold=True
        )

    def draw(self):

        if self.current_radius < 1: return

        # Interpolación dinámica basada en excitación
        base_speed = 0.05
        max_speed = 0.4 # Más rápido si está muy cerca
        speed = base_speed + (max_speed - base_speed) * self.excitation_level
        
        base_wobble = 1.5
        max_wobble = 6.0 # Más deformación
        wobble_base = base_wobble + (max_wobble - base_wobble) * self.excitation_level

        self.time += speed
        t = self.time + self.phase_offset
        step = 0.25 
        vertices = []
        angle = 0
        while angle < 2 * math.pi:
            ca = math.cos(angle)
            sa = math.sin(angle)
            noise = math.sin(angle * 5 + t) * wobble_base
            stretch = (self.stretch_vel_x * ca) + (self.stretch_vel_y * sa)
            r = self.current_radius + noise + stretch
            vx = self.x + r * ca
            vy = self.y + r * sa
            vertices.append((vx, vy))
            angle += step

        if vertices:
            arcade.draw_polygon_filled(vertices, self.dark_color)
            inner_vertices = []
            border_ratio = 0.88
            for vx, vy in vertices:
                ivx = self.x + (vx - self.x) * border_ratio
                ivy = self.y + (vy - self.y) * border_ratio
                inner_vertices.append((ivx, ivy))
            arcade.draw_polygon_filled(inner_vertices, self.color)

        if self.current_radius > self.target_radius * 0.5:
            self.name_text.draw()
            self.count_text.draw()

    def update(self, world_mouse_x, world_mouse_y):

        # logica animacion
        if self.current_radius < self.target_radius:
            # Fuerza del resorte hacia el tamaño objetivo
            force = (self.target_radius - self.current_radius) * 0.1
            self.scale_speed += force
            self.scale_speed *= 0.8 # Amortiguación
            self.current_radius += self.scale_speed
        #-----------------


        self.prev_x = self.x
        self.prev_y = self.y

        if self.is_dragging:
            self.x = world_mouse_x - self.offset_x
            self.y = world_mouse_y - self.offset_y
            
            # Calculate drag velocity for inertia
            self.drag_vel_x = self.x - self.prev_x
            self.drag_vel_y = self.y - self.prev_y
        else:
            self.x += self.physics_vel_x
            self.y += self.physics_vel_y
            self.physics_vel_x *= 0.90 # Increased friction (was 0.92)
            self.physics_vel_y *= 0.90

        # Actualizar posición de ambos textos
        font_size = self.name_text.font_size
        self.name_text.x = self.x
        self.name_text.y = self.y + font_size * 0.6
        self.count_text.x = self.x
        self.count_text.y = self.y - font_size * 0.6

        instant_vel_x = self.x - self.prev_x
        instant_vel_y = self.y - self.prev_y
        self.stretch_vel_x += (instant_vel_x - self.stretch_vel_x) * 0.15
        self.stretch_vel_y += (instant_vel_y - self.stretch_vel_y) * 0.15

        self.excitation_level = 0.0

    def is_mouse_over(self, world_mouse_x, world_mouse_y):
        dx = self.x - world_mouse_x
        dy = self.y - world_mouse_y
        return (dx*dx + dy*dy) < (self.radius * self.radius)

    def start_drag(self, world_mouse_x, world_mouse_y):
        self.is_dragging = True
        self.offset_x = world_mouse_x - self.x
        self.offset_y = world_mouse_y - self.y
        self.physics_vel_x = 0
        self.physics_vel_y = 0
        self.drag_vel_x = 0
        self.drag_vel_y = 0

    def stop_drag(self):
        self.is_dragging = False
        # Apply inertia (dampened)
        self.physics_vel_x = self.drag_vel_x * 0.5
        self.physics_vel_y = self.drag_vel_y * 0.5

    def get_base_ancestors(self):
        if not self.parents:
            return {self}
        
        ancestors = set()
        for parent in self.parents:
            ancestors.update(parent.get_base_ancestors())
        return ancestors
    
    def get_formula_string(self):
        """Genera la fórmula recursiva completa de esta célula."""
        if not self.parents:
            return self.name  # Caso base
        
        # Mapeo de operaciones a símbolos
        OP_MAP = {
            0: "∩",  # OP_INTERSECT
            1: "∪",  # OP_UNION
            2: "-",  # OP_DIFFERENCE
            "INTERSECT": "∩",
            "UNION": "∪",
            "DIFFERENCE": "-",
            "intersect": "∩",
            "union": "∪",
            "difference": "-",
        }
        
        p1_formula = self.parents[0].get_formula_string()
        p2_formula = self.parents[1].get_formula_string() if len(self.parents) > 1 else "?"
        symbol = OP_MAP.get(self.operation, str(self.operation))
        
        return f"({p1_formula} {symbol} {p2_formula})"