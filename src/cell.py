import arcade
import math
import random

class Cell:
    def __init__(self, x, y, radius, col, name, count):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = col
        self.name = name
        self.count = count

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
        self.time = 0.0

        font_size = int(self.radius * 0.25)
        if font_size < 10: font_size = 10
        
        self.text_object = arcade.Text(
            text=f"{self.name}\n{self.count}",
            x=self.x,
            y=self.y,
            color=arcade.color.BLACK,
            font_size=font_size,
            font_name=("calibri", "arial"),
            anchor_x="center",
            anchor_y="center",
            align="center",
            bold=True
        )

    def draw(self):
        self.time += 0.05
        t = self.time + self.phase_offset
        step = 0.25 
        wobble_amount = 1.5 
        vertices = []
        angle = 0
        while angle < 2 * math.pi:
            ca = math.cos(angle)
            sa = math.sin(angle)
            noise = math.sin(angle * 5 + t) * wobble_amount
            stretch = (self.stretch_vel_x * ca) + (self.stretch_vel_y * sa)
            r = self.radius + noise + stretch
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

        self.text_object.draw()

    def update(self, world_mouse_x, world_mouse_y):
        self.prev_x = self.x
        self.prev_y = self.y

        if self.is_dragging:
            self.x = world_mouse_x - self.offset_x
            self.y = world_mouse_y - self.offset_y
        else:
            self.x += self.physics_vel_x
            self.y += self.physics_vel_y
            self.physics_vel_x *= 0.90
            self.physics_vel_y *= 0.90

        # Actualizar posición del texto
        self.text_object.x = self.x
        self.text_object.y = self.y

        instant_vel_x = self.x - self.prev_x
        instant_vel_y = self.y - self.prev_y
        self.stretch_vel_x += (instant_vel_x - self.stretch_vel_x) * 0.15
        self.stretch_vel_y += (instant_vel_y - self.stretch_vel_y) * 0.15

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

    def stop_drag(self):
        self.is_dragging = False
        self.physics_vel_x = self.stretch_vel_x
        self.physics_vel_y = self.stretch_vel_y