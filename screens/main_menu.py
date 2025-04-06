import pygame as pg
from assets.button import Button
import time
from assets.consts import Consts
from MVC.controller import Controller
from MVC.save_manager import SaveManager
import os
import sys

class MainMenu:
    def __init__(self) -> None:
        """Init main menu
        """
        pg.init()
        os.system('cls' if os.name == 'nt' else 'clear')
        # Init Clock
        self.clock = pg.time.Clock()

        # Screen Layout
        self.display = pg.display.set_mode((Consts.WINDOW_WIDTH, Consts.WINDOW_HEIGHT), 0, 32)
        
        # Carrega a imagem do leão
        self.lion_image = pg.image.load("assets/lion.png")
        # Redimensiona a imagem para um tamanho apropriado
        self.lion_image = pg.transform.scale(self.lion_image, (100, 100))
        
        # Botão de Regras no canto superior esquerdo
        rules_button_width = 120
        rules_button_height = 50
        margin = 20  # Margem em relação à borda da tela
        self.rules_button = Button("#4169E1", margin, margin, 
                                   rules_button_width, rules_button_height, 
                                   border_radius=15, text="Regras", 
                                   font=Consts.button_font)
        
        # Botões centralizados
        button_width = 200
        button_height = 60
        button_spacing = 20
        start_y = 200
        
        self.pvp_button = Button("#4CAF50", Consts.WINDOW_WIDTH/2 - button_width/2, start_y, button_width, button_height, 
                                border_radius=15, text="Jogar PxP", font=Consts.button_font)
        self.pve_button = Button("#2196F3", Consts.WINDOW_WIDTH/2 - button_width/2, start_y + button_height + button_spacing, 
                                button_width, button_height, border_radius=15, text="Jogar PxIA", 
                                font=Consts.button_font)
        self.aixai_button = Button("#9C27B0", Consts.WINDOW_WIDTH/2 - button_width/2, start_y + (button_height + button_spacing) * 2, 
                                 button_width, button_height, border_radius=15, text="Jogar IAxIA", 
                                 font=Consts.button_font)
        
        # Verifica se existe um jogo salvo para habilitar o botão Carregar
        has_saved_game = SaveManager.game_save_exists()
        load_color = "#FFA500" if has_saved_game else "#CCCCCC"  # Laranja se disponível, cinza se não
        
        self.load_button = Button(load_color, Consts.WINDOW_WIDTH/2 - button_width/2, start_y + (button_height + button_spacing) * 3, 
                                 button_width, button_height, border_radius=15, text="Carregar Jogo", 
                                 font=Consts.button_font)
                                 
        # Botão Sair no canto inferior esquerdo
        quit_button_width = 120
        quit_button_height = 50
        margin = 20  # Margem em relação à borda da tela
        self.quit_button = Button("#f44336", margin, Consts.WINDOW_HEIGHT - margin - quit_button_height, 
                                 quit_button_width, quit_button_height, border_radius=15, text="Sair", 
                                 font=Consts.button_font)
        
        self.buttons = [self.pvp_button, self.pve_button, self.aixai_button, self.load_button, self.quit_button]
        self.ui_buttons = [self.rules_button, self.quit_button]  # Botões de interface separados dos botões principais
        self.has_saved_game = has_saved_game  # Guarda estado para verificar na função de clique
        
        # Textos centralizados
        self.texts = [
            Consts.main_title_font.render('Jungle Chess', True, Consts.TEXT_COLOR),
            Consts.sub_title_font.render('Elementos de Inteligência Artificial e Ciência de Dados', True, Consts.SUBTITLE_COLOR),
            Consts.label_font.render('por Afonso Santos, Hugo Ferreira e Xavier Teixeira', True, Consts.LABEL_COLOR)
        ]

        # Posicionamento dos textos
        title_y = 100
        self.text_rects = [
            self.texts[0].get_rect(center=(Consts.WINDOW_WIDTH/2, title_y)),
            self.texts[1].get_rect(center=(Consts.WINDOW_WIDTH/2, title_y + 40)),
            self.texts[2].get_rect(center=(Consts.WINDOW_WIDTH/2, title_y + 70))
        ]
        
        # Fundo com gradiente
        self.background_color = Consts.BACKGROUND_COLOR
        pg.display.update()
        time.sleep(0.01)
        self.display.fill(self.background_color)

        # Desenha os elementos
        for button in self.buttons:
            button.draw(self.display)

        for i in range(3):
            self.display.blit(self.texts[i], self.text_rects[i])
            
        self.main_menu_loop()
    
    def main_menu_loop(self) -> None:
        """Main Menu loop
        """
        while True:
            pg.display.update()     # Refresh display
            
            for button in self.buttons:
                button.draw(self.display)   # Draw button
                
            # Desenha os botões de interface (Regras e Sair)
            for button in self.ui_buttons:
                button.draw(self.display)
            
            # Desenha a imagem do leão no canto inferior direito
            lion_x = Consts.WINDOW_WIDTH - 120
            lion_y = Consts.WINDOW_HEIGHT - 120
            self.display.blit(self.lion_image, (lion_x, lion_y))
            
            pos = pg.mouse.get_pos()    # Get mouse position
            
            for event in pg.event.get():
                """Handle events"""
                ev_type = event.type
                if ev_type == pg.QUIT:      # if event was quit, exit program
                    pg.quit()
                    sys.exit()
                
                elif ev_type == pg.MOUSEBUTTONDOWN:     # if event was mouse button down, handle press
                    if self.buttons[0].is_over(pos):    # Handle press on PvP Button
                        pg.display.quit()
                        time.sleep(0.2)
                        game = Controller(False)
                        
                    elif self.buttons[1].is_over(pos):  # Handle press on PvE Button
                        self.ai_selection_loop()
                    elif self.buttons[2].is_over(pos):  # Handle press on AIxAI Button
                        self.ai_vs_ai_selection_loop()
                    elif self.buttons[3].is_over(pos) and self.has_saved_game:  # Handle press on load Button
                        self.load_game()
                    elif self.buttons[4].is_over(pos):  # Handle press on quit Button
                        pg.quit()
                        sys.exit()
                    elif self.rules_button.is_over(pos):  # Handle press on rules Button
                        self.show_rules()
            
            self.clock.tick(60)

    def draw_ai_selection_menu(self):
        """Desenha o menu de seleção de IA"""
        self.display.fill(Consts.BACKGROUND_COLOR)
        
        # Título
        title = Consts.main_title_font.render("Selecione a IA", True, Consts.TEXT_COLOR)
        title_rect = title.get_rect(center=(Consts.WINDOW_WIDTH/2, 100))
        self.display.blit(title, title_rect)
        
        # Botões centralizados
        button_width = 200
        button_height = 60
        button_spacing = 20
        start_y = 150
        
        self.random_button = Button("#DCDCDC", Consts.WINDOW_WIDTH/2 - button_width/2, start_y, button_width, button_height, 
                                    border_radius=15, text="Aleatório", font=Consts.button_font)
        self.minimax_button = Button("#4CAF50", Consts.WINDOW_WIDTH/2 - button_width/2, start_y + button_height + button_spacing, 
                                   button_width, button_height, border_radius=15, text="Minimax", 
                                   font=Consts.button_font)
        self.negamax_button = Button("#2196F3", Consts.WINDOW_WIDTH/2 - button_width/2, start_y + (button_height + button_spacing) * 2, 
                                   button_width, button_height, border_radius=15, text="Negamax", 
                                   font=Consts.button_font)
        self.back_button = Button("#808080", Consts.WINDOW_WIDTH/2 - button_width/2, start_y + (button_height + button_spacing) * 3, 
                                 button_width, button_height, border_radius=15, text="Voltar", 
                                 font=Consts.button_font)
        
        # Desenha os botões
        self.random_button.draw(self.display)
        self.minimax_button.draw(self.display)
        self.negamax_button.draw(self.display)
        self.back_button.draw(self.display)
        
        # Desenha a imagem do leão no canto inferior direito
        lion_x = Consts.WINDOW_WIDTH - 120
        lion_y = Consts.WINDOW_HEIGHT - 120
        self.display.blit(self.lion_image, (lion_x, lion_y))
        
        pg.display.flip()

    def draw_minimax_difficulty_menu(self):
        """Desenha o menu de seleção de dificuldade do Minimax"""
        self.display.fill(Consts.BACKGROUND_COLOR)
        
        # Título
        title = Consts.main_title_font.render("Selecione a Dificuldade", True, Consts.TEXT_COLOR)
        title_rect = title.get_rect(center=(Consts.WINDOW_WIDTH/2, 100))
        self.display.blit(title, title_rect)
        
        # Botões centralizados
        button_width = 200
        button_height = 60
        button_spacing = 20
        start_y = 150
        
        self.easy_button = Button("#4CAF50", Consts.WINDOW_WIDTH/2 - button_width/2, start_y, button_width, button_height, 
                                   border_radius=15, text="Fácil", font=Consts.button_font)
        self.medium_button = Button("#FFA500", Consts.WINDOW_WIDTH/2 - button_width/2, start_y + button_height + button_spacing, 
                                   button_width, button_height, border_radius=15, text="Médio", 
                                   font=Consts.button_font)
        self.hard_button = Button("#f44336", Consts.WINDOW_WIDTH/2 - button_width/2, start_y + (button_height + button_spacing) * 2, 
                                   button_width, button_height, border_radius=15, text="Difícil", 
                                   font=Consts.button_font)
        self.back_button = Button("#808080", Consts.WINDOW_WIDTH/2 - button_width/2, start_y + (button_height + button_spacing) * 3, 
                                 button_width, button_height, border_radius=15, text="Voltar", 
                                 font=Consts.button_font)
        
        # Desenha os botões
        self.easy_button.draw(self.display)
        self.medium_button.draw(self.display)
        self.hard_button.draw(self.display)
        self.back_button.draw(self.display)
        
        # Desenha a imagem do leão no canto inferior direito
        lion_x = Consts.WINDOW_WIDTH - 120
        lion_y = Consts.WINDOW_HEIGHT - 120
        self.display.blit(self.lion_image, (lion_x, lion_y))
        
        pg.display.flip()
        
    def draw_negamax_difficulty_menu(self):
        """Desenha o menu de seleção de dificuldade do Negamax"""
        self.display.fill(Consts.BACKGROUND_COLOR)
        
        # Título
        title = Consts.main_title_font.render("Selecione a Dificuldade", True, Consts.TEXT_COLOR)
        title_rect = title.get_rect(center=(Consts.WINDOW_WIDTH/2, 100))
        self.display.blit(title, title_rect)
        
        # Botões centralizados
        button_width = 200
        button_height = 60
        button_spacing = 20
        start_y = 150
        
        self.easy_button = Button("#4CAF50", Consts.WINDOW_WIDTH/2 - button_width/2, start_y, button_width, button_height, 
                                   border_radius=15, text="Fácil", font=Consts.button_font)
        self.medium_button = Button("#FFA500", Consts.WINDOW_WIDTH/2 - button_width/2, start_y + button_height + button_spacing, 
                                   button_width, button_height, border_radius=15, text="Médio", 
                                   font=Consts.button_font)
        self.hard_button = Button("#f44336", Consts.WINDOW_WIDTH/2 - button_width/2, start_y + (button_height + button_spacing) * 2, 
                                   button_width, button_height, border_radius=15, text="Difícil", 
                                   font=Consts.button_font)
        self.back_button = Button("#808080", Consts.WINDOW_WIDTH/2 - button_width/2, start_y + (button_height + button_spacing) * 3, 
                                 button_width, button_height, border_radius=15, text="Voltar", 
                                 font=Consts.button_font)
        
        # Desenha os botões
        self.easy_button.draw(self.display)
        self.medium_button.draw(self.display)
        self.hard_button.draw(self.display)
        self.back_button.draw(self.display)
        
        # Desenha a imagem do leão no canto inferior direito
        lion_x = Consts.WINDOW_WIDTH - 120
        lion_y = Consts.WINDOW_HEIGHT - 120
        self.display.blit(self.lion_image, (lion_x, lion_y))
        
        pg.display.flip()
        
    def ai_selection_loop(self):
        """Loop do menu de seleção de IA"""
        while True:
            self.draw_ai_selection_menu()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                    
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    
                    # Verifica clique nos botões
                    if self.random_button.is_over(mouse_pos):
                        game = Controller(True, "random")
                        return
                    elif self.minimax_button.is_over(mouse_pos):
                        self.minimax_difficulty_loop()
                        return
                    elif self.negamax_button.is_over(mouse_pos):
                        self.negamax_difficulty_loop()
                        return
                    elif self.back_button.is_over(mouse_pos):
                        # Limpa a tela e redesenha o menu principal
                        self.display.fill(Consts.BACKGROUND_COLOR)
                        for button in self.buttons:
                            button.draw(self.display)
                        for i in range(3):
                            self.display.blit(self.texts[i], self.text_rects[i])
                        pg.display.flip()
                        return
                        
            self.clock.tick(60)

    def minimax_difficulty_loop(self):
        """Loop do menu de seleção de dificuldade do Minimax"""
        while True:
            self.draw_minimax_difficulty_menu()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                    
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    
                    # Verifica clique nos botões
                    if self.easy_button.is_over(mouse_pos):
                        game = Controller(True, "minimax", 3)  # Fácil - depth 3
                        return
                    elif self.medium_button.is_over(mouse_pos):
                        game = Controller(True, "minimax", 4)  # Médio - depth 4
                        return
                    elif self.hard_button.is_over(mouse_pos):
                        game = Controller(True, "minimax", 5)  # Difícil - depth 5
                        return
                    elif self.back_button.is_over(mouse_pos):
                        # Volta para o menu de seleção de IA
                        self.ai_selection_loop()
                        return
                        
            self.clock.tick(60)

    def negamax_difficulty_loop(self):
        """Loop do menu de seleção de dificuldade do Negamax"""
        while True:
            self.draw_negamax_difficulty_menu()
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                    
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    
                    # Verifica clique nos botões
                    if self.easy_button.is_over(mouse_pos):
                        game = Controller(True, "negamax", 3)  # Fácil - depth 3
                        return
                    elif self.medium_button.is_over(mouse_pos):
                        game = Controller(True, "negamax", 4)  # Médio - depth 4
                        return
                    elif self.hard_button.is_over(mouse_pos):
                        game = Controller(True, "negamax", 5)  # Difícil - depth 5
                        return
                    elif self.back_button.is_over(mouse_pos):
                        # Volta para o menu de seleção de IA
                        self.ai_selection_loop()
                        return
                        
            self.clock.tick(60)

    def draw_ai_vs_ai_selection_menu(self, player_color):
        """Desenha o menu de seleção de IA para IAxIA"""
        self.display.fill(Consts.BACKGROUND_COLOR)
        
        # Título
        title_text = "Selecione a IA para o Jogador " + ("Azul" if player_color == "blue" else "Vermelho")
        title = Consts.main_title_font.render(title_text, True, Consts.TEXT_COLOR)
        title_rect = title.get_rect(center=(Consts.WINDOW_WIDTH/2, 100))
        self.display.blit(title, title_rect)
        
        # Botões organizados em duas colunas
        button_width = 200
        button_height = 60
        button_spacing = 20
        start_y = 150
        
        # Posições para coluna esquerda
        left_x = Consts.WINDOW_WIDTH/2 - button_width - button_spacing/2
        # Posições para coluna direita
        right_x = Consts.WINDOW_WIDTH/2 + button_spacing/2
        
        # Criação dos botões (organizados em duas colunas)
        # Coluna esquerda
        self.random_button = Button("#DCDCDC", left_x, start_y, button_width, button_height, 
                                    border_radius=15, text="Aleatório", font=Consts.button_font)
        self.minimax2_button = Button("#4CAF50", left_x, start_y + button_height + button_spacing, 
                                   button_width, button_height, border_radius=15, text="Minimax 3", 
                                   font=Consts.button_font)
        self.minimax3_button = Button("#4CAF50", left_x, start_y + (button_height + button_spacing) * 2, 
                                   button_width, button_height, border_radius=15, text="Minimax 4", 
                                   font=Consts.button_font)
        self.minimax4_button = Button("#4CAF50", left_x, start_y + (button_height + button_spacing) * 3, 
                                   button_width, button_height, border_radius=15, text="Minimax 5", 
                                   font=Consts.button_font)
        
        # Coluna direita
        self.negamax2_button = Button("#2196F3", right_x, start_y, 
                                   button_width, button_height, border_radius=15, text="Negamax 3", 
                                   font=Consts.button_font)
        self.negamax3_button = Button("#2196F3", right_x, start_y + button_height + button_spacing, 
                                   button_width, button_height, border_radius=15, text="Negamax 4", 
                                   font=Consts.button_font)
        self.negamax4_button = Button("#2196F3", right_x, start_y + (button_height + button_spacing) * 2, 
                                   button_width, button_height, border_radius=15, text="Negamax 5", 
                                   font=Consts.button_font)
        
        # Botão voltar na coluna direita
        self.back_button = Button("#808080", right_x, start_y + (button_height + button_spacing) * 3, 
                                 button_width, button_height, border_radius=15, text="Voltar", 
                                 font=Consts.button_font)
        
        # Desenha os botões
        self.random_button.draw(self.display)
        self.minimax2_button.draw(self.display)
        self.minimax3_button.draw(self.display)
        self.minimax4_button.draw(self.display)
        self.negamax2_button.draw(self.display)
        self.negamax3_button.draw(self.display)
        self.negamax4_button.draw(self.display)
        self.back_button.draw(self.display)
        
        # Desenha a imagem do leão no canto inferior direito
        lion_x = Consts.WINDOW_WIDTH - 120
        lion_y = Consts.WINDOW_HEIGHT - 120
        self.display.blit(self.lion_image, (lion_x, lion_y))
        
        pg.display.flip()

    def ai_vs_ai_selection_loop(self):
        """Loop do menu de seleção de IA para IAxIA"""
        # Seleção do jogador azul
        blue_ai = self.ai_vs_ai_selection_menu_loop("blue")
        if blue_ai is None:  # Se o usuário voltou
            return
            
        # Seleção do jogador vermelho
        red_ai = self.ai_vs_ai_selection_menu_loop("red")
        if red_ai is None:  # Se o usuário voltou
            return
            
        # Inicia o jogo com as IAs selecionadas
        game = Controller(True, "aixai", blue_ai=blue_ai, red_ai=red_ai)

    def ai_vs_ai_selection_menu_loop(self, player_color):
        """Loop do menu de seleção de IA para um jogador específico"""
        while True:
            self.draw_ai_vs_ai_selection_menu(player_color)
            
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                    
                if event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    
                    # Verifica clique nos botões
                    if self.random_button.is_over(mouse_pos):
                        return "random"
                    elif self.minimax2_button.is_over(mouse_pos):
                        return ("minimax", 3)
                    elif self.minimax3_button.is_over(mouse_pos):
                        return ("minimax", 4)
                    elif self.minimax4_button.is_over(mouse_pos):
                        return ("minimax", 5)
                    elif self.negamax2_button.is_over(mouse_pos):
                        return ("negamax", 3)
                    elif self.negamax3_button.is_over(mouse_pos):
                        return ("negamax", 4)
                    elif self.negamax4_button.is_over(mouse_pos):
                        return ("negamax", 5)
                    elif self.back_button.is_over(mouse_pos):
                        # Limpa a tela e redesenha o menu principal
                        self.display.fill(Consts.BACKGROUND_COLOR)
                        for button in self.buttons:
                            button.draw(self.display)
                        for i in range(3):
                            self.display.blit(self.texts[i], self.text_rects[i])
                        pg.display.flip()
                        return None
                        
            self.clock.tick(60)

    def load_game(self):
        """Carrega um jogo salvo"""
        if not self.has_saved_game:
            # Se não houver jogo salvo, não faz nada
            return
        
        # Fecha a tela atual
        pg.display.quit()
        time.sleep(0.2)
        
        try:
            # Carrega o jogo salvo
            controller = Controller.load_saved_game()
            if controller is None:
                # Se falhou ao carregar, volta ao menu principal
                self.__init__()
        except Exception as e:
            # Se ocorrer erro, imprime e volta ao menu principal
            print(f"Erro ao carregar o jogo: {e}")
            self.__init__()

    def show_rules(self):
        """Mostra a tela de regras do jogo"""
        # Carrega a imagem do tabuleiro
        board_image = pg.image.load("assets/board.png")
        # Redimensiona a imagem para um tamanho adequado
        board_image = pg.transform.scale(board_image, (400, 400))
        
        # Texto das regras
        rules_text = [
            "Jungle Chess",
            "Jungle Chess é um jogo antigo indiano, também conhecido como Jungle (no entanto, devido a muitas diferenças, não é incluído na categoria de xadrez). É jogado num tabuleiro de 6 x 7 que contém campos de água (azul), tocas dos jogadores (dourado) e armadilhas (bordô).",
            "",
            "Posição inicial e objetivo do jogo",
            "",
            "Cada jogador começa o jogo com 6 peças que representam seis tipos de animais – elefante, leão, leopardo, lobo, gato e rato (ordenados por força). As peças estão posicionadas nas suas posições iniciais:",
            "",
            "O objetivo do jogo é conquistar a toca do adversário ou capturar todos os animais inimigos.",
            "",
            "Movimento e captura das peças",
            "",
            "A movimentação básica de todas as peças é de uma casa na horizontal ou vertical para uma casa que esteja vazia ou ocupada por um animal inimigo (se for possível capturá-lo, ver regras detalhadas na secção seguinte).",
            "A regra comum de captura é que cada animal pode comer um animal inimigo com a mesma força ou mais fraco (há regras especiais para o elefante e o rato, ver abaixo).",
            "",
            "- Elefante (8): É o animal mais forte e pode capturar todos os outros",
            "animais, exceto o rato.",
            "",
            "- Leão (7): O leão pode fazer (além dos seus movimentos normais) saltos",
            "por cima da água. Isto significa que se estiver ao lado de uma casa azul e a casa de destino correspondente do outro lado da água estiver vazia ou ocupada por um animal que ele possa comer, o leão pode fazer o movimento de salto. Há uma exceção: não é possível saltar se um rato (do jogador ou do adversário) estiver a bloquear o caminho do salto.",
            "",
            "- Leopardo (5): Não tem movimentos ou habilidades especiais.",
            "",
            "- Lobo (4): Não tem movimentos ou habilidades especiais.",
            "",
            "- Gato (2): Não tem movimentos ou habilidades especiais.",
            "",
            "- Rato (1): O rato é a peça mais interessante do jogo. Apesar de ser o",
            "menor e mais fraco, pode matar um elefante (havia um mito de que um rato podia entrar no ouvido de um elefante e comer-lhe o cérebro).",
            "O rato é também o único animal que pode entrar na água (casas azuis) e bloquear os saltos do leão ou do tigre. No entanto, um rato na água não pode capturar um elefante inimigo ao saltar para fora da água tem de fazer outro movimento para sair da água primeiro.",
            "",
            "Como termina o jogo",
            "",
            "O jogo termina se uma das seguintes condições for cumprida:",
            "",
            "- Um animal de um dos jogadores entra na toca do adversário (casa dourada).",
            "Esse jogador vence o jogo.",
            "",
            "Outras regras importantes",
            "",
            "- Nenhum animal pode entrar na sua própria toca.",
            "",
            "- Qualquer animal de um jogador que esteja numa armadilha do adversário",
            "(casa bordô) pode ser comido por qualquer animal inimigo, até mesmo por um rato.",
            "",
            "",
            "",
        ]
        
        # Cores e fontes
        title_font = Consts.main_title_font  # Título principal usando a fonte main_title_font
        heading_font = Consts.sub_title_font  # Subtítulos usando a fonte sub_title_font
        text_font = Consts.text_font  # Texto normal usando a fonte text_font
        
        # Botão voltar (posicionado no topo à esquerda)
        back_button = Button("#B8C6DB", 20, 20, 90, 55, 
                           border_radius=50, text='Voltar', font=Consts.button_font)
        
        # Definições para a barra de scroll
        scroll_bar_width = 20
        scroll_bar_color = (180, 180, 180)
        scroll_thumb_color = (120, 120, 120)
        scroll_bar_x = Consts.WINDOW_WIDTH - scroll_bar_width - 10
        is_dragging_scroll = False
        
        # Posição inicial do texto e imagem (ajustada para não sobrepor o botão)
        y_pos = 100  # Aumentado para evitar sobreposição com o botão
        margin_left = 80  # Margem à esquerda aumentada
        margin_right = 120  # Margem à direita aumentada para evitar que o texto seja cortado
        text_area_width = Consts.WINDOW_WIDTH - margin_left - margin_right  # Largura disponível para o texto
        scroll_offset = 0
        
        # Espaçamentos
        line_spacing = 35  # Espaço entre linhas normais aumentado
        paragraph_spacing = 40  # Espaço após parágrafos aumentado
        section_spacing = 60  # Espaço antes de nova seção aumentado
        title_spacing = 80  # Espaço após título principal aumentado
        list_item_spacing = 30  # Espaço para itens de lista
        empty_line_spacing = 15  # Espaço para linhas vazias
        
        # Função auxiliar para quebrar o texto que é muito longo
        def wrap_text(text, font, max_width):
            words = text.split(' ')
            lines = []
            current_line = []
            
            for word in words:
                # Testa se a linha atual + a próxima palavra cabe na largura máxima
                test_line = ' '.join(current_line + [word])
                test_width = font.size(test_line)[0]
                
                if test_width <= max_width:
                    current_line.append(word)
                else:
                    # Se não couber, adiciona a linha atual à lista de linhas
                    if current_line:
                        lines.append(' '.join(current_line))
                    current_line = [word]
            
            # Adiciona a última linha
            if current_line:
                lines.append(' '.join(current_line))
                
            return lines
        
        # Processa o texto para quebrar linhas muito longas
        processed_rules_text = []
        for line in rules_text:
            if line.startswith("-") or line == "" or line == "Jungle Chess":
                # Mantém títulos, linhas vazias e itens de lista como estão
                processed_rules_text.append(line)
            elif line in ["Posição inicial e objetivo do jogo", "Movimento e captura das peças", 
                         "Como termina o jogo", "Outras regras importantes"]:
                # Mantém cabeçalhos de seção como estão
                processed_rules_text.append(line)
            else:
                # Quebra o texto que é muito longo
                wrapped_lines = wrap_text(line, text_font, text_area_width)
                processed_rules_text.extend(wrapped_lines)
        
        # Loop da tela de regras
        running = True
        while running:
            self.display.fill(Consts.BACKGROUND_COLOR)
            
            # Calcular altura total do conteúdo para a barra de scroll
            total_height = y_pos
            for i, line in enumerate(processed_rules_text):
                # Calcula a altura com base no tipo de linha
                if i == 0:  # Título principal
                    total_height += title_spacing  # Altura do título com espaçamento
                elif line and line in ["Posição inicial e objetivo do jogo", "Movimento e captura das peças",
                                      "Como termina o jogo", "Outras regras importantes"]:
                    # Adiciona espaço extra antes dos títulos de seção
                    if i > 1 and processed_rules_text[i-1] == "":
                        total_height += section_spacing
                    else:
                        total_height += paragraph_spacing
                elif line == "":  # Linha vazia (separador)
                    total_height += empty_line_spacing  # Espaço menor para linhas vazias
                elif line.startswith("-"):  # Item de lista
                    total_height += list_item_spacing  # Espaço para itens de lista
                else:
                    total_height += line_spacing  # Espaçamento normal entre linhas
                
                # Adiciona espaço para a imagem
                if i == 8:  # Após a linha das posições iniciais
                    total_height += 40 + 400 + 30  # Espaço antes + altura da imagem + espaço depois
            
            # Desenha a barra de scroll
            visible_ratio = min(1.0, Consts.WINDOW_HEIGHT / total_height)
            thumb_height = max(40, visible_ratio * Consts.WINDOW_HEIGHT)
            
            # Calcula a posição do thumb da barra de scroll
            scroll_range = total_height - Consts.WINDOW_HEIGHT
            scroll_ratio = 0 if scroll_range <= 0 else min(1.0, abs(scroll_offset) / scroll_range)
            thumb_pos = scroll_ratio * (Consts.WINDOW_HEIGHT - thumb_height)
            
            # Desenha a barra de fundo
            pg.draw.rect(self.display, scroll_bar_color, 
                        (scroll_bar_x, 0, 
                         scroll_bar_width, Consts.WINDOW_HEIGHT))
            
            # Desenha o thumb (o controle deslizante)
            pg.draw.rect(self.display, scroll_thumb_color, 
                        (scroll_bar_x, thumb_pos, 
                         scroll_bar_width, thumb_height),
                        border_radius=scroll_bar_width // 2)
            
            # Desenha o botão voltar
            back_button.draw(self.display)
            
            # Aplica o scroll
            current_y = y_pos + scroll_offset
            
            # Desenha o título
            title_surface = title_font.render(processed_rules_text[0], True, (33, 33, 33))
            title_rect = title_surface.get_rect(center=(Consts.WINDOW_WIDTH/2 - scroll_bar_width/2, current_y))
            self.display.blit(title_surface, title_rect)
            current_y += title_spacing
            
            # Variável para controlar se estamos começando uma nova seção
            new_section = False
            
            # Desenha o texto das regras
            for i in range(1, len(processed_rules_text)):
                line = processed_rules_text[i]
                
                # Verifica se estamos começando uma nova seção
                if line in ["Posição inicial e objetivo do jogo", "Movimento e captura das peças", 
                           "Como termina o jogo", "Outras regras importantes"]:
                    new_section = True
                
                # Se é uma linha de título (sem espaço no início e linha anterior vazia)
                if line and not line.startswith(" ") and (i == 1 or processed_rules_text[i-1] == ""):
                    # Verifica se é um título de seção
                    if line in ["Posição inicial e objetivo do jogo", "Movimento e captura das peças", 
                               "Como termina o jogo", "Outras regras importantes"]:
                        # Adiciona espaço extra antes dos títulos de seção
                        if new_section:
                            current_y += section_spacing - line_spacing  # Ajusta para não duplicar o espaçamento normal
                        
                        text_surface = heading_font.render(line, True, (33, 33, 33))
                    else:
                        text_surface = text_font.render(line, True, (33, 33, 33))
                else:
                    text_surface = text_font.render(line, True, (33, 33, 33))
                
                # Não renderiza texto fora da área visível
                if current_y > -50 and current_y < Consts.WINDOW_HEIGHT + 50:
                    text_rect = text_surface.get_rect(topleft=(margin_left, current_y))
                    
                    # Verifica se o texto está sobrepondo o botão voltar
                    if current_y < 80:  # Altura aproximada do botão + margem
                        # Ajusta a posição X para evitar sobreposição com o botão
                        text_rect.topleft = (max(margin_left, 120), current_y)  # 120 = botão (90) + margem (30)
                    
                    self.display.blit(text_surface, text_rect)
                
                # Calcula o próximo espaçamento baseado no tipo de linha
                if i == 11:  # Após a linha das posições iniciais (para a imagem)
                    current_y += 40  # Espaço antes da imagem
                    if current_y > -400 and current_y < Consts.WINDOW_HEIGHT + 400:
                        # Centraliza a imagem (considerando a barra de scroll)
                        image_rect = board_image.get_rect(center=(Consts.WINDOW_WIDTH/2 - scroll_bar_width/2, current_y + 200))
                        self.display.blit(board_image, image_rect)
                    current_y += 430  # Espaço para a imagem + espaço extra
                elif line == "":  # Linha vazia (separador)
                    current_y += empty_line_spacing  # Espaço menor para linhas vazias
                elif line.startswith("-"):  # Item de lista
                    current_y += list_item_spacing  # Espaço para itens de lista
                elif line in ["Posição inicial e objetivo do jogo", "Movimento e captura das peças", 
                             "Como termina o jogo", "Outras regras importantes"]:
                    current_y += paragraph_spacing  # Mais espaço após títulos de seção
                else:
                    current_y += line_spacing  # Espaçamento normal entre linhas
            
            # Processa eventos
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouse_pos = pg.mouse.get_pos()
                    if back_button.is_over(mouse_pos):
                        running = False
                        # Redesenha completamente o menu principal quando sair
                        self.display.fill(Consts.BACKGROUND_COLOR)
                        
                        # Desenha textos do título
                        for i in range(3):
                            self.display.blit(self.texts[i], self.text_rects[i])
                        
                        # Desenha os botões principais
                        for button in self.buttons:
                            button.draw(self.display)
                            
                        # Desenha os botões de interface
                        for button in self.ui_buttons:
                            button.draw(self.display)
                        
                        # Desenha o leão no canto
                        lion_x = Consts.WINDOW_WIDTH - 120
                        lion_y = Consts.WINDOW_HEIGHT - 120
                        self.display.blit(self.lion_image, (lion_x, lion_y))
                        
                        pg.display.flip()
                    # Verifica se clicou na barra de scroll ou no thumb
                    elif (scroll_bar_x <= mouse_pos[0] <= scroll_bar_x + scroll_bar_width) and (0 <= mouse_pos[1] <= Consts.WINDOW_HEIGHT):
                        # Se clicou no thumb, inicia o arrasto
                        if thumb_pos <= mouse_pos[1] <= thumb_pos + thumb_height:
                            is_dragging_scroll = True
                        else:
                            # Se clicou na barra (não no thumb), move a visualização para a posição correspondente
                            # Calcula a proporção do clique em relação à altura da barra de scroll
                            click_ratio = mouse_pos[1] / Consts.WINDOW_HEIGHT
                            # Calcula o novo offset baseado na proporção
                            scroll_offset = -(click_ratio * (total_height - Consts.WINDOW_HEIGHT))
                            # Garante que o scroll não ultrapasse os limites
                            if scroll_offset > 0:
                                scroll_offset = 0
                            min_scroll = -((total_height - Consts.WINDOW_HEIGHT))
                            if scroll_offset < min_scroll:
                                scroll_offset = min_scroll
                    elif event.button == 4:  # Scroll para cima
                        scroll_offset += 30
                        if scroll_offset > 0:
                            scroll_offset = 0
                    elif event.button == 5:  # Scroll para baixo
                        scroll_offset -= 30
                        # Limita o scroll para baixo (valor negativo maior em módulo)
                        min_scroll = -((total_height - Consts.WINDOW_HEIGHT))
                        if scroll_offset < min_scroll:
                            scroll_offset = min_scroll
                elif event.type == pg.MOUSEMOTION:
                    # Se estiver arrastando o thumb
                    if is_dragging_scroll:
                        mouse_pos = pg.mouse.get_pos()
                        # Obter o deslocamento relativo ao topo da barra
                        relative_pos = mouse_pos[1]
                        # Ajustar para que o ponto de arrasto seja mantido sob o cursor
                        relative_pos = max(0, min(relative_pos, Consts.WINDOW_HEIGHT - thumb_height))
                        # Calcular a proporção
                        scroll_percent = relative_pos / (Consts.WINDOW_HEIGHT - thumb_height)
                        # Aplicar a proporção ao intervalo total
                        scroll_offset = -scroll_percent * (total_height - Consts.WINDOW_HEIGHT)
                        # Limite de segurança
                        if scroll_offset > 0:
                            scroll_offset = 0
                        min_scroll = -((total_height - Consts.WINDOW_HEIGHT))
                        if min_scroll > 0:
                            min_scroll = 0
                        if scroll_offset < min_scroll:
                            scroll_offset = min_scroll
                elif event.type == pg.MOUSEBUTTONUP:
                    # Para de arrastar quando o botão do mouse é solto
                    if is_dragging_scroll:
                        is_dragging_scroll = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_UP:  # Seta para cima
                        scroll_offset += 30
                        if scroll_offset > 0:
                            scroll_offset = 0
                    elif event.key == pg.K_DOWN:  # Seta para baixo
                        scroll_offset -= 30
                        # Limita o scroll para baixo
                        min_scroll = -((total_height - Consts.WINDOW_HEIGHT))
                        if scroll_offset < min_scroll:
                            scroll_offset = min_scroll
            
            pg.display.flip()
            self.clock.tick(60)