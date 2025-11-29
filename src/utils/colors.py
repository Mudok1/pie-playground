"""
utilidades para colores bonitos
"""
import random
import colorsys


def generate_beautiful_color():
    """
    genera color aleatorio bonito con hsv
    retorna rgb 0-255
    """
    # hue aleatorio
    hue = random.random()
    
    # saturacion alta para que vibre
    saturation = 0.6 + random.random() * 0.3
    
    # valor alto para que se vea bien
    value = 0.8 + random.random() * 0.2
    
    # hsv a rgb
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    
    # a rango 0-255
    return (int(r * 255), int(g * 255), int(b * 255))
