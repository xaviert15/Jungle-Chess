import pygame as pg

class Button:
    def __init__(self, color, x, y, w, h, border_radius=0, text='', font=None, outline=None, outline_thickness=0):
        hex = color[1:]
        self.color = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
        self.original_color = self.color  # Guarda a cor original
        self.hover_color = self.lighten_color(self.color, 30)  # Cor mais clara para hover
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.text = text
        self.font = font
        self.outline = outline
        self.outline_thickness = outline_thickness
        self.border_radius = border_radius
        self.is_hovered = False  # Estado de hover

    def lighten_color(self, color, amount=30):
        """Clareia uma cor RGB adicionando um valor a cada componente"""
        r, g, b = color
        return min(r + amount, 255), min(g + amount, 255), min(b + amount, 255)

    def draw(self, window):
        # Verifica se o mouse está sobre o botão
        mouse_pos = pg.mouse.get_pos()
        self.is_hovered = self.is_over(mouse_pos)
        
        # Escolhe a cor baseada no estado de hover
        current_color = self.hover_color if self.is_hovered else self.original_color
        
        # Desenha o contorno se existir
        if self.outline:
            pg.draw.rect(window, self.outline, 
                        (self.x - self.outline_thickness, 
                         self.y - self.outline_thickness,
                         self.w + self.outline_thickness * 2,
                         self.h + self.outline_thickness * 2),
                        border_radius=self.border_radius)

        # Desenha o botão
        pg.draw.rect(window, current_color, 
                    (self.x, self.y, self.w, self.h), 
                    border_radius=self.border_radius)

        # Desenha o texto se existir
        if self.text and self.font:
            text = self.font.render(self.text, True, (255, 255, 255))  # Cor branca
            text_rect = text.get_rect(center=(self.x + self.w/2, self.y + self.h/2))
            window.blit(text, text_rect)

    def is_over(self, pos):
        return self.x < pos[0] < self.x + self.w and self.y < pos[1] < self.y + self.h