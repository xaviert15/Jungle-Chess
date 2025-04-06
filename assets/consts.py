import pygame as pg
import os

class Consts:
    pg.init()
    # Obtém o diretório atual do arquivo
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Caminhos das fontes
    button_font = pg.font.Font(os.path.join(current_dir, 'button_font.ttf'), 30)
    main_title_font = pg.font.Font(os.path.join(current_dir, 'main_title_font.ttf'), 50)
    sub_title_font = pg.font.Font(os.path.join(current_dir, 'sub_title_font.ttf'), 30)
    message_font = pg.font.Font(os.path.join(current_dir, 'main_title_font.ttf'), 35)
    label_font = pg.font.Font(os.path.join(current_dir, 'main_title_font.ttf'), 15)
    text_font = pg.font.Font(os.path.join(current_dir, 'text_font.ttf'), 24)

    # Dimensões da janela
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 550

    # Cores
    BACKGROUND_COLOR = (245, 245, 245)  # Cinza claro
    TEXT_COLOR = (33, 33, 33)  # Cinza escuro
    SUBTITLE_COLOR = (66, 66, 66)  # Cinza médio
    LABEL_COLOR = (100, 100, 100)  # Cinza mais claro

    grass_color = (107, 170, 117)
    river_color = (69, 105, 144)
    trap_color = (173, 52, 62)
    den_color = (242, 175, 41)

    ROWS = 7
    COLS = 6
    BLOCK_SIZE = 50
    GAP = 5

    FPS = 60

    DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]