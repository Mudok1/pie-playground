import arcade
import math

def get_rounded_rect_points(center_x, center_y, width, height, radius, num_segments=10):
    """
    Genera una lista de puntos (vértices) para un
    polígono de rectángulo redondeado.
    """
    half_width = width / 2
    half_height = height / 2

    # Centros de los arcos de las esquinas
    tr_cx = center_x + half_width - radius  # Top-Right
    tr_cy = center_y + half_height - radius
    tl_cx = center_x - half_width + radius  # Top-Left
    tl_cy = center_y + half_height - radius
    bl_cx = center_x - half_width + radius  # Bottom-Left
    bl_cy = center_y - half_height + radius
    br_cx = center_x + half_width - radius  # Bottom-Right
    br_cy = center_y - half_height + radius

    point_list = []
    
    # Arco superior derecho (0 a 90 grados)
    for i in range(num_segments + 1):
        angle = math.radians(i * (90 / num_segments))
        x = tr_cx + math.cos(angle) * radius
        y = tr_cy + math.sin(angle) * radius
        point_list.append((x, y))
        
    # Arco superior izquierdo (90 a 180 grados)
    for i in range(num_segments + 1):
        angle = math.radians(90 + i * (90 / num_segments))
        x = tl_cx + math.cos(angle) * radius
        y = tl_cy + math.sin(angle) * radius
        point_list.append((x, y))

    # Arco inferior izquierdo (180 a 270 grados)
    for i in range(num_segments + 1):
        angle = math.radians(180 + i * (90 / num_segments))
        x = bl_cx + math.cos(angle) * radius
        y = bl_cy + math.sin(angle) * radius
        point_list.append((x, y))
        
    # Arco inferior derecho (270 a 360 grados)
    for i in range(num_segments + 1):
        angle = math.radians(270 + i * (90 / num_segments))
        x = br_cx + math.cos(angle) * radius
        y = br_cy + math.sin(angle) * radius
        point_list.append((x, y))
        
    return point_list