import arcade

def draw_grid(camera: arcade.Camera2D, screen_width: int, screen_height: int, pixel_ratio: float = 1.0):
    """
    Dibuja el grid
    pixel_ratio: Multiplicador para el grosor de línea basado en la resolución.
    """
    grid_spacing = 40
    grid_color = (240, 240, 240, 255)
    
    target_pixel_width = 1 * pixel_ratio
    calculated_thickness = target_pixel_width / camera.zoom
    
    # Grosor mínimo también escalado
    line_thickness = max(1.5 * pixel_ratio, calculated_thickness)

    # Límites visibles
    min_world_pos = camera.unproject((0, 0))
    left_x, bottom_y = min_world_pos[0], min_world_pos[1]

    max_world_pos = camera.unproject((screen_width, screen_height))
    right_x, top_y = max_world_pos[0], max_world_pos[1]

    # Snapping
    first_x = (int(left_x) // grid_spacing) * grid_spacing
    first_y = (int(bottom_y) // grid_spacing) * grid_spacing
    
    point_list = []

    # Verticales
    current_x = first_x
    while current_x < right_x + grid_spacing:
        point_list.append((current_x, bottom_y))
        point_list.append((current_x, top_y))
        current_x += grid_spacing

    # Horizontales
    current_y = first_y
    while current_y < top_y + grid_spacing:
        point_list.append((left_x, current_y))
        point_list.append((right_x, current_y))
        current_y += grid_spacing

    # Dibujar
    line_count = 0
    if point_list:
        arcade.draw_lines(point_list, grid_color, line_thickness)
        line_count = len(point_list) // 2
        
    return line_count