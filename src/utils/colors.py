"""
Utilidades para generar colores bonitos y visibles.
"""
import random
import colorsys


def generate_beautiful_color():
    """
    Genera un color aleatorio bonito y visible usando HSV.
    Retorna (R, G, B) en rango 0-255.
    """
    # Hue aleatorio (0-1 para todo el espectro)
    hue = random.random()
    
    # Saturación alta para colores vibrantes (70-95%)
    saturation = 0.7 + random.random() * 0.25
    
    # Valor medio-alto para visibilidad (60-85%)
    value = 0.6 + random.random() * 0.25
    
    # Convertir HSV a RGB
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    
    # Convertir a rango 0-255
    return (int(r * 255), int(g * 255), int(b * 255))
