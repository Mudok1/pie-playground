import arcade
import arcade.gui
import arcade.shape_list
import math

# constantes de operacion (igual que en main.py y top_bar.py)
OP_INTERSECT = 0
OP_UNION = 1
OP_DIFFERENCE = 2

class InspectionUI:
    def __init__(self, window: arcade.Window, on_close_callback):
        self.window = window
        self.on_close = on_close_callback
        
        self.ui_manager = arcade.gui.UIManager(window)
        self.ui_manager.enable()
        
        # estado de la ui
        self.visible = False
        self.scroll_y = 0
        self.current_cell = None
        
        # object pooling para lista de pasajeros
        self.passenger_data = [] # lista de datos crudos
        self.visible_rows = [] # pool de objetos de texto
        self.pool_size = 30 # suficiente para cubrir la altura de pantalla
        
        self.cached_context_items = [] # lista de stats de contexto
        self.cached_plot_texts = [] # lista de textos para el plot
        
        # boton cerrar
        style_close = {
            "font_name": ("calibri", "arial"),
            "font_size": 12,
            "font_color": arcade.color.WHITE,
            "bg_color": arcade.color.RED,
            "border_color": arcade.color.DARK_RED,
            "border_width": 1,
        }
        
        self.btn_close = arcade.gui.UIFlatButton(text="X", width=30, height=30, style={"normal": style_close, "hover": style_close, "press": style_close})
        self.btn_close.on_click = self._on_close_click
        self.ui_manager.add(self.btn_close)
        
        # rectangulos de layout
        self.left_panel_rect = None # plot + formula
        self.right_panel_rect = None # lista pasajeros + contexto
        self.plot_rect = None
        self.formula_rect = None
        self.list_rect = None
        self.context_rect = None
        
        # textos estaticos (headers)
        self.txt_header_list = arcade.Text("Lista de Pasajeros", 0, 0, arcade.color.BLACK, 14, anchor_x="center", bold=True)
        self.txt_col_name = arcade.Text("Nombre", 0, 0, arcade.color.DARK_GRAY, 10, bold=True)
        self.txt_col_age = arcade.Text("Edad", 0, 0, arcade.color.DARK_GRAY, 10, bold=True, anchor_x="right")
        self.txt_col_class = arcade.Text("Clase", 0, 0, arcade.color.DARK_GRAY, 10, bold=True, anchor_x="right")
        self.txt_col_fare = arcade.Text("Tarifa", 0, 0, arcade.color.DARK_GRAY, 10, bold=True, anchor_x="right")
        self.txt_context_header = arcade.Text("Ingredientes Base", 0, 0, arcade.color.BLACK, 12, bold=True)
        
        # texto de la formula
        self.txt_formula = arcade.Text("", 0, 0, arcade.color.BLACK, 16, anchor_x="left", anchor_y="center", font_name=("consolas", "monaco", "monospace"))
        
        self.on_resize(window.width, window.height)

    def enable(self):
        self.visible = True
        self.ui_manager.enable()
        self.current_cell = None # forzar refresco

    def disable(self):
        self.visible = False
        self.ui_manager.disable()

    def _on_close_click(self, event):
        if self.on_close:
            self.on_close()

    def is_mouse_over(self, x, y):
        """Devuelve True si el mouse esta sobre algun panel de la UI"""
        if not self.visible: return False
        
        # Check left panel
        if self.left_panel_rect:
            lx, ly, lw, lh = self.left_panel_rect
            if lx <= x <= lx + lw and ly <= y <= ly + lh:
                return True
                
        # Check right panel
        if self.right_panel_rect:
            rx, ry, rw, rh = self.right_panel_rect
            if rx <= x <= rx + rw and ry <= y <= ry + rh:
                return True
                
        return False

    def on_resize(self, width, height):
        padding = 20
        
        # split layout: izquierda (60%) / derecha (40%)
        # altura: 85% de pantalla
        total_w = width - (padding * 3) # padding izquierda, medio, derecha
        total_h = height * 0.85
        start_y = (height - total_h) / 2
        
        left_w = total_w * 0.6
        right_w = total_w * 0.4
        
        # panel izquierdo (plot + formula)
        self.left_panel_rect = (padding, start_y, left_w, total_h)
        
        # split panel izquierdo: plot (arriba 80%), formula (abajo 20%)
        plot_h = total_h * 0.8
        formula_h = total_h * 0.2
        self.plot_rect = (padding, start_y + formula_h, left_w, plot_h)
        self.formula_rect = (padding, start_y, left_w, formula_h)
        
        # panel derecho (lista + contexto)
        self.right_panel_rect = (padding * 2 + left_w, start_y, right_w, total_h)
        
        # split panel derecho: lista (arriba 70%), contexto (abajo 30%)
        # tamaño dinamico segun altura ventana
        list_h = total_h * 0.6 # reducido un poco para dar espacio al contexto
        context_h = total_h * 0.4
        
        self.list_rect = (padding * 2 + left_w, start_y + context_h, right_w, list_h)
        self.context_rect = (padding * 2 + left_w, start_y, right_w, context_h)
        
        # posicion boton cerrar (arriba derecha del panel derecho)
        btn_x = (padding * 2 + left_w) + right_w - self.btn_close.width
        btn_y = start_y + total_h + 5
        
        self.ui_manager.clear()
        layout = arcade.gui.UIAnchorLayout()
        layout.add(
            child=self.btn_close,
            anchor_x="left",
            anchor_y="bottom",
            align_x=btn_x,
            align_y=btn_y
        )
        self.ui_manager.add(layout)
        
        # tamaño fuente dinamico para lista
        font_size = max(10, int(height * 0.015))
        self.txt_header_list.font_size = font_size + 2
        
        # inicializar pool de objetos para lista
        self.visible_rows = []
        for _ in range(self.pool_size):
            row_objs = {
                'name': arcade.Text("", 0, 0, arcade.color.BLACK, font_size, anchor_x="left"),
                'age': arcade.Text("", 0, 0, arcade.color.BLACK, font_size, anchor_x="right"),
                'class': arcade.Text("", 0, 0, arcade.color.BLACK, font_size, anchor_x="right"),
                'fare': arcade.Text("", 0, 0, arcade.color.DARK_GREEN, font_size, anchor_x="right")
            }
            self.visible_rows.append(row_objs)
        
        # forzar refresco cache al redimensionar
        self.current_cell = None

    def _update_passenger_cache(self, cell):
        self.passenger_data = [] # guardar solo datos crudos
        if not cell: return
        
        data_list = list(cell.data)
        data_list.sort()
        
        for pid in data_list:
            passenger = self.window.passenger_lookup.get(pid)
            if not passenger: continue
            
            name = passenger.get('Name', 'Unknown')
            age = passenger.get('Age', '?')
            pclass = passenger.get('Pclass', '?')
            fare = passenger.get('Fare', 0.0)
            
            # cortar nombre si > 20 chars
            if len(name) > 20:
                name = name[:20] + "..."
                
            age_str = f"{int(age)}y" if isinstance(age, (int, float)) and not math.isnan(age) else "-"
            class_str = f"{pclass}st" if pclass == 1 else f"{pclass}nd" if pclass == 2 else f"{pclass}rd"
            fare_str = f"£{fare:.1f}"
            
            self.passenger_data.append({
                'name': name,
                'age': age_str,
                'class': class_str,
                'fare': fare_str
            })

    def _update_context_cache(self, cell):
        self.cached_context_items = []
        if not cell: return
        
        # usar get_base_ancestors recursivo
        ancestors = cell.get_base_ancestors()
        
        # si ancestros vacio (no deberia pasar), usar self
        if not ancestors:
            ancestors = {cell}
        
        # Deduplicar por nombre (en caso de que haya múltiples instancias del mismo conjunto base)
        unique_ancestors = {}
        for ancestor in ancestors:
            if ancestor.name not in unique_ancestors:
                unique_ancestors[ancestor.name] = ancestor
        
        # ordenar ancestros por nombre
        sorted_ancestors = sorted(unique_ancestors.values(), key=lambda c: c.name)
        
        max_count = max(c.count for c in sorted_ancestors) if sorted_ancestors else 1
        if max_count == 0: max_count = 1
        
        for ancestor in sorted_ancestors:
            # items layout vertical: nombre, barra, cuenta
            name_text = arcade.Text(ancestor.name, 0, 0, arcade.color.BLACK, 10, anchor_x="left", bold=True)
            count_text = arcade.Text(str(ancestor.count), 0, 0, arcade.color.DARK_GRAY, 10, anchor_x="right")
            
            self.cached_context_items.append({
                'name_text': name_text,
                'count_text': count_text,
                'count': ancestor.count,
                'color': ancestor.color,
                'max_count': max_count
            })

    def draw(self):
        if not self.visible:
            return
            
        def draw_panel_bg(rect, color):
            if not rect: return
            x, y, w, h = rect
            arcade.draw_rect_filled(arcade.types.XYWH(x + w/2, y + h/2, w, h), color)
            arcade.draw_rect_outline(arcade.types.XYWH(x + w/2, y + h/2, w, h), arcade.color.GRAY, 2)

        # dibujar fondos
        draw_panel_bg(self.plot_rect, (250, 250, 250, 240))
        draw_panel_bg(self.formula_rect, (240, 240, 240, 240))
        draw_panel_bg(self.list_rect, (250, 250, 250, 240))
        draw_panel_bg(self.context_rect, (245, 245, 245, 240))
        
        if self.window.inspected_cell:
            cell = self.window.inspected_cell
            
            # ver si cambio celula para reconstruir cache
            if cell != self.current_cell:
                self._update_passenger_cache(cell)
                self._update_context_cache(cell)
                self.current_cell = cell
                # limpiar cache texto plot
                self.cached_plot_texts = [] 
            
            # dibujar contenido
            if self.plot_rect:
                self.draw_upset_plot(self.plot_rect, cell)
                
            if self.formula_rect:
                self.draw_formula(self.formula_rect, cell)
                
            if self.list_rect:
                self.draw_passenger_list(self.list_rect, cell)
                
            if self.context_rect:
                self.draw_context_stats(self.context_rect)

        self.ui_manager.draw()

    def draw_formula(self, rect, cell):
        x, y, w, h = rect
        
        # Generar fórmula recursiva completa
        formula_str = cell.get_formula_string()
        formula_str += f" = {cell.count}"
        
        # Calcular tamaño de fuente basado en longitud y ancho disponible
        # Estimación: cada carácter ocupa aproximadamente 0.6 * font_size píxeles
        available_width = w - 40  # Margen de 20px a cada lado
        estimated_char_width = 0.6
        
        # Calcular font_size ideal
        ideal_font_size = available_width / (len(formula_str) * estimated_char_width)
        # Limitar entre 10 y 16
        font_size = max(10, min(16, int(ideal_font_size)))
        
        self.txt_formula.font_size = font_size
        self.txt_formula.text = formula_str
        self.txt_formula.x = x + 20
        self.txt_formula.y = y + h/2
        self.txt_formula.draw()

    def draw_passenger_list(self, rect, cell):
        x, y, w, h = rect
        
        # header
        self.txt_header_list.x = x + w/2
        self.txt_header_list.y = y + h - 20
        self.txt_header_list.draw()
        
        # layout headers columnas
        # nombre: 65% | edad: 15% | clase: 10% | tarifa: 10%
        col_y = y + h - 45
        
        # anchos
        w_name = w * 0.65
        w_age = w * 0.15
        w_class = w * 0.10
        w_fare = w * 0.10
        
        # posiciones x (anclas)
        # nombre: alineado izq en x + 10
        # otros: alineados der en su limite
        x_name = x + 10
        x_age = x + w_name + w_age
        x_class = x + w_name + w_age + w_class
        x_fare = x + w - 10
        
        self.txt_col_name.x = x_name
        self.txt_col_name.y = col_y
        self.txt_col_name.draw()
        
        self.txt_col_age.x = x_age
        self.txt_col_age.y = col_y
        self.txt_col_age.draw()
        
        self.txt_col_class.x = x_class
        self.txt_col_class.y = col_y
        self.txt_col_class.draw()
        
        self.txt_col_fare.x = x_fare
        self.txt_col_fare.y = col_y
        self.txt_col_fare.draw()
        
        arcade.draw_line(x + 5, col_y - 5, x + w - 5, col_y - 5, arcade.color.LIGHT_GRAY, 1)

        # contenido lista
        line_height = 25
        margin_bottom = 50 
        
        total_content_h = len(self.passenger_data) * line_height
        max_scroll = max(0, total_content_h + margin_bottom - (h - 70))
        self.scroll_y = max(0, min(self.scroll_y, max_scroll))
        
        list_y_start = y + h - 60 + self.scroll_y
        
        # scissor
        try:
            self.window.ctx.scissor = int(x), int(y), int(w), int(h - 50)
        except Exception: pass
        
        # logica object pooling
        # calcular indice inicio segun scroll
        # queremos dibujar filas visibles en y, y+h
        # list_y_start es pos Y del elemento 0
        # row_y = list_y_start - (i * line_height)
        # We need row_y < y + h and row_y > y - line_height
        
        # i * line_height = list_y_start - row_y
        # Max row_y = y + h -> Min i = (list_y_start - (y + h)) / line_height
        # Min row_y = y -> Max i = (list_y_start - y) / line_height
        
        start_index = int((self.scroll_y - 60) / line_height) # Approx
        # iteramos pool y asignamos datos segun scroll
        
        # logica correcta:
        # primer item visible en indice: floor(scroll_y / line_height)
        first_visible_index = int(self.scroll_y // line_height)
        
        for i in range(self.pool_size):
            data_index = first_visible_index + i
            
            if data_index < 0 or data_index >= len(self.passenger_data):
                # sin datos para este slot, ocultar
                for txt in self.visible_rows[i].values():
                    txt.text = ""
                continue
                
            row_data = self.passenger_data[data_index]
            row_y = list_y_start - (data_index * line_height)
            
            # check visibilidad (estricto)
            if row_y < y - line_height or row_y > y + h:
                # fuera de vista
                for txt in self.visible_rows[i].values():
                    txt.text = ""
                continue
            
            # tira
            if data_index % 2 == 0:
                arcade.draw_rect_filled(arcade.types.XYWH(x + w/2, row_y + line_height/2 - 5, w - 10, line_height), (245, 245, 245))
            
            # actualizar y dibujar objetos texto del pool
            row_objs = self.visible_rows[i]
            
            row_objs['name'].text = row_data['name']
            row_objs['name'].x = x_name
            row_objs['name'].y = row_y
            row_objs['name'].draw()
            
            row_objs['age'].text = row_data['age']
            row_objs['age'].x = x_age
            row_objs['age'].y = row_y
            row_objs['age'].draw()
            
            row_objs['class'].text = row_data['class']
            row_objs['class'].x = x_class
            row_objs['class'].y = row_y
            row_objs['class'].draw()
            
            row_objs['fare'].text = row_data['fare']
            row_objs['fare'].x = x_fare
            row_objs['fare'].y = row_y
            row_objs['fare'].draw()
            
            row_objs['fare'].draw()

        try:
            self.window.ctx.scissor = None
        except Exception: pass

    def draw_context_stats(self, rect):
        x, y, w, h = rect
        
        self.txt_context_header.x = x + 10
        self.txt_context_header.y = y + h - 20
        self.txt_context_header.draw()
        
        # layout vertical para items
        # cada item necesita unos 40px altura
        item_height = 40
        start_y = y + h - 50
        
        for i, item in enumerate(self.cached_context_items):
            item_y = start_y - i * (item_height + 10)
            
            # 1. nombre (arriba izq)
            item['name_text'].x = x + 10
            item['name_text'].y = item_y + 10
            item['name_text'].draw()
            
            # 2. barra (medio)
            bar_max_w = w - 60 # dejar espacio para cuenta
            bar_w = (item['count'] / item['max_count']) * bar_max_w
            bar_x = x + 10
            
            # barra fondo (gris claro, 100% ancho)
            arcade.draw_rect_filled(arcade.types.XYWH(bar_x + bar_max_w/2, item_y - 5, bar_max_w, 8), (230, 230, 230))
            
            # barra valor
            arcade.draw_rect_filled(arcade.types.XYWH(bar_x + bar_w/2, item_y - 5, bar_w, 8), item['color'])
            
            # 3. cuenta (abajo der)
            item['count_text'].x = x + w - 10
            item['count_text'].y = item_y - 5
            item['count_text'].draw()

    def draw_upset_plot(self, rect, cell):
        x, y, w, h = rect
        
        shape_list = arcade.shape_list.ShapeElementList()
        
        # necesitamos cachear textos del plot tambien, o recrearlos cada frame (menos eficiente pero ok para pocos items)
        # por simplicidad recreamos objetos texto aqui pero pocos
        # idealmente cachear en _update_plot_cache si va lento
        
        if not cell.parents:
            # --- celula base ---
            cx = x + w/2
            bar_h = h * 0.6
            bar_y = y + h * 0.3 + bar_h/2
            rect_shape = arcade.shape_list.create_rectangle_filled(cx, bar_y, 40, bar_h, cell.color)
            shape_list.append(rect_shape)
            
            arcade.Text(str(cell.count), cx, bar_y + bar_h/2 + 10, arcade.color.BLACK, 12, anchor_x="center", bold=True).draw()
            
            row_y = y + 40
            dot = arcade.shape_list.create_ellipse_filled(cx, row_y, 8, 8, cell.color) # Radius 8
            shape_list.append(dot)
            
            arcade.Text(cell.name, x + 20, row_y, arcade.color.BLACK, 12, anchor_x="left", anchor_y="center").draw()
            
        else:
            # --- celula derivada ---
            p1 = cell.parents[0]
            p2 = cell.parents[1] if len(cell.parents) > 1 else None
            
            cols = [p1]
            if p2: cols.append(p2)
            cols.append(cell)
            
            col_width = w / (len(cols) + 1)
            start_x = x + col_width
            
            max_count = max(c.count for c in cols)
            if max_count == 0: max_count = 1
            
            bars_base_y = y + 100
            bars_max_h = h - 140
            
            row_height = 40
            matrix_base_y = y + 30
            
            # etiquetas matriz
            arcade.Text(p1.name, x + 10, matrix_base_y + row_height, arcade.color.BLACK, 10, anchor_x="left", anchor_y="center").draw()
            if p2:
                arcade.Text(p2.name, x + 10, matrix_base_y, arcade.color.BLACK, 10, anchor_x="left", anchor_y="center").draw()
            
            for i, col_cell in enumerate(cols):
                cx = start_x + i * col_width
                
                is_result = (col_cell == cell)
                
                # logica color:
                # resultado: color completo
                # padres: color padre con alpha 100
                if is_result:
                    color = col_cell.color
                else:
                    r, g, b = col_cell.color
                    color = (r, g, b, 100)
                
                # barra
                bar_h = (col_cell.count / max_count) * bars_max_h
                bar_y = bars_base_y + bar_h/2
                
                rect_shape = arcade.shape_list.create_rectangle_filled(cx, bar_y, 30, bar_h, color)
                shape_list.append(rect_shape)
                
                # cuenta
                arcade.Text(str(col_cell.count), cx, bar_y + bar_h/2 + 5, arcade.color.BLACK, 10, anchor_x="center", bold=True).draw()
                
                # puntos matriz
                y_row_p1 = matrix_base_y + row_height
                y_row_p2 = matrix_base_y
                
                dots_to_draw = []
                if i == 0: dots_to_draw.append(y_row_p1)
                elif i == 1 and p2: dots_to_draw.append(y_row_p2)
                elif is_result:
                    dots_to_draw.append(y_row_p1)
                    if p2: dots_to_draw.append(y_row_p2)
                
                # dibujar puntos (radio 8)
                dot_color = col_cell.color 
                
                for dy in dots_to_draw:
                    # logica visual operaciones
                    is_subtracted = False
                    if cell.operation in [OP_DIFFERENCE, "DIFFERENCE", "difference", "-"]:
                        # si es segundo padre o segundo punto columna resultado
                        # espera, para columna resultado queremos mostrar relacion
                        # padre 2 (restado): X roja
                        if i == 1 and p2: is_subtracted = True
                        if is_result and dy == y_row_p2: is_subtracted = True
                    
                    if is_subtracted:
                        # dibujar X roja
                        # sin circulo fondo como se pidio
                        
                        # X roja
                        line1 = arcade.shape_list.create_line(cx - 6, dy - 6, cx + 6, dy + 6, arcade.color.RED, 3)
                        line2 = arcade.shape_list.create_line(cx - 6, dy + 6, cx + 6, dy - 6, arcade.color.RED, 3)
                        shape_list.append(line1)
                        shape_list.append(line2)
                    else:
                        # punto normal
                        dot = arcade.shape_list.create_ellipse_filled(cx, dy, 8, 8, dot_color)
                        shape_list.append(dot)
                
                # linea conectora (grosor 3)
                if is_result and len(dots_to_draw) > 1:
                    line = arcade.shape_list.create_line(cx, min(dots_to_draw), cx, max(dots_to_draw), dot_color, 3)
                    shape_list.append(line)
                    
                    # simbolo conector
                    mid_y = (min(dots_to_draw) + max(dots_to_draw)) / 2
                    
                    # caja blanca fondo
                    box = arcade.shape_list.create_rectangle_filled(cx, mid_y, 14, 14, arcade.color.WHITE)
                    shape_list.append(box)
                    box_outline = arcade.shape_list.create_rectangle_outline(cx, mid_y, 14, 14, dot_color, 2)
                    shape_list.append(box_outline)
                    
                    # simbolo
                    sym = ""
                    if cell.operation in [OP_INTERSECT, "INTERSECT", "intersect", "∩"]: sym = "∩"
                    elif cell.operation in [OP_UNION, "UNION", "union", "∪"]: sym = "∪"
                    elif cell.operation in [OP_DIFFERENCE, "DIFFERENCE", "difference", "-"]: sym = "-"
                    
                    self.cached_plot_texts.append(arcade.Text(sym, cx, mid_y, arcade.color.BLACK, 10, anchor_x="center", anchor_y="center", bold=True))

        shape_list.draw()
        for txt in self.cached_plot_texts:
            txt.draw()
        self.cached_plot_texts = [] # limpiar tras dibujar

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.visible:
            return False
        return self.ui_manager.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.visible:
            return False
        return self.ui_manager.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        if not self.visible:
            return False
        return self.ui_manager.on_mouse_release(x, y, button, modifiers)
        
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.visible or not self.list_rect:
            return False
            
        rx, ry, rw, rh = self.list_rect
        # Check if mouse is within the list rectangle
        if rx <= x <= rx + rw and ry <= y <= ry + rh:
            # Scroll speed multiplier
            self.scroll_y -= scroll_y * 20
            return True
        return False
