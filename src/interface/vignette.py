import arcade

class Vignette:
    def __init__(self, width: int, height: int, color: tuple):
        self.width = width
        self.height = height
        self.color = color
        self.shape_list = None
        
        # Grosor del desvanecimiento (15% de la pantalla)
        self.thickness_x = int(width * 0.15)
        self.thickness_y = int(height * 0.15)
        
        self.refresh()

    def refresh(self):
        self.shape_list = arcade.shape_list.ShapeElementList()
        
        r, g, b = self.color[:3]

        c_solid = (r, g, b, 255)
        c_trans = (r, g, b, 0)
        
        w = self.width
        h = self.height
        tx = self.thickness_x
        ty = self.thickness_y

        
        # top
        p_top = [
            (0, h - ty),  # BL
            (w, h - ty),  # BR
            (w, h),       # TR
            (0, h)        # TL
        ]
        c_top = [c_trans, c_trans, c_solid, c_solid]
        shape_top = arcade.shape_list.create_rectangle_filled_with_colors(p_top, c_top)
        self.shape_list.append(shape_top)

        # abajo
        p_bot = [
            (0, 0),       # BL
            (w, 0),       # BR
            (w, ty),      # TR
            (0, ty)       # TL
        ]
        c_bot = [c_solid, c_solid, c_trans, c_trans]
        shape_bot = arcade.shape_list.create_rectangle_filled_with_colors(p_bot, c_bot)
        self.shape_list.append(shape_bot)

        # izq
        p_left = [
            (0, 0),       # BL
            (tx, 0),      # BR
            (tx, h),      # TR
            (0, h)        # TL
        ]
        c_left = [c_solid, c_trans, c_trans, c_solid]
        shape_left = arcade.shape_list.create_rectangle_filled_with_colors(p_left, c_left)
        self.shape_list.append(shape_left)

        # der
        p_right = [
            (w - tx, 0),  # BL
            (w, 0),       # BR
            (w, h),       # TR
            (w - tx, h)   # TL
        ]
        c_right = [c_trans, c_solid, c_solid, c_trans]
        shape_right = arcade.shape_list.create_rectangle_filled_with_colors(p_right, c_right)
        self.shape_list.append(shape_right)

    def resize(self, width, height):
        self.width = width
        self.height = height
        self.thickness_x = int(width * 0.15)
        self.thickness_y = int(height * 0.15)
        self.refresh()

    def draw(self):
        if self.shape_list:
            self.shape_list.draw()