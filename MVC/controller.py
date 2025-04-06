from MVC.model import Model, AI, RandomAI, NegamaxAI
from MVC.view import View
import time
import pygame as pg
from assets.consts import Consts
from MVC.save_manager import SaveManager
import numpy as np


class Controller:
    def __init__(self, is_pve: bool, ai_type: str = "minimax", depth: int = 4, blue_ai: tuple = None, red_ai: tuple = None, start_loop: bool = True):
        """Inicia o componente Controlador

        Args:
            is_pve (bool): deve o jogo usar lógica PvE ou PvP
            ai_type (str): tipo de IA a ser usada (default: "minimax")
            depth (int): profundidade do algoritmo minimax (default: 4)
            blue_ai (tuple): configuração da IA para o jogador azul no modo IAxIA (default: None)
            red_ai (tuple): configuração da IA para o jogador vermelho no modo IAxIA (default: None)
            start_loop (bool): inicia o loop principal automaticamente (default: True)
        """
        self.model = Model()
        self.view = View()
        self.is_pve = is_pve
        self.ai_type = ai_type
        
        # Inicializa as IAs apropriadas
        if blue_ai is not None and red_ai is not None:  # Modo IAxIA
            self.blue_ai = self._create_ai(blue_ai)
            self.red_ai = self._create_ai(red_ai)
            self.is_aixai = True
            self.view.is_aixai = True  # Define a flag na View
            # Adiciona controle de movimentos repetidos
            self.last_moves = []  # Lista para armazenar os últimos movimentos
            self.forbidden_move = None  # Movimento proibido após 3 repetições
        elif is_pve:
            if ai_type == "minimax":
                self.ai = AI(self.model, depth)
            elif ai_type == "negamax":
                self.ai = NegamaxAI(self.model, depth)
            else:  # random
                self.ai = RandomAI(self.model)
            self.is_aixai = False
        else:
            self.is_aixai = False
        
        pg.event.set_blocked([pg.MOUSEMOTION])
        
        # Inicia o loop principal apenas se start_loop for True
        if start_loop:
            self.main_loop()
    
    def _create_ai(self, ai_config):
        """Cria uma instância de IA baseada na configuração fornecida
        
        Args:
            ai_config (tuple/str): Configuração da IA ("random" ou (tipo, profundidade))
            
        Returns:
            AI/NegamaxAI/RandomAI: Instância da IA criada
        """
        if ai_config == "random":
            return RandomAI(self.model, seed=42)  # Usa semente fixa 42 para reprodutibilidade
        else:
            ai_type, depth = ai_config
            if ai_type == "minimax":
                return AI(self.model, depth)
            elif ai_type == "negamax":
                return NegamaxAI(self.model, depth)
            else:
                # Fallback para RandomAI em caso de tipo desconhecido
                return RandomAI(self.model, seed=42)
    
    def main_loop(self):
        """Loop principal do jogo
        """
        while True:
            if self.is_aixai:  # Modo IAxIA
                self.aixai_game_loop()   # Chama a lógica de jogo IAxIA
            elif self.is_pve:    # Deve usar lógica de jogo PvE ou PvP
                self.pve_game_loop(self.model.turn)   # Chama a lógica de jogo PvE
            else:
                self.pvp_game_loop(self.model.turn)   # Chama a lógica de jogo PvP
                       
    def pve_game_loop(self, turn: int):
        """Lógica de jogo PvE

        Args:
            turn (int): turno para jogador azul (0) ou jogador vermelho (1)
        """
        # Força o desenho do tabuleiro logo no início, sem esperar por um evento
        self.view.draw_board(self.model.game_board, self.model.last_move_coords)
        
        # Também desenha possíveis movimentos se uma peça já estiver selecionada
        if self.model.selected_game_piece is not None and self.model.moves:
            self.view.draw_possible_moves(self.model.moves)
        
        pg.display.flip()

        if turn == 0:
            # turno para o jogador humano
            for event in pg.event.get():
                ev_type = event.type
                # Desenha o tabuleiro após cada evento para garantir que os movimentos possíveis sejam visíveis
                self.view.draw_board(self.model.game_board, self.model.last_move_coords)
                
                # Se houver uma peça selecionada e movimentos possíveis, desenha-os
                if self.model.selected_game_piece is not None and self.model.moves:
                    self.view.draw_possible_moves(self.model.moves)
                
                self.handle(ev_type)    # Processa o evento

        elif turn == 1:
            # turno para a IA
            time.sleep(0.2)  # Pequena pausa para melhor experiência do utilizador
            
            # Atualiza o temporizador antes de começar o processamento da IA
            self.view.draw_board(self.model.game_board, self.model.last_move_coords)
            pg.display.flip()
            
            # Obtém o melhor movimento da IA
            best_move = self.ai.get_best_move()
            
            # Atualiza o temporizador após o processamento da IA
            self.view.draw_board(self.model.game_board, self.model.last_move_coords)
            pg.display.flip()
            
            if best_move:
                start, end = best_move
                self.model.perform_move(start, end)
                self.view.draw_board(self.model.game_board, self.model.last_move_coords)
                is_win = self.model.is_win()
                if is_win[0]:
                    play_again_button, main_menu_button = self.view.draw_win_message(is_win[1])
                    self.view.draw_board(self.model.game_board, self.model.last_move_coords)
                    while True:
                        for event in pg.event.get():
                            if event.type == pg.MOUSEBUTTONDOWN:
                                if play_again_button.is_over(pg.mouse.get_pos()):
                                    self.reset_game()
                                elif main_menu_button.is_over(pg.mouse.get_pos()):
                                    pg.display.quit()
                                    time.sleep(0.2)
                                    from screens.main_menu import MainMenu
                                    main_menu = MainMenu()
                            if event == pg.QUIT:
                                pg.quit()
                                quit()
                else:
                    self.model.switch_turn()
                    self.view.switch_turn(self.model.turn)
        
        self.view.clock.tick(Consts.FPS)

    def pvp_game_loop(self, turn: int):
        self.view.draw_status()
        if turn == 0:
            # Turno para o jogador azul
            for event in pg.event.get():
                ev_type = event.type    # Obtém o tipo de evento
                self.view.draw_board(self.model.game_board, self.model.last_move_coords)    # Desenha o tabuleiro
                self.handle(ev_type)    # Processa o evento
                
        if turn == 1:
            # Turno para o jogador vermelho
            for event in pg.event.get():
                ev_type = event.type    # Obtém o tipo de evento
                self.view.draw_board(self.model.game_board, self.model.last_move_coords)     # Desenha o tabuleiro
                self.handle(ev_type)    # Processa o evento

    def turn_logic_human(self, row, col):
        """Lógica de turno para jogadores humanos

        Args:
            row (int): linha selecionada
            col (int): coluna selecionada
        """
        if self.model.is_choosing_current_move((row, col)):     # Verifica se o movimento selecionado está na lista de movimentos atuais
                        self.model.perform_move(self.model.selected_game_piece, (row, col))     # Executa o movimento no modelo
                        self.view.draw_board(self.model.game_board, self.model.last_move_coords)     # Desenha o tabuleiro atualizado no ecrã usando o componente view
                        self.model.moves = []       # Reinicia a lista de movimentos atuais
                        self.model.selected_game_piece = None       # Reinicia a peça selecionada
                        is_win = self.model.is_win()        # Obtém dados da vitória
                        if is_win[0]:       # Verifica se há vitória
                            play_again_button, main_menu_button = self.view.draw_win_message(is_win[1])         # Desenha mensagem de vitória e obtém referências para ambos os botões
                            self.view.draw_board(self.model.game_board, self.model.last_move_coords)         # Desenha o tabuleiro atualizado
                            while True:     # Cria novo listener de eventos para novos botões
                                for event in pg.event.get():
                                    if event.type == pg.MOUSEBUTTONDOWN:
                                        if play_again_button.is_over(pg.mouse.get_pos()):
                                            self.reset_game()
                                            
                                        elif main_menu_button.is_over(pg.mouse.get_pos()):
                                            pg.display.quit()
                                            time.sleep(0.2)
                                            from screens.main_menu import MainMenu
                                            main_menu = MainMenu()
                                    if event == pg.QUIT:
                                        pg.quit()
                                        quit()
                        else:       # Se não houver vencedor
                            self.model.switch_turn()        # Muda o turno, de Azul para Vermelho e vice-versa
                            self.view.switch_turn(self.model.turn)      # Muda a mensagem de turno no componente view               
        else:       # Se estiver a escolher uma casa que não está na lista de movimentos atuais
            if self.model.is_selecting_valid_game_piece((row, col)):    # E estiver a escolher outra peça válida
                self.model.moves = self.model.get_possible_moves((row, col))    # Atualiza a lista de movimentos atuais
                print(f'possible moves: {self.model.moves}')    # Imprime a nova lista de movimentos
                self.model.selected_game_piece = (row, col)     # Atualiza a peça selecionada no componente model
                self.view.draw_possible_moves(self.model.moves) # Desenha novos movimentos no tabuleiro usando o componente view            
    
    def handle(self, event):
        """Processa eventos do pygame

        Args:
            event ([type]): tipo de evento
        """
        if event is pg.QUIT:
            # Processa clique no botão de sair do SO
            pg.quit()
            quit()
        
        elif event == pg.MOUSEBUTTONDOWN:
            mouse_loc = pg.mouse.get_pos() # Obtém posição do rato
            if self.view.close_button.is_over(mouse_loc):
                # Processa clique no botão de sair do jogo
                pg.display.quit()
                time.sleep(0.2)
                from screens.main_menu import MainMenu
                main_menu = MainMenu()
            elif self.view.save_button.is_over(mouse_loc):
                # Processa clique no botão Guardar
                game_state = SaveManager.prepare_game_state(self)
                if SaveManager.save_game(game_state):
                    # Exibe mensagem de sucesso temporária
                    self.show_save_message("Jogo salvo com sucesso!")
                else:
                    # Exibe mensagem de erro temporária
                    self.show_save_message("Erro ao salvar o jogo!", error=True)
            else:
                # Processa clique no ecrã, não no botão de sair
                col, row = self.view.mouse_to_board(mouse_loc) # Obtém linha e coluna selecionadas
                if col == row == -1:
                    pass
                else:
                    print(f'col: {col}, row: {row}')
                    
                    self.turn_logic_human(row, col)
                    
    def show_save_message(self, message, error=False):
        """Mostra uma mensagem temporária após salvar o jogo
        
        Args:
            message (str): Mensagem a ser exibida
            error (bool): True se for uma mensagem de erro, False se for de sucesso
        """
        # Define a cor da mensagem (verde para sucesso, vermelho para erro)
        color = (255, 0, 0) if error else (0, 128, 0)
        
        # Renderiza a mensagem
        font = pg.font.Font(None, 36)
        text = font.render(message, True, color)
        text_rect = text.get_rect(center=(500, 500))
        
        # Desenha a mensagem na tela
        self.view.display.blit(text, text_rect)
        pg.display.flip()
        
        # Espera um segundo antes de continuar
        pg.time.wait(1000)

    def reset_game(self):
        """Reinicia o jogo
        """
        self.model.reset()
        self.view.start_time = pg.time.get_ticks()  # Reinicia o temporizador usando pygame.time.get_ticks()
        self.view.last_update = 0
        self.view.elapsed_time = 0
        self.view.game_time = "00:00:00"
        
        # Armazena as configurações atuais para recriação
        is_aixai = self.is_aixai
        
        if is_aixai:
            # Se for modo IAxIA, armazena as configurações das IAs
            blue_ai_instance = self.blue_ai
            red_ai_instance = self.red_ai
            
            # Fecha a tela atual
            pg.display.quit()
            time.sleep(0.2)
            
            # Cria um novo controlador com as mesmas IAs
            if isinstance(blue_ai_instance, RandomAI):
                blue_ai_config = "random"
            elif isinstance(blue_ai_instance, AI):
                blue_ai_config = ("minimax", blue_ai_instance.max_depth)
            elif isinstance(blue_ai_instance, NegamaxAI):
                blue_ai_config = ("negamax", blue_ai_instance.max_depth)
                
            if isinstance(red_ai_instance, RandomAI):
                red_ai_config = "random"
            elif isinstance(red_ai_instance, AI):
                red_ai_config = ("minimax", red_ai_instance.max_depth)
            elif isinstance(red_ai_instance, NegamaxAI):
                red_ai_config = ("negamax", red_ai_instance.max_depth)
                
            # Cria um novo jogo com as mesmas configurações
            from MVC.controller import Controller
            new_controller = Controller(True, "aixai", blue_ai=blue_ai_config, red_ai=red_ai_config)
        else:
            # Para outros modos, apenas reseta o jogo
            self.model.reset()
            self.view.reset()
            
            # Inicializa os contadores para detecção de ciclos
            self.model.last_moves = []
            self.model.forbidden_move = None
            self.model.move_history = []
            self.model.cycle_detected = False
            
            # Retorna ao início do loop principal
            self.main_loop()

    def aixai_game_loop(self):
        """Loop principal do jogo IAxIA"""
        while True:
            # Processa eventos do pygame
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    quit()
                elif event.type == pg.MOUSEBUTTONDOWN:
                    mouse_loc = pg.mouse.get_pos()
                    if self.view.close_button.is_over(mouse_loc):
                        pg.display.quit()
                        time.sleep(0.2)
                        from screens.main_menu import MainMenu
                        main_menu = MainMenu()
                    elif self.view.stop_button.is_over(mouse_loc) and not self.view.is_paused:
                        self.view.is_paused = True
                        self.view.show_resume_button = True  # Mostra o botão resume quando pausa
                    elif self.view.resume_button.is_over(mouse_loc) and self.view.is_paused:
                        self.view.is_paused = False
                        self.view.show_resume_button = False  # Esconde o botão resume quando resume
            
            # Se o jogo estiver pausado, continua o loop sem fazer movimentos
            if self.view.is_paused:
                self.view.draw_board(self.model.game_board, self.model.last_move_coords)
                self.view.clock.tick(Consts.FPS)
                continue
            
            # Seleciona a IA apropriada baseada no turno
            current_ai = self.blue_ai if self.model.turn == 0 else self.red_ai
            
            # Atualiza o temporizador antes de começar o processamento da IA
            self.view.draw_board(self.model.game_board, self.model.last_move_coords)
            pg.display.flip()
            
            # Obtém e executa o melhor movimento
            best_move = current_ai.get_best_move()
            
            # Atualiza o temporizador após o processamento da IA
            self.view.draw_board(self.model.game_board, self.model.last_move_coords)
            pg.display.flip()
            
            if best_move:
                start, end = best_move
                
                # Verifica se o movimento está proibido devido a repetição do mesmo jogador
                if self.model.forbidden_move and (start, end) == self.model.forbidden_move:
                    # Se estiver proibido, tenta obter outro movimento
                    best_move = current_ai.get_alternative_move()
                    if best_move:
                        start, end = best_move
                    else:
                        # Se não houver alternativa, o jogo termina
                        break
                
                # Verifica se foi detectado um ciclo entre os dois jogadores
                if self.model.cycle_detected:
                    # Se um ciclo foi detectado, força um movimento alternativo
                    alternative_move = current_ai.get_alternative_move()
                    if alternative_move:
                        start, end = alternative_move
                        # Reseta o estado de detecção de ciclo após forçar um movimento alternativo
                        self.model.cycle_detected = False
                        self.model.move_history = []
                    else:
                        # Se não houver alternativa, o jogo termina
                        break
                
                # Verifica se é um movimento vitorioso
                if self.model.is_winning_move(start, end):
                    self.model.perform_move(start, end)
                    self.view.draw_board(self.model.game_board, self.model.last_move_coords)
                    is_win = self.model.is_win()
                    if is_win[0]:
                        play_again_button, main_menu_button = self.view.draw_win_message(is_win[1])
                        self.view.draw_board(self.model.game_board, self.model.last_move_coords)
                        while True:
                            for event in pg.event.get():
                                if event.type == pg.MOUSEBUTTONDOWN:
                                    if play_again_button.is_over(pg.mouse.get_pos()):
                                        self.reset_game()
                                    elif main_menu_button.is_over(pg.mouse.get_pos()):
                                        pg.display.quit()
                                        time.sleep(0.2)
                                        from screens.main_menu import MainMenu
                                        main_menu = MainMenu()
                                if event == pg.QUIT:
                                    pg.quit()
                                    quit()
                        break
                
                # Executa o movimento
                self.model.perform_move(start, end)
                self.view.draw_board(self.model.game_board, self.model.last_move_coords)
                
                # Atualiza o controle de movimentos repetidos do mesmo jogador
                self.model.last_moves.append((start, end))
                if len(self.model.last_moves) > 3:
                    self.model.last_moves.pop(0)
                
                # Verifica se houve 3 movimentos iguais do mesmo jogador
                if len(self.model.last_moves) == 3 and all(move == self.model.last_moves[0] for move in self.model.last_moves):
                    self.model.forbidden_move = self.model.last_moves[0]
                    # Limpa a lista de movimentos após proibir um movimento
                    self.model.last_moves = []
                
                # Atualiza o histórico de movimentos para detecção de ciclos entre jogadores
                self.model.move_history.append((self.model.turn, start, end))
                
                # Detecta ciclos de 3 movimentos por jogador (6 movimentos no total)
                if len(self.model.move_history) >= 6:
                    # Verifica se há um padrão repetitivo com os últimos 6 movimentos
                    # O padrão deve ser: jogador1-jogada1, jogador2-jogada2, jogador1-jogada1, jogador2-jogada2, jogador1-jogada1, jogador2-jogada2
                    last_6_moves = self.model.move_history[-6:]
                    
                    # Verifica se os turnos alternam corretamente
                    turns_alternate = all(last_6_moves[i][0] != last_6_moves[i+1][0] for i in range(5))
                    
                    # Verifica se os mesmos movimentos estão sendo repetidos
                    player1_moves_same = (last_6_moves[0][1:] == last_6_moves[2][1:] == last_6_moves[4][1:])
                    player2_moves_same = (last_6_moves[1][1:] == last_6_moves[3][1:] == last_6_moves[5][1:])
                    
                    if turns_alternate and player1_moves_same and player2_moves_same:
                        # Ciclo detectado - marca para forçar um movimento diferente no próximo turno
                        self.model.cycle_detected = True
                        # Limita o tamanho do histórico para evitar crescimento excessivo
                        self.model.move_history = self.model.move_history[-6:]
                    
                    # Limita o tamanho do histórico para evitar crescimento excessivo
                    if len(self.model.move_history) > 10:
                        self.model.move_history = self.model.move_history[-10:]
                
                self.model.switch_turn()
                time.sleep(0.5)  # Pequena pausa para visualização
            else:
                # Se não houver movimentos possíveis, o jogo termina
                break
                
            self.view.clock.tick(Consts.FPS)

    @staticmethod
    def load_saved_game():
        """Carrega um jogo salvo
        
        Returns:
            Controller: Nova instância do Controller com o jogo carregado, ou None se falhar
        """
        # Carrega o estado do jogo
        game_state = SaveManager.load_game()
        if not game_state:
            return None
        
        # Cria uma nova instância do Controller com base no modo de jogo, mas sem iniciar o loop
        is_pve = game_state['is_pve']
        is_aixai = game_state['is_aixai']
        
        # Determina os parâmetros para criar o controller
        if is_aixai:
            # Prepara as configurações para IAxIA
            blue_ai_config = (game_state['blue_ai_type'], game_state['blue_ai_depth']) if game_state['blue_ai_type'] != 'random' else 'random'
            red_ai_config = (game_state['red_ai_type'], game_state['red_ai_depth']) if game_state['red_ai_type'] != 'random' else 'random'
            controller = Controller(True, "aixai", blue_ai=blue_ai_config, red_ai=red_ai_config, start_loop=False)
        elif is_pve:
            # Prepara as configurações para PvE
            ai_type = game_state['ai_type']
            ai_depth = game_state.get('ai_depth', 4)
            controller = Controller(True, ai_type, ai_depth, start_loop=False)
        else:
            # Modo PvP
            controller = Controller(False, start_loop=False)
        
        # Atualiza o estado do jogo na nova instância
        controller.model.game_board = np.array(game_state['game_board'], dtype=int)
        controller.model.turn = game_state['turn']
        controller.model.selected_game_piece = game_state['selected_game_piece']
        controller.model.moves = game_state['moves']
        controller.model.last_move_coords = game_state['last_move_coords']
        controller.model.last_moves = game_state['last_moves']
        controller.model.forbidden_move = game_state['forbidden_move']
        controller.model.move_history = game_state['move_history']
        controller.model.cycle_detected = game_state['cycle_detected']
        
        # Atualiza o tempo de jogo
        controller.view.elapsed_time = game_state['elapsed_time']
        controller.view.game_time = game_state['game_time']
        
        # Ajusta o tempo inicial para manter a contagem de tempo correta
        current_time = pg.time.get_ticks()
        controller.view.start_time = current_time - (controller.view.elapsed_time * 1000)
        
        # Atualiza a mensagem de turno no componente view
        controller.view.switch_turn(controller.model.turn)
        
        # Agora que tudo está configurado, inicia o loop principal
        controller.main_loop()
        
        # Retorna a nova instância do controller
        return controller