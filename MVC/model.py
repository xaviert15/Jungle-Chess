import numpy as np
from assets.consts import Consts
import random


class Model:
    def __init__(self) -> None:
        board = [[-7, 0, 0, 0, 0, -5],
                 [0, -4, 0, 0, -2, 0],
                 [-1, 0, 0, 0, 0, -8],
                 [0, 0, 0, 0, 0, 0],
                 [8, 0, 0, 0, 0, 1],
                 [0, 2, 0, 0, 4, 0],
                 [5, 0, 0, 0, 0, 7]]
        self.game_board = np.asarray(board, dtype=int)    # Converte a variável do tabuleiro num array numpy
        self.moves = []
        self.selected_game_piece = None
        self.turn = 0
        self.last_move_coords = None # Guarda as coordenadas (start, end) da última jogada
        # Adiciona controle de movimentos repetidos
        self.last_moves = []  # Lista para armazenar os últimos movimentos
        self.forbidden_move = None  # Movimento proibido após 3 repetições
        # Adiciona controle de ciclos de movimentos entre os dois jogadores
        self.move_history = []  # Lista para armazenar o histórico de movimentos
        self.cycle_detected = False  # Flag para indicar se um ciclo foi detectado
        # Adiciona histórico de estados do tabuleiro e controle de repetições
        self.board_states = []  # Lista para armazenar estados anteriores do tabuleiro
        self.repeated_states_count = {}  # Contador de estados repetidos
        self.random_factor = 0.1  # Fator de aleatoriedade inicial
    
    def is_outside_r_edge(self, pos_x: int) -> bool:
        """Verifica se a posição X está fora da borda direita do tabuleiro

        Args:
            pos_x (int): Posição X a verificar

        Returns:
            bool: está fora da borda direita do tabuleiro
        """
        return True if pos_x >= 6 else False
    
    def is_outside_l_edge(self, pos_x: int) -> bool:
        """Verifica se a posição X está fora da borda esquerda do tabuleiro

        Args:
            pos_x (int): Posição X a verificar

        Returns:
            bool: está fora da borda esquerda do tabuleiro
        """
        return True if pos_x < 0 else False
    
    def is_outside_u_edge(self, pos_y: int) -> bool:
        """Verifica se a posição Y está fora da borda superior do tabuleiro

        Args:
            pos_y (int): Posição Y a verificar

        Returns:
            bool: está fora da borda superior do tabuleiro
        """
        return True if pos_y < 0 else False
    
    def is_outside_d_edge(self, pos_y: int) -> bool:
        """Verifica se a posição Y está fora da borda inferior do tabuleiro

        Args:
            pos_y (int): Posição Y a verificar

        Returns:
            bool: está fora da borda inferior do tabuleiro
        """
        return True if pos_y >= 7 else False
    
    def is_overlapping_own_den(self, pos, rank: int) -> bool:
        """Verifica se a posição possível de uma peça está a cobrir a sua própria toca

        Args:
            pos (tuple(int, int)): Posição possível da peça
            rank (int): Rank da peça (Positivo para jogador azul, negativo para jogador vermelho)

        Returns:
            bool: está a cobrir a posição da sua própria toca
        """
        if (rank < 0 and pos == (0, 3)) or (rank > 0 and pos == (6, 2)):
            return True
        
        return False
    
    def is_self_rank_higher(self, rank_a: int, rank_b: int) -> bool:
        """Compara rank e other_rank para determinar se a peça rank_a pode comer a peça rank_b

        Args:
            rank_a (int): Rank da possível peça que come
            rank_b (int): Rank da peça a ser comida

        Returns:
            bool: rank pode comer other_rank
        """
        # Verifica se as peças são do mesmo time
        if (rank_a > 0 and rank_b > 0) or (rank_a < 0 and rank_b < 0):
            return False

        # Encontra a posição da peça a ser comida (rank_b)
        pos_b = None
        for i in range(7):
            for j in range(6):
                if self.game_board[i, j] == rank_b:
                    pos_b = (i, j)
                    break
            if pos_b:
                break

        # Encontra a posição da peça que come (rank_a)
        pos_a = None
        for i in range(7):
            for j in range(6):
                if self.game_board[i, j] == rank_a:
                    pos_a = (i, j)
                    break
            if pos_a:
                break

        # Se não encontrar uma das posições, retorna False
        if pos_a is None or pos_b is None:
            return False

        # Verifica se a peça está em uma armadilha do adversário
        if rank_b > 0:  # Peça azul
            if pos_b in [(0, 2), (0, 4), (1, 3)]:  # Armadilhas vermelhas
                return True
        else:  # Peça vermelha
            if pos_b in [(6, 1), (6, 3), (5, 2)]:  # Armadilhas azuis
                return True

        # Se não estiver em armadilha, continua com as regras normais
        rank_a = abs(rank_a)
        rank_b = abs(rank_b)

        # Regra especial para Ratos (rank 1)
        if rank_a == 1 and rank_b == 1:
            # Verifica se ambos estão no rio ou ambos em terra
            is_a_in_river = (pos_a[1] in (1, 4) and 2 < pos_a[0] < 5) or \
                          (pos_a[1] in (1, 4) and pos_a[0] == 2)
            is_b_in_river = (pos_b[1] in (1, 4) and 2 < pos_b[0] < 5) or \
                          (pos_b[1] in (1, 4) and pos_b[0] == 2)
            
            return is_a_in_river == is_b_in_river

        # Regra especial para Rato vs Elefante
        if rank_a == 1 and rank_b == 8:
            # Verifica se o rato está no rio
            is_a_in_river = (pos_a[1] in (1, 4) and 2 < pos_a[0] < 5) or \
                          (pos_a[1] in (1, 4) and pos_a[0] == 2)
            
            # O rato só pode capturar o elefante se não estiver no rio
            return not is_a_in_river

        # Regras normais para outras peças...
        if rank_a == 1 and rank_b in (0, 1, 8):
            return True
        
        if rank_a == 2 and rank_b <= 2:
            return True
        
        if rank_a == 3 and rank_b <= 3:
            return True
        
        if rank_a == 4 and rank_b <= 4:
            return True
        
        if rank_a == 5 and rank_b <= 5:
            return True
        
        if rank_a == 6 and rank_b <= 6:
            return True
        
        if rank_a == 7 and rank_b <= 7:
            return True
        
        if rank_a == 8 and rank_b in (0, 2, 3, 4, 5, 6, 7, 8):
            return True
        
        return False
            
    def get_directions_to_river(self, pos):
        """Gera uma lista de direções adjacentes aos rios para uma peça dada

        Args:
            pos (tuple(int, int)): posição da peça

        Returns:
            list[str]: lista de direções para os rios
        """
        directions = []

        # Verifica se a peça está à direita do rio
        if pos[1] == 2 and 2 < pos[0] < 5:
            directions.append((0, -1))
        
        # Verifica se a peça está à esquerda do rio
        if pos[1] == 3 and 2 < pos[0] < 5:
            directions.append((0, 1))
        
        # Verifica se a peça está acima do rio
        if pos[1] in (1, 4) and pos[0] == 2:
            directions.append((1, 0))
        
        # Verifica se a peça está abaixo do rio
        if pos[1] in (1, 4) and pos[0] == 4:
            directions.append((-1, 0))
        
        return directions
    
    def land_logic(self, pos, rank: int):
        """Lógica de movimento para peças terrestres: Gato, Cão, Lobo, Leopardo, Elefante

        Args:
            pos (tuple(int, int)): posição atual da peça
            rank (int): rank da peça atual
        """

        directions_to_river = self.get_directions_to_river(pos)
        moves = []
        if len(directions_to_river) == 0:
            for dir in Consts.DIRECTIONS:
                if not self.is_outside_r_edge(pos[1] + dir[1]): 
                    if not self. is_outside_l_edge(pos[1] + dir[1]):
                        if not self.is_outside_u_edge(pos[0] + dir[0]):
                            if not self.is_outside_d_edge(pos[0] + dir[0]):
                                # Verifica se a posição de destino é rio
                                new_pos = (pos[0] + dir[0], pos[1] + dir[1])
                                if not ((new_pos[1] in (1, 4) and 2 < new_pos[0] < 5) or \
                                      (new_pos[1] in (1, 4) and new_pos[0] == 2)):
                                    if self.is_self_rank_higher(rank, self.game_board[new_pos[0], new_pos[1]]):
                                        if not self.is_overlapping_own_den(new_pos, rank):
                                            moves.append(new_pos)
        
        else:
            DIR = Consts.DIRECTIONS.copy()
            for direction in directions_to_river:
                DIR.remove(direction)
            
            for dir in DIR:
                if not self.is_outside_r_edge(pos[1] + dir[1]): 
                    if not self. is_outside_l_edge(pos[1] + dir[1]):
                        if not self.is_outside_u_edge(pos[0] + dir[0]):
                            if not self.is_outside_d_edge(pos[0] + dir[0]):
                                # Verifica se a posição de destino é rio
                                new_pos = (pos[0] + dir[0], pos[1] + dir[1])
                                if not ((new_pos[1] in (1, 4) and 2 < new_pos[0] < 5) or \
                                      (new_pos[1] in (1, 4) and new_pos[0] == 2)):
                                    if self.is_self_rank_higher(rank, self.game_board[new_pos[0], new_pos[1]]):
                                        if not self.is_overlapping_own_den(new_pos, rank):
                                            moves.append(new_pos)
        
        return moves
    
    def land_river_logic(self, pos, rank: int):
        """Lógica de movimento para peças terrestres-aquáticas: Rato

        Args:
            pos (tuple(int, int)): posição atual da peça
            rank (int): rank da peça atual
        """
        moves = []
        for dir in Consts.DIRECTIONS:
            if not self.is_outside_r_edge(pos[1] + dir[1]): 
                    if not self. is_outside_l_edge(pos[1] + dir[1]):
                        if not self.is_outside_u_edge(pos[0] + dir[0]):
                            if not self.is_outside_d_edge(pos[0] + dir[0]):
                                if self.is_self_rank_higher(rank, self.game_board[pos[0] + dir[0], pos[1] + dir[1]]):
                                    if not self.is_overlapping_own_den((pos[0] + dir[0], pos[1] + dir[1]), rank):
                                        moves.append((pos[0] + dir[0], pos[1] + dir[1]))
        
        return moves

    def is_river(self, pos):
        """Verifica se uma posição é rio

        Args:
            pos (tuple(int, int)): posição a verificar (linha, coluna)

        Returns:
            bool: True se a posição é rio, False caso contrário
        """
        row, col = pos
        # Rio nas colunas 1 e 4, entre as linhas 2 e 4
        return col in (1, 4) and 2 <= row <= 4

    def land_jump_logic(self, pos, rank: int):
        """Lógica de movimento para peças terrestres com salto: Tigre, Leão

        Args:
            pos (tuple(int, int)): posição atual da peça
            rank (int): rank da peça atual
        """
        moves = []
        row, col = pos
        
        # Movimentos normais (sem rio)
        for dir in Consts.DIRECTIONS:
            new_row, new_col = row + dir[0], col + dir[1]
            if (0 <= new_row < 7 and 0 <= new_col < 6):  # Dentro do tabuleiro
                new_pos = (new_row, new_col)
                if not self.is_river(new_pos):
                    if self.is_self_rank_higher(rank, self.game_board[new_row, new_col]):
                        if not self.is_overlapping_own_den(new_pos, rank):
                            moves.append(new_pos)

        # Lógica especial para o Leão (rank 7)
        if abs(rank) == 7:
            # Saltos horizontais sobre o rio
            if 2 <= row <= 4:  # Entre as linhas 2 e 4 (inclusive)
                # Salto para a esquerda
                if col == 2:  # Se estiver à direita da coluna 1
                    target_pos = (row, 0)
                    path_clear = True
                    # Verifica se há ratos no caminho
                    if abs(self.game_board[row, 1]) == 1:  # Se for um rato
                        path_clear = False
                    if path_clear and self.is_self_rank_higher(rank, self.game_board[target_pos[0], target_pos[1]]):
                        moves.append(target_pos)
                elif col == 5:  # Se estiver à direita da coluna 4
                    target_pos = (row, 3)
                    path_clear = True
                    # Verifica se há ratos no caminho
                    if abs(self.game_board[row, 4]) == 1:  # Se for um rato
                        path_clear = False
                    if path_clear and self.is_self_rank_higher(rank, self.game_board[target_pos[0], target_pos[1]]):
                        moves.append(target_pos)
                
                # Salto para a direita
                if col == 0:  # Se estiver à esquerda da coluna 1
                    target_pos = (row, 2)
                    path_clear = True
                    # Verifica se há ratos no caminho
                    if abs(self.game_board[row, 1]) == 1:  # Se for um rato
                        path_clear = False
                    if path_clear and self.is_self_rank_higher(rank, self.game_board[target_pos[0], target_pos[1]]):
                        moves.append(target_pos)
                elif col == 3:  # Se estiver à esquerda da coluna 4
                    target_pos = (row, 5)
                    path_clear = True
                    # Verifica se há ratos no caminho
                    if abs(self.game_board[row, 4]) == 1:  # Se for um rato
                        path_clear = False
                    if path_clear and self.is_self_rank_higher(rank, self.game_board[target_pos[0], target_pos[1]]):
                        moves.append(target_pos)
            
            # Saltos verticais sobre o rio
            if col in (1, 4):  # Nas colunas do rio
                # Salto para cima
                if row == 5:  # Na linha 5
                    target_pos = (1, col)
                    path_clear = True
                    # Verifica se há ratos no caminho
                    for r in range(2, 5):
                        if abs(self.game_board[r, col]) == 1:  # Se for um rato
                            path_clear = False                        
                    if path_clear and self.is_self_rank_higher(rank, self.game_board[target_pos[0], target_pos[1]]):
                        moves.append(target_pos)
                
                # Salto para baixo
                if row == 1:  # Na linha 2
                    target_pos = (5, col)
                    path_clear = True
                    # Verifica se há ratos no caminho
                    for r in range(2, 5):
                        if abs(self.game_board[r, col]) == 1:  # Se for um rato
                            path_clear = False                        
                    if path_clear and self.is_self_rank_higher(rank, self.game_board[target_pos[0], target_pos[1]]):
                        moves.append(target_pos)
        
        return moves

    def get_possible_moves(self, position):
        """Retorna os movimentos possíveis de uma peça para uma posição dada

        Args:
            position (tuple(int, int)): posição dada
        """
        
        moves = None      # Gera movimentos possíveis
        current_rank = self.game_board[position[0], position[1]]    # Obtém o rank atual

        if current_rank == 0:
            return None
        
        elif abs(current_rank) == 1: # Rato
            moves = self.land_river_logic(position, current_rank)
        elif abs(current_rank) == 2: # Gato
            moves = self.land_logic(position, current_rank)
        elif abs(current_rank) == 3: # Cão
            moves = self.land_logic(position, current_rank)
        elif abs(current_rank) == 4: # Lobo
            moves = self.land_logic(position, current_rank)
        elif abs(current_rank) == 5: # Leopardo
            moves = self.land_logic(position, current_rank)
        elif abs(current_rank) == 6: # Tigre
            moves = self.land_jump_logic(position, current_rank)
        elif abs(current_rank) == 7: # Leão
            moves = self.land_jump_logic(position, current_rank)
            
        elif abs(current_rank) == 8: # Elefante
            moves = self.land_logic(position, current_rank)
        
        return moves

    def is_choosing_current_move(self, pos) -> bool:
        """Verifica se a posição selecionada está na lista de movimentos atuais

        Args:
            pos (tuple(int, int)): Posição selecionada

        Returns:
            bool: resposta da consulta
        """
        return True if pos in self.moves and self.selected_game_piece is not None else False
    
    def is_selecting_valid_game_piece(self, pos) -> bool:
        """Verifica se o jogador está a clicar numa peça válida e não nas peças do oponente ou num espaço vazio

        Args:
            pos (tuple(int, int)): posição selecionada

        Returns:
            bool: resposta da consulta
        """
        return True if (self.game_board[pos[0], pos[1]] > 0 and self.turn == 0) or (self.game_board[pos[0], pos[1]] < 0 and self.turn == 1) else False
    
    def perform_move(self, start_place, selected_move) -> None:
        """Move uma peça da posição original para a posição selecionada

        Args:
            game_piece (tuple(int, int)): posição da peça a mover
            selected_move (tuple(int, int)): posição selecionada
        """
        self.game_board[selected_move[0], selected_move[1]] = self.game_board[start_place[0], start_place[1]]
        self.game_board[start_place[0], start_place[1]] = 0
        self.last_move_coords = (start_place, selected_move) # Regista a última jogada
        
        # Adiciona o movimento ao histórico para controle de repetições
        self.last_moves.append((start_place, selected_move))
        
        # Mantém apenas os últimos 12 movimentos (6 pares de jogadas)
        if len(self.last_moves) > 12:
            self.last_moves.pop(0)
        
        # Armazena o estado atual do tabuleiro para detectar repetições
        current_state = self.game_board.tobytes()
        self.board_states.append(current_state)
        
        # Mantém apenas os últimos 20 estados do tabuleiro
        if len(self.board_states) > 20:
            self.board_states.pop(0)
        
        # Conta ocorrências de cada estado
        if current_state in self.repeated_states_count:
            self.repeated_states_count[current_state] += 1
        else:
            self.repeated_states_count[current_state] = 1
        
        # Se um estado se repete demais, aumenta o fator de aleatoriedade
        if self.repeated_states_count[current_state] >= 3:
            self.random_factor = 0.5  # Aumenta significativamente a aleatoriedade
            self.cycle_detected = True
        elif self.repeated_states_count[current_state] >= 2:
            self.random_factor = 0.3  # Aumenta moderadamente a aleatoriedade
            self.cycle_detected = True
        
        # Verifica se ocorreu uma repetição de movimentos (ciclo)
        self.check_move_repetition()

    def check_move_repetition(self) -> None:
        """Verifica se há repetição de movimentos e define um movimento proibido se necessário"""
        # Precisamos de pelo menos 6 movimentos para detectar ciclos de 3 pares de jogadas
        if len(self.last_moves) < 6:
            return
        
        # Verifica ciclos de 2 movimentos que se repetem 3 vezes
        if len(self.last_moves) >= 6:
            # Verifica se os últimos 6 movimentos formam um padrão de repetição
            if (self.last_moves[-6] == self.last_moves[-4] == self.last_moves[-2] and 
                self.last_moves[-5] == self.last_moves[-3] == self.last_moves[-1]):
                # Define o último movimento como proibido para o próximo turno
                self.forbidden_move = self.last_moves[-2]
                self.cycle_detected = True
                return
        
        # Verifica ciclos de 4 movimentos que se repetem 2 vezes
        if len(self.last_moves) >= 8:
            # Verifica se os últimos 8 movimentos formam um padrão de repetição
            if (self.last_moves[-8] == self.last_moves[-4] and 
                self.last_moves[-7] == self.last_moves[-3] and
                self.last_moves[-6] == self.last_moves[-2] and
                self.last_moves[-5] == self.last_moves[-1]):
                # Define o último movimento como proibido para o próximo turno
                self.forbidden_move = self.last_moves[-4]
                self.cycle_detected = True
                return
                
        # Verifica ciclos de 6 movimentos que se repetem 2 vezes
        if len(self.last_moves) >= 12:
            # Verifica se os últimos 12 movimentos formam um padrão de repetição
            if (self.last_moves[-12] == self.last_moves[-6] and 
                self.last_moves[-11] == self.last_moves[-5] and
                self.last_moves[-10] == self.last_moves[-4] and
                self.last_moves[-9] == self.last_moves[-3] and
                self.last_moves[-8] == self.last_moves[-2] and
                self.last_moves[-7] == self.last_moves[-1]):
                # Define os últimos movimentos como proibidos
                self.forbidden_move = self.last_moves[-6]
                self.cycle_detected = True
                return
        
        # Se não detectou ciclos específicos, mas temos estados repetidos, mantém o ciclo detectado
        if not self.cycle_detected:
            # Verifica se algum estado se repete mais de uma vez
            for state in self.board_states:
                if self.board_states.count(state) >= 3:
                    self.cycle_detected = True
                    return
        
        # Se não detectou ciclos, limpa o movimento proibido
        self.forbidden_move = None
        self.cycle_detected = False

    def switch_turn(self) -> None:
        """Muda o turno de 0 (Azul) para 1 (Vermelho) e vice-versa
        """
        self.turn = 0 if self.turn == 1 else 1
        self.selected_game_piece = None
        
        # Não resetamos mais o controle de movimentos repetidos para permitir
        # a detecção de ciclos entre os dois jogadores
        
        # Apenas limpa o movimento proibido se não houver ciclo detectado
        if not self.cycle_detected:
            self.forbidden_move = None
            self.random_factor = 0.1  # Retorna ao fator de aleatoriedade normal

    def is_win(self):
        """Verifica se há um vencedor, de acordo com as regras

        Returns:
            tuple(bool, str): tuplo que contém bool se houver vitória e uma str que indica qual jogador venceu
        """
        winning_player = ''
        is_win = False
        # Verifica vitória para o jogador azul
        if self.game_board[0, 3] > 0 or (self.game_board >= 0).all():
            # print('blue win') # REMOVIDO
            is_win = True
            winning_player = 'Azul'
            
        
        # Verifica vitória para o jogador vermelho
        if self.game_board[6, 2] < 0 or (self.game_board <= 0).all():
            # print('red win') # REMOVIDO
            is_win = True
            winning_player = 'Vermelho'
        
        return (is_win, winning_player)
    
    def reset(self) -> None:
        """Reinicia o modelo para o seu estado inicial
        """
        board = [[-7, 0, 0, 0, 0, -5],
                 [0, -4, 0, 0, -2, 0],
                 [-1, 0, 0, 0, 0, -8],
                 [0, 0, 0, 0, 0, 0],
                 [8, 0, 0, 0, 0, 1],
                 [0, 2, 0, 0, 4, 0],
                 [5, 0, 0, 0, 0, 7]]
        self.game_board = np.asarray(board, dtype=int)    # Converte a variável do tabuleiro num array numpy
        self.moves = []
        self.selected_game_piece = None
        self.turn = 0
        # Reseta o controle de movimentos repetidos
        self.last_moves = []
        self.forbidden_move = None
        # Reseta o controle de ciclos
        self.move_history = []
        self.cycle_detected = False
        # Reseta o histórico de estados do tabuleiro
        self.board_states = []
        self.repeated_states_count = {}
        self.random_factor = 0.1

    def is_piece_safe_in_trap(self, pos: tuple, piece: int) -> bool:
        """Verifica se uma peça está segura em uma armadilha (não pode ser capturada)

        Args:
            pos (tuple): Posição da peça
            piece (int): Valor da peça

        Returns:
            bool: True se a peça está segura, False caso contrário
        """
        # Verifica todas as peças adjacentes
        for dir in Consts.DIRECTIONS:
            new_pos = (pos[0] + dir[0], pos[1] + dir[1])
            if not (self.is_outside_r_edge(new_pos[1]) or 
                   self.is_outside_l_edge(new_pos[1]) or 
                   self.is_outside_u_edge(new_pos[0]) or 
                   self.is_outside_d_edge(new_pos[0])):
                adjacent_piece = self.game_board[new_pos[0], new_pos[1]]
                if adjacent_piece != 0:
                    # Se a peça adjacente for do oponente e puder capturar
                    if (piece < 0 and adjacent_piece > 0) or (piece > 0 and adjacent_piece < 0):
                        if self.is_self_rank_higher(adjacent_piece, piece):
                            return False
        return True

    def is_winning_move(self, start: tuple, end: tuple) -> bool:
        """Verifica se um movimento leva à vitória

        Args:
            start (tuple): posição inicial (linha, coluna)
            end (tuple): posição final (linha, coluna)

        Returns:
            bool: True se o movimento leva à vitória, False caso contrário
        """
        # Faz uma cópia do tabuleiro para simular o movimento
        temp_board = self.game_board.copy()
        piece_value = temp_board[end[0], end[1]]
        temp_board[end[0], end[1]] = temp_board[start[0], start[1]]
        temp_board[start[0], start[1]] = 0
        
        # Verifica se o movimento leva à vitória
        if self.turn == 0:  # Jogador azul
            return temp_board[0, 3] > 0  # Verifica se uma peça azul chegou ao covil vermelho
        else:  # Jogador vermelho
            return temp_board[6, 2] < 0  # Verifica se uma peça vermelha chegou ao covil azul

    def is_valid_move(self, start: tuple, end: tuple) -> bool:
        """Verifica se é um movimento válido da posição start para a posição end

        Args:
            start (tuple): posição inicial (linha, coluna)
            end (tuple): posição final (linha, coluna)

        Returns:
            bool: True se for um movimento válido, False caso contrário
        """
        # Verifica se a posição final está na lista de movimentos possíveis
        possible_moves = self.get_possible_moves(start)
        if possible_moves is None:
            return False
        
        return end in possible_moves


class AI:
    def __init__(self, model: Model, depth: int = 4):
        self.model = model
        self.max_depth = depth  # Profundidade configurável
        
        # Cache para avaliações de posição
        self.position_cache = {}
        
        # Valores das peças (otimizados)
        self.piece_values = {
            1: 6,   # Rato
            2: 3,   # Gato
            3: 4,   # Cão
            4: 5,   # Lobo
            5: 6,   # Leopardo
            6: 7,   # Tigre
            7: 8,   # Leão
            8: 15   # Elefante - Valor aumentado significativamente
        }
        
        # Posições das armadilhas
        self.traps = [
            (0, 2), (0, 4), (1, 3),  # Armadilhas vermelhas
            (6, 1), (6, 3), (5, 2)   # Armadilhas azuis
        ]
        
        # Posições das tocas
        self.dens = [(0, 3), (6, 2)]  # (vermelho, azul)
        
        # Limite de movimentos para poda
        self.move_limit = 20  # Limita o número de movimentos avaliados por nó
        
    def evaluate_board(self) -> float:
        """Avalia o estado atual do tabuleiro com uma função de avaliação otimizada"""
        # Verifica cache
        board_key = hash(self.model.game_board.tobytes())
        if board_key in self.position_cache:
            return self.position_cache[board_key]
            
        score = 0
        
        # Verifica se o jogo terminou
        if self.model.is_win()[0]:
            if self.model.is_win()[1] == 'Vermelho':
                return float('inf')
            else:
                return float('-inf')

        # 1. Avaliação de material (pesos iguais para ambos jogadores)
        for i in range(7):
            for j in range(6):
                piece = self.model.game_board[i, j]
                if piece != 0:
                    value = self.piece_values[abs(piece)]
                    if piece < 0:  # Peça vermelha
                        score += value
                    else:  # Peça azul
                        score -= value
        
        # 2. Avaliação de posição (equilibrada para ambos os jogadores)
        closest_red_to_blue_den = float('inf')  # Distância da peça vermelha mais próxima ao covil azul
        closest_blue_to_red_den = float('inf')  # Distância da peça azul mais próxima ao covil vermelho
        
        # Pontuação por proximidade ao covil adversário - equilibrada para ambos os jogadores
        for i in range(7):
            for j in range(6):
                piece = self.model.game_board[i, j]
                if piece != 0:
                    # Progresso em direção à toca adversária
                    if piece < 0:  # Peça vermelha
                        dist_to_den = abs(i - self.dens[1][0]) + abs(j - self.dens[1][1])
                        # Guarda a distância da peça mais próxima ao covil
                        closest_red_to_blue_den = min(closest_red_to_blue_den, dist_to_den)
                        
                        # Pontuação progressiva baseada na proximidade
                        proximity_score = (8 - dist_to_den) * 6.0
                        score += proximity_score
                        
                        # Bônus adicional para peças muito próximas ao covil
                        if dist_to_den <= 1:
                            score += 500
                        elif dist_to_den <= 2:
                            score += 200
                        elif dist_to_den <= 3:
                            score += 120
                        elif dist_to_den <= 4:
                            score += 80
                    else:  # Peça azul
                        dist_to_den = abs(i - self.dens[0][0]) + abs(j - self.dens[0][1])
                        # Guarda a distância da peça mais próxima ao covil
                        closest_blue_to_red_den = min(closest_blue_to_red_den, dist_to_den)
                        
                        # Pontuação progressiva baseada na proximidade (mesmo valor que o vermelho)
                        proximity_score = (8 - dist_to_den) * 6.0
                        score -= proximity_score
                        
                        # Bônus adicional para peças muito próximas ao covil (mesmo valor que o vermelho)
                        if dist_to_den <= 1:
                            score -= 500
                        elif dist_to_den <= 2:
                            score -= 200
                        elif dist_to_den <= 3:
                            score -= 120
                        elif dist_to_den <= 4:
                            score -= 80
        
        # Bônus para vantagem na corrida para os covis - equilibrado para ambos jogadores
        if closest_red_to_blue_den < closest_blue_to_red_den:
            race_advantage = closest_blue_to_red_den - closest_red_to_blue_den
            score += race_advantage * 80
        elif closest_blue_to_red_den < closest_red_to_blue_den:
            race_advantage = closest_red_to_blue_den - closest_blue_to_red_den
            score -= race_advantage * 80  # Mesmo valor que o vermelho
            
        # Armazena em cache e retorna
        self.position_cache[board_key] = score
        return score
    
    def get_all_possible_moves(self, is_ai_turn: bool) -> list:
        """Retorna todas as possíveis jogadas para o jogador atual (otimizada)"""
        moves = []
        for i in range(7):
            for j in range(6):
                piece = self.model.game_board[i, j]
                # Verifica se a peça pertence ao jogador atual
                if (is_ai_turn and piece < 0) or (not is_ai_turn and piece > 0):
                    possible_moves = self.model.get_possible_moves((i, j))
                    if possible_moves:
                        moves.extend(((i, j), move) for move in possible_moves)
        
        # Ordena e limita o número de movimentos
        moves.sort(key=lambda x: self.evaluate_move(x), reverse=is_ai_turn)
        return moves[:self.move_limit]  # Retorna apenas os melhores movimentos
    
    def minimax(self, depth: int, alpha: float, beta: float, is_maximizing: bool, add_noise: bool = False) -> tuple:
        """Implementa o algoritmo Minimax com cortes alfa-beta"""
        if depth == 0 or self.model.is_win()[0]:
            result = self.evaluate_board()
            # Adiciona um pequeno ruído aleatório para quebrar empates e evitar loops
            if add_noise and depth == 0:
                result += random.uniform(-self.model.random_factor, self.model.random_factor) * 100
            return result, None
        
        moves = self.get_all_possible_moves(is_maximizing)
        
        # Remove o movimento proibido da lista, se existir
        if self.model.forbidden_move and self.model.cycle_detected:
            moves = [move for move in moves if move != self.model.forbidden_move]
            
        if not moves:  # Se não houver movimentos possíveis
            return self.evaluate_board(), None
            
        if is_maximizing:
            max_eval = float('-inf')
            best_move = moves[0] if moves else None
            
            # Embaralha os movimentos para introduzir variação
            if self.model.cycle_detected:
                random.shuffle(moves)
            
            for start, end in moves:
                # Faz a jogada
                piece_value = self.model.game_board[end[0], end[1]]
                self.model.game_board[end[0], end[1]] = self.model.game_board[start[0], start[1]]
                self.model.game_board[start[0], start[1]] = 0
                
                # Avalia a jogada
                eval, _ = self.minimax(depth - 1, alpha, beta, False, add_noise)
                
                # Penaliza movimentos que levam a estados repetidos
                current_state = self.model.game_board.tobytes()
                if current_state in self.model.board_states:
                    eval -= self.model.random_factor * 50  # Penalidade proporcional ao fator de aleatoriedade
                
                # Desfaz a jogada
                self.model.game_board[start[0], start[1]] = self.model.game_board[end[0], end[1]]
                self.model.game_board[end[0], end[1]] = piece_value
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = (start, end)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
                    
            return max_eval, best_move
        else:
            min_eval = float('inf')
            best_move = moves[0] if moves else None
            
            # Embaralha os movimentos para introduzir variação
            if self.model.cycle_detected:
                random.shuffle(moves)
            
            for start, end in moves:
                # Faz a jogada
                piece_value = self.model.game_board[end[0], end[1]]
                self.model.game_board[end[0], end[1]] = self.model.game_board[start[0], start[1]]
                self.model.game_board[start[0], start[1]] = 0
                
                # Avalia a jogada
                eval, _ = self.minimax(depth - 1, alpha, beta, True, add_noise)
                
                # Penaliza movimentos que levam a estados repetidos
                current_state = self.model.game_board.tobytes()
                if current_state in self.model.board_states:
                    eval += self.model.random_factor * 50  # Penalidade proporcional ao fator de aleatoriedade
                
                # Desfaz a jogada
                self.model.game_board[start[0], start[1]] = self.model.game_board[end[0], end[1]]
                self.model.game_board[end[0], end[1]] = piece_value
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = (start, end)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
                    
            return min_eval, best_move

    def get_best_move(self) -> tuple:
        """Retorna a melhor jogada para a IA"""
        # Verifica primeiro se há um movimento vitorioso direto
        all_moves = self.get_all_possible_moves(self.model.turn == 1)
        
        # Remove o movimento proibido da lista, se existir
        if self.model.forbidden_move and self.model.cycle_detected:
            all_moves = [move for move in all_moves if move != self.model.forbidden_move]
        
        # Se depois de remover o movimento proibido não sobrar nenhum movimento, 
        # retornamos todos os movimentos novamente
        if not all_moves:
            all_moves = self.get_all_possible_moves(self.model.turn == 1)
        
        for start, end in all_moves:
            # Verifica se pode entrar no covil adversário
            if (self.model.turn == 0 and end == (0, 3)) or (self.model.turn == 1 and end == (6, 2)):
                return (start, end)
            
            # Ou verifica se o movimento é vitorioso usando o método is_winning_move
            if self.model.is_winning_move(start, end):
                return (start, end)
                
        # Se não houver movimento vitorioso, continua com a lógica normal
        self.position_cache.clear()
        # Determina se é o turno da IA baseado no turno atual
        is_ai_turn = self.model.turn == 1  # Se turn == 1, é o turno da IA vermelha
        
        # Adiciona um pouco de aleatoriedade para evitar ficar preso em padrões
        if self.model.cycle_detected:
            # Adiciona uma pequena perturbação aleatória à avaliação
            add_noise = True
        else:
            add_noise = False
        
        # Corrigido: usando is_ai_turn, não 1 ou -1 para o parâmetro is_maximizing
        _, best_move = self.minimax(self.max_depth, float('-inf'), float('inf'), is_ai_turn, add_noise)
        
        # Se o melhor movimento for o movimento proibido, escolhe um alternativo
        if self.model.forbidden_move and best_move == self.model.forbidden_move and self.model.cycle_detected:
            return self.get_alternative_move()
            
        return best_move
    
    def evaluate_move(self, move: tuple) -> float:
        """Avalia um movimento específico para ordenação (otimizada)"""
        start, end = move
        score = 0
        piece = self.model.game_board[start[0], start[1]]
        
        # Movimento para o covil adversário - prioridade máxima absoluta para ambos os jogadores
        if (self.model.turn == 0 and end == (0, 3)) or (self.model.turn == 1 and end == (6, 2)):
            return float('inf')  # Prioridade igual para ambos
        
        # Movimento para uma célula adjacente ao covil adversário - equalizado para ambos jogadores
        if self.model.turn == 0:  # Jogador azul
            if end in [(0, 2), (0, 4), (1, 3)]:  # Células adjacentes ao covil vermelho
                # Simula o movimento
                temp_board = self.model.game_board.copy()
                temp_board[end[0], end[1]] = temp_board[start[0], start[1]]
                temp_board[start[0], start[1]] = 0
                
                # Verifica se a peça estaria segura nesta posição
                is_safe = True
                
                # Como estamos em uma armadilha adversária, verificamos se há peças inimigas adjacentes
                for dr, dc in Consts.DIRECTIONS:
                    nr, nc = end[0] + dr, end[1] + dc
                    if 0 <= nr < 7 and 0 <= nc < 6 and temp_board[nr, nc] < 0:  # Peça inimiga
                        # Verifica se a peça inimiga pode capturar nossa peça
                        if self.model.is_self_rank_higher(temp_board[nr, nc], temp_board[end[0], end[1]]):
                            is_safe = False
                            break
                
                if is_safe:
                    return float('inf') * 0.995  # Prioridade extremamente alta
                else:
                    # Mesmo valor para ambos jogadores
                    score += 50
        else:  # Jogador vermelho
            if end in [(6, 1), (6, 3), (5, 2)]:  # Células adjacentes ao covil azul
                # Simula o movimento
                temp_board = self.model.game_board.copy()
                temp_board[end[0], end[1]] = temp_board[start[0], start[1]]
                temp_board[start[0], start[1]] = 0
                
                # Verifica se a peça estaria segura nesta posição
                is_safe = True
                
                # Como estamos em uma armadilha adversária, verificamos se há peças inimigas adjacentes
                for dr, dc in Consts.DIRECTIONS:
                    nr, nc = end[0] + dr, end[1] + dc
                    if 0 <= nr < 7 and 0 <= nc < 6 and temp_board[nr, nc] > 0:  # Peça inimiga
                        # Verifica se a peça inimiga pode capturar nossa peça
                        if self.model.is_self_rank_higher(temp_board[nr, nc], temp_board[end[0], end[1]]):
                            is_safe = False
                            break
                
                if is_safe:
                    return float('inf') * 0.995  # Prioridade extremamente alta
                else:
                    # Mesmo valor para ambos jogadores
                    score += 50
        
        # Células a duas casas de distância do covil - equilibrado para ambos jogadores
        covil_vermelho_proximidade2 = [(0, 1), (0, 5), (1, 2), (1, 4), (2, 3)]
        covil_azul_proximidade2 = [(6, 0), (6, 4), (5, 1), (5, 3), (4, 2)]
        
        if self.model.turn == 0 and end in covil_vermelho_proximidade2:  # Jogador azul perto do covil vermelho
            # Verifica se há um caminho livre até uma célula adjacente ao covil
            has_path_to_den = False
            for dr, dc in Consts.DIRECTIONS:
                nr, nc = end[0] + dr, end[1] + dc
                if (nr, nc) in [(0, 2), (0, 4), (1, 3)] and self.model.is_valid_move(end, (nr, nc)):
                    has_path_to_den = True
                    break
            
            if has_path_to_den:
                score += 500  # Mesmo valor para ambos jogadores
        elif self.model.turn == 1 and end in covil_azul_proximidade2:  # Jogador vermelho perto do covil azul
            # Verifica se há um caminho livre até uma célula adjacente ao covil
            has_path_to_den = False
            for dr, dc in Consts.DIRECTIONS:
                nr, nc = end[0] + dr, end[1] + dc
                if (nr, nc) in [(6, 1), (6, 3), (5, 2)] and self.model.is_valid_move(end, (nr, nc)):
                    has_path_to_den = True
                    break
            
            if has_path_to_den:
                score += 500  # Mesmo valor para ambos jogadores
        
        # Captura de peça - equilibrada para ambos jogadores
        if self.model.game_board[end[0], end[1]] != 0:
            captured_piece = abs(self.model.game_board[end[0], end[1]])
            score += self.piece_values[captured_piece] * 2.0
        
        # Movimento em direção à toca adversária - equilibrado para ambos jogadores
        if piece < 0:  # Peças vermelhas
            dist_before = abs(start[0] - self.dens[1][0]) + abs(start[1] - self.dens[1][1])
            dist_after = abs(end[0] - self.dens[1][0]) + abs(end[1] - self.dens[1][1])
            if dist_after < dist_before:
                score += 60 * (dist_before - dist_after)
                # Bônus progressivo baseado na proximidade ao covil
                score += (7 - dist_after) * 25
                # Bônus extra para movimentos que aproximam a peça para 2 ou 3 células de distância do covil
                if dist_after == 1:
                    score += 250
                elif dist_after == 2:
                    score += 150
                elif dist_after == 3:
                    score += 100
                elif dist_after == 4:
                    score += 70
            # Penalidade para movimentos que se afastam do covil
            elif dist_after > dist_before:
                score -= 50 * (dist_after - dist_before)
        else:  # Peças azuis - valores iguais ao vermelho
            dist_before = abs(start[0] - self.dens[0][0]) + abs(start[1] - self.dens[0][1])
            dist_after = abs(end[0] - self.dens[0][0]) + abs(end[1] - self.dens[0][1])
            if dist_after < dist_before:
                score += 60 * (dist_before - dist_after)  # Mesmo valor que o vermelho
                # Bônus progressivo baseado na proximidade ao covil
                score += (7 - dist_after) * 25  # Mesmo valor que o vermelho
                # Bônus extra para movimentos que aproximam a peça para 2 ou 3 células de distância do covil
                if dist_after == 1:
                    score += 250  # Mesmo valor que o vermelho
                elif dist_after == 2:
                    score += 150  # Mesmo valor que o vermelho
                elif dist_after == 3:
                    score += 100  # Mesmo valor que o vermelho
                elif dist_after == 4:
                    score += 70  # Mesmo valor que o vermelho
            # Penalidade para movimentos que se afastam do covil
            elif dist_after > dist_before:
                score -= 50 * (dist_after - dist_before)  # Mesmo valor que o vermelho
        
        # Movimento para o centro (novo)
        center_positions = [(3, 2), (3, 3)]
        if end in center_positions:
            score += 4  # Ligeiro Aumento
        
        # Movimento que protege peças valiosas (novo)
        if abs(piece) >= 6:  # Tigre, Leão e Elefante
            if self.model.is_piece_safe_in_trap(end, piece):
                if abs(piece) == 8:  # Se for o Elefante
                    score += 20  # Bônus muito maior para proteger o elefante
                else:
                    score += 7  # Mantém o bônus original para outras peças valiosas
            
            # Verifica se há aliados próximos para proteção
            allies_nearby = 0
            for dr, dc in Consts.DIRECTIONS:
                nr, nc = end[0] + dr, end[1] + dc
                if (0 <= nr < 7 and 0 <= nc < 6):
                    nearby_piece = self.model.game_board[nr, nc]
                    if (piece < 0 and nearby_piece < 0) or (piece > 0 and nearby_piece > 0):  # Se for aliado
                        allies_nearby += 1
            
            if abs(piece) == 8:  # Se for o Elefante
                score += allies_nearby * 15  # Bônus significativo por ter aliados próximos
            else:
                score += allies_nearby * 5  # Bônus menor para outras peças valiosas
            
            # Penalidade extra para mover o elefante para posições perigosas
            if abs(piece) == 8:
                enemies_nearby = 0
                for dr, dc in Consts.DIRECTIONS:
                    nr, nc = end[0] + dr, end[1] + dc
                    if (0 <= nr < 7 and 0 <= nc < 6):
                        nearby_piece = self.model.game_board[nr, nc]
                        if (piece < 0 and nearby_piece > 0) or (piece > 0 and nearby_piece < 0):  # Se for inimigo
                            if abs(nearby_piece) == 1:  # Se for um rato
                                enemies_nearby += 3  # Penalidade extra por ratos próximos
                            else:
                                enemies_nearby += 1
                
                if enemies_nearby > allies_nearby:
                    score -= (enemies_nearby - allies_nearby) * 25  # Penalidade significativa por ter mais inimigos que aliados
        
        # Movimento que ameaça peças valiosas (novo)
        for dir in Consts.DIRECTIONS:
            threat_pos = (end[0] + dir[0], end[1] + dir[1])
            if (0 <= threat_pos[0] < 7 and 0 <= threat_pos[1] < 6):
                threat_piece = self.model.game_board[threat_pos[0], threat_pos[1]]
                if threat_piece != 0 and abs(threat_piece) >= 6:
                    if (piece < 0 and threat_piece > 0) or (piece > 0 and threat_piece < 0):
                        if self.model.is_self_rank_higher(piece, threat_piece):
                            score += 8  # Ligeiro Aumento
        
        return score

    def get_alternative_move(self) -> tuple:
        """Retorna um movimento alternativo quando o melhor movimento está proibido, priorizando movimentos em direção ao covil"""
        # Obtém todas as jogadas possíveis
        possible_moves = []
        for i in range(7):
            for j in range(6):
                piece = self.model.game_board[i, j]
                if (piece < 0 and self.model.turn == 1) or (piece > 0 and self.model.turn == 0):
                    moves = self.model.get_possible_moves((i, j))
                    if moves:
                        for move in moves:
                            possible_moves.append(((i, j), move))
        
        # Remove o movimento proibido da lista
        if self.model.forbidden_move:
            if self.model.forbidden_move in possible_moves:
                possible_moves.remove(self.model.forbidden_move)
        
        # Se não houver movimentos alternativos, retorna None
        if not possible_moves:
            return None
        
        # Verifica se algum movimento leva diretamente ao covil
        for start, end in possible_moves:
            if (self.model.turn == 0 and end == (0, 3)) or (self.model.turn == 1 and end == (6, 2)):
                return (start, end)
        
        # Avalia e ordena os movimentos
        scored_moves = [(self.evaluate_move((start, end)), (start, end)) for start, end in possible_moves]
        scored_moves.sort(reverse=True)  # Ordena por pontuação, do maior para o menor
        
        # Retorna o melhor movimento alternativo
        return scored_moves[0][1]


class RandomAI:
    def __init__(self, model: Model, seed: int = None):
        self.model = model
        # Define uma semente para reprodutibilidade
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        
    def get_best_move(self) -> tuple:
        """Retorna uma jogada aleatória válida"""
        # Obtém todas as jogadas possíveis para a IA
        possible_moves = []
        for i in range(7):
            for j in range(6):
                piece = self.model.game_board[i, j]
                # Verifica se a peça pertence ao jogador atual
                if (piece < 0 and self.model.turn == 1) or (piece > 0 and self.model.turn == 0):
                    moves = self.model.get_possible_moves((i, j))
                    if moves:
                        for move in moves:
                            possible_moves.append(((i, j), move))
        
        # Se não houver movimentos possíveis, retorna None
        if not possible_moves:
            return None
            
        # Escolhe um movimento aleatório
        return random.choice(possible_moves)

    def get_alternative_move(self) -> tuple:
        """Retorna um movimento alternativo quando o melhor movimento está proibido"""
        # Obtém todas as jogadas possíveis
        possible_moves = []
        for i in range(7):
            for j in range(6):
                piece = self.model.game_board[i, j]
                if (piece < 0 and self.model.turn == 1) or (piece > 0 and self.model.turn == 0):
                    moves = self.model.get_possible_moves((i, j))
                    if moves:
                        for move in moves:
                            possible_moves.append(((i, j), move))
        
        # Remove o movimento proibido da lista
        if self.model.forbidden_move:
            if self.model.forbidden_move in possible_moves:
                possible_moves.remove(self.model.forbidden_move)
        
        # Se não houver movimentos alternativos, retorna None
        if not possible_moves:
            return None
            
        # Retorna um movimento aleatório da lista de alternativas
        return random.choice(possible_moves)


class NegamaxAI:
    def __init__(self, model: Model, depth: int = 4):
        self.model = model
        self.max_depth = depth
        self.position_cache = {}
        
        # Valores das peças (otimizados)
        self.piece_values = {
            1: 6,   # Rato
            2: 3,   # Gato
            3: 4,   # Cão
            4: 5,   # Lobo
            5: 6,   # Leopardo
            6: 7,   # Tigre
            7: 8,   # Leão
            8: 15   # Elefante - Valor aumentado significativamente
        }
        
        # Posições das armadilhas
        self.traps = [
            (0, 2), (0, 4), (1, 3),  # Armadilhas vermelhas
            (6, 1), (6, 3), (5, 2)   # Armadilhas azuis
        ]
        
        # Posições das tocas
        self.dens = [(0, 3), (6, 2)]  # (vermelho, azul)
        
        # Limite de movimentos para poda
        self.move_limit = 20

    def evaluate_board(self) -> float:
        """Avalia o estado atual do tabuleiro"""
        board_key = hash(self.model.game_board.tobytes())
        if board_key in self.position_cache:
            return self.position_cache[board_key]
            
        score = 0
        
        # Verifica se o jogo terminou
        if self.model.is_win()[0]:
            if self.model.is_win()[1] == 'Vermelho':
                return float('inf')
            else:
                return float('-inf')

        # Avaliação de material
        for i in range(7):
            for j in range(6):
                piece = self.model.game_board[i, j]
                if piece != 0:
                    value = self.piece_values[abs(piece)]
                    if piece < 0:  # Peça vermelha (AI)
                        score += value  # Mesmo peso para ambos jogadores
                    else:  # Peça azul
                        score -= value
        
        # Avaliação de posição (melhorada para priorizar o covil)
        closest_red_to_blue_den = float('inf')  # Distância da peça vermelha mais próxima ao covil azul
        closest_blue_to_red_den = float('inf')  # Distância da peça azul mais próxima ao covil vermelho
        
        # Pontuação por proximidade ao covil adversário
        for i in range(7):
            for j in range(6):
                piece = self.model.game_board[i, j]
                if piece != 0:
                    if piece < 0:  # Peça vermelha (AI)
                        dist_to_den = abs(i - self.dens[1][0]) + abs(j - self.dens[1][1])
                        # Guarda a distância da peça mais próxima ao covil
                        closest_red_to_blue_den = min(closest_red_to_blue_den, dist_to_den)
                        
                        # Pontuação progressiva baseada na proximidade
                        proximity_score = (8 - dist_to_den) * 6.0
                        score += proximity_score
                        
                        # Bônus adicional para peças muito próximas ao covil
                        if dist_to_den <= 1:
                            score += 500
                        elif dist_to_den <= 2:
                            score += 200
                        elif dist_to_den <= 3:
                            score += 120
                        elif dist_to_den <= 4:
                            score += 80
                    else:  # Peça azul
                        dist_to_den = abs(i - self.dens[0][0]) + abs(j - self.dens[0][1])
                        # Guarda a distância da peça mais próxima ao covil
                        closest_blue_to_red_den = min(closest_blue_to_red_den, dist_to_den)
                        
                        # Pontuação progressiva baseada na proximidade (mesmo valor que o vermelho)
                        proximity_score = (8 - dist_to_den) * 6.0
                        score -= proximity_score
                        
                        # Bônus adicional para peças muito próximas ao covil (mesmo valor que o vermelho)
                        if dist_to_den <= 1:
                            score -= 500
                        elif dist_to_den <= 2:
                            score -= 200
                        elif dist_to_den <= 3:
                            score -= 120
                        elif dist_to_den <= 4:
                            score -= 80
        
        # Bônus para vantagem na corrida para os covis - equilibrado para ambos jogadores
        if closest_red_to_blue_den < closest_blue_to_red_den:
            race_advantage = closest_blue_to_red_den - closest_red_to_blue_den
            score += race_advantage * 80
        elif closest_blue_to_red_den < closest_red_to_blue_den:
            race_advantage = closest_red_to_blue_den - closest_blue_to_red_den
            score -= race_advantage * 80  # Mesmo valor que o vermelho
            
        # Armazena em cache e retorna
        self.position_cache[board_key] = score
        return score

    def get_all_possible_moves(self, is_ai_turn: bool) -> list:
        """Retorna todas as possíveis jogadas para o jogador atual"""
        moves = []
        for i in range(7):
            for j in range(6):
                piece = self.model.game_board[i, j]
                # Verifica se a peça pertence ao jogador atual
                if (is_ai_turn and piece < 0) or (not is_ai_turn and piece > 0):
                    possible_moves = self.model.get_possible_moves((i, j))
                    if possible_moves:
                        moves.extend(((i, j), move) for move in possible_moves)
        
        moves.sort(key=lambda x: self.evaluate_move(x), reverse=is_ai_turn)
        return moves[:self.move_limit]

    def negamax(self, depth: int, alpha: float, beta: float, color: int, add_noise: bool = False) -> tuple:
        """Implementa o algoritmo Negamax com cortes alfa-beta"""
        if depth == 0 or self.model.is_win()[0]:
            result = color * self.evaluate_board()
            # Adiciona um pequeno ruído aleatório para quebrar empates e evitar loops
            if add_noise and depth == 0:
                result += random.uniform(-self.model.random_factor, self.model.random_factor) * 100 * abs(color)
            return result, None
        
        moves = self.get_all_possible_moves(color > 0)
        
        # Remove o movimento proibido da lista, se existir
        if self.model.forbidden_move and self.model.cycle_detected:
            moves = [move for move in moves if move != self.model.forbidden_move]
            
        if not moves:
            return color * self.evaluate_board(), None
            
        best_value = float('-inf')
        best_move = moves[0] if moves else None
        
        # Embaralha os movimentos para introduzir variação
        if self.model.cycle_detected:
            random.shuffle(moves)
        
        for start, end in moves:
            # Faz a jogada
            piece_value = self.model.game_board[end[0], end[1]]
            self.model.game_board[end[0], end[1]] = self.model.game_board[start[0], start[1]]
            self.model.game_board[start[0], start[1]] = 0
            
            # Avalia a jogada
            value, _ = self.negamax(depth - 1, -beta, -alpha, -color, add_noise)
            value = -value
            
            # Penaliza movimentos que levam a estados repetidos
            current_state = self.model.game_board.tobytes()
            if current_state in self.model.board_states:
                value -= self.model.random_factor * 50 * abs(color)  # Penalidade proporcional ao fator de aleatoriedade
            
            # Desfaz a jogada
            self.model.game_board[start[0], start[1]] = self.model.game_board[end[0], end[1]]
            self.model.game_board[end[0], end[1]] = piece_value
            
            if value > best_value:
                best_value = value
                best_move = (start, end)
            
            alpha = max(alpha, value)
            if alpha >= beta:
                break
                
        return best_value, best_move

    def evaluate_move(self, move: tuple) -> float:
        """Avalia um movimento específico para ordenação (otimizada)"""
        start, end = move
        score = 0
        piece = self.model.game_board[start[0], start[1]]
        
        # Movimento para o covil adversário - prioridade máxima absoluta para ambos os jogadores
        if (self.model.turn == 0 and end == (0, 3)) or (self.model.turn == 1 and end == (6, 2)):
            return float('inf')  # Prioridade igual para ambos
        
        # Movimento para uma célula adjacente ao covil adversário - equalizado para ambos jogadores
        if self.model.turn == 0:  # Jogador azul
            if end in [(0, 2), (0, 4), (1, 3)]:  # Células adjacentes ao covil vermelho
                # Simula o movimento
                temp_board = self.model.game_board.copy()
                temp_board[end[0], end[1]] = temp_board[start[0], start[1]]
                temp_board[start[0], start[1]] = 0
                
                # Verifica se a peça estaria segura nesta posição
                is_safe = True
                
                # Como estamos em uma armadilha adversária, verificamos se há peças inimigas adjacentes
                for dr, dc in Consts.DIRECTIONS:
                    nr, nc = end[0] + dr, end[1] + dc
                    if 0 <= nr < 7 and 0 <= nc < 6 and temp_board[nr, nc] < 0:  # Peça inimiga
                        # Verifica se a peça inimiga pode capturar nossa peça
                        if self.model.is_self_rank_higher(temp_board[nr, nc], temp_board[end[0], end[1]]):
                            is_safe = False
                            break
                
                if is_safe:
                    return float('inf') * 0.995  # Prioridade extremamente alta
                else:
                    # Mesmo valor para ambos jogadores
                    score += 50
        else:  # Jogador vermelho
            if end in [(6, 1), (6, 3), (5, 2)]:  # Células adjacentes ao covil azul
                # Simula o movimento
                temp_board = self.model.game_board.copy()
                temp_board[end[0], end[1]] = temp_board[start[0], start[1]]
                temp_board[start[0], start[1]] = 0
                
                # Verifica se a peça estaria segura nesta posição
                is_safe = True
                
                # Como estamos em uma armadilha adversária, verificamos se há peças inimigas adjacentes
                for dr, dc in Consts.DIRECTIONS:
                    nr, nc = end[0] + dr, end[1] + dc
                    if 0 <= nr < 7 and 0 <= nc < 6 and temp_board[nr, nc] > 0:  # Peça inimiga
                        # Verifica se a peça inimiga pode capturar nossa peça
                        if self.model.is_self_rank_higher(temp_board[nr, nc], temp_board[end[0], end[1]]):
                            is_safe = False
                            break
                
                if is_safe:
                    return float('inf') * 0.995  # Prioridade extremamente alta
                else:
                    # Mesmo valor para ambos jogadores
                    score += 50
        
        # Células a duas casas de distância do covil - equilibrado para ambos jogadores
        covil_vermelho_proximidade2 = [(0, 1), (0, 5), (1, 2), (1, 4), (2, 3)]
        covil_azul_proximidade2 = [(6, 0), (6, 4), (5, 1), (5, 3), (4, 2)]
        
        if self.model.turn == 0 and end in covil_vermelho_proximidade2:  # Jogador azul perto do covil vermelho
            # Verifica se há um caminho livre até uma célula adjacente ao covil
            has_path_to_den = False
            for dr, dc in Consts.DIRECTIONS:
                nr, nc = end[0] + dr, end[1] + dc
                if (nr, nc) in [(0, 2), (0, 4), (1, 3)] and self.model.is_valid_move(end, (nr, nc)):
                    has_path_to_den = True
                    break
            
            if has_path_to_den:
                score += 500  # Mesmo valor para ambos jogadores
        elif self.model.turn == 1 and end in covil_azul_proximidade2:  # Jogador vermelho perto do covil azul
            # Verifica se há um caminho livre até uma célula adjacente ao covil
            has_path_to_den = False
            for dr, dc in Consts.DIRECTIONS:
                nr, nc = end[0] + dr, end[1] + dc
                if (nr, nc) in [(6, 1), (6, 3), (5, 2)] and self.model.is_valid_move(end, (nr, nc)):
                    has_path_to_den = True
                    break
            
            if has_path_to_den:
                score += 500  # Mesmo valor para ambos jogadores
        
        # Captura de peça - equilibrada para ambos jogadores
        if self.model.game_board[end[0], end[1]] != 0:
            captured_piece = abs(self.model.game_board[end[0], end[1]])
            score += self.piece_values[captured_piece] * 2.0
        
        # Movimento em direção à toca adversária - equilibrado para ambos jogadores
        if piece < 0:  # Peças vermelhas
            dist_before = abs(start[0] - self.dens[1][0]) + abs(start[1] - self.dens[1][1])
            dist_after = abs(end[0] - self.dens[1][0]) + abs(end[1] - self.dens[1][1])
            if dist_after < dist_before:
                score += 60 * (dist_before - dist_after)
                # Bônus progressivo baseado na proximidade ao covil
                score += (7 - dist_after) * 25
                # Bônus extra para movimentos que aproximam a peça para 2 ou 3 células de distância do covil
                if dist_after == 1:
                    score += 250
                elif dist_after == 2:
                    score += 150
                elif dist_after == 3:
                    score += 100
                elif dist_after == 4:
                    score += 70
            # Penalidade para movimentos que se afastam do covil
            elif dist_after > dist_before:
                score -= 50 * (dist_after - dist_before)
        else:  # Peças azuis - valores iguais ao vermelho
            dist_before = abs(start[0] - self.dens[0][0]) + abs(start[1] - self.dens[0][1])
            dist_after = abs(end[0] - self.dens[0][0]) + abs(end[1] - self.dens[0][1])
            if dist_after < dist_before:
                score += 60 * (dist_before - dist_after)  # Mesmo valor que o vermelho
                # Bônus progressivo baseado na proximidade ao covil
                score += (7 - dist_after) * 25  # Mesmo valor que o vermelho
                # Bônus extra para movimentos que aproximam a peça para 2 ou 3 células de distância do covil
                if dist_after == 1:
                    score += 250  # Mesmo valor que o vermelho
                elif dist_after == 2:
                    score += 150  # Mesmo valor que o vermelho
                elif dist_after == 3:
                    score += 100  # Mesmo valor que o vermelho
                elif dist_after == 4:
                    score += 70  # Mesmo valor que o vermelho
            # Penalidade para movimentos que se afastam do covil
            elif dist_after > dist_before:
                score -= 50 * (dist_after - dist_before)  # Mesmo valor que o vermelho
        
        # Movimento para o centro (novo)
        center_positions = [(3, 2), (3, 3)]
        if end in center_positions:
            score += 4  # Ligeiro Aumento
        
        # Movimento que protege peças valiosas (novo)
        if abs(piece) >= 6:  # Tigre, Leão e Elefante
            if self.model.is_piece_safe_in_trap(end, piece):
                if abs(piece) == 8:  # Se for o Elefante
                    score += 20  # Bônus muito maior para proteger o elefante
                else:
                    score += 7  # Mantém o bônus original para outras peças valiosas
            
            # Verifica se há aliados próximos para proteção
            allies_nearby = 0
            for dr, dc in Consts.DIRECTIONS:
                nr, nc = end[0] + dr, end[1] + dc
                if (0 <= nr < 7 and 0 <= nc < 6):
                    nearby_piece = self.model.game_board[nr, nc]
                    if (piece < 0 and nearby_piece < 0) or (piece > 0 and nearby_piece > 0):  # Se for aliado
                        allies_nearby += 1
            
            if abs(piece) == 8:  # Se for o Elefante
                score += allies_nearby * 15  # Bônus significativo por ter aliados próximos
            else:
                score += allies_nearby * 5  # Bônus menor para outras peças valiosas
            
            # Penalidade extra para mover o elefante para posições perigosas
            if abs(piece) == 8:
                enemies_nearby = 0
                for dr, dc in Consts.DIRECTIONS:
                    nr, nc = end[0] + dr, end[1] + dc
                    if (0 <= nr < 7 and 0 <= nc < 6):
                        nearby_piece = self.model.game_board[nr, nc]
                        if (piece < 0 and nearby_piece > 0) or (piece > 0 and nearby_piece < 0):  # Se for inimigo
                            if abs(nearby_piece) == 1:  # Se for um rato
                                enemies_nearby += 3  # Penalidade extra por ratos próximos
                            else:
                                enemies_nearby += 1
                
                if enemies_nearby > allies_nearby:
                    score -= (enemies_nearby - allies_nearby) * 25  # Penalidade significativa por ter mais inimigos que aliados
        
        # Movimento que ameaça peças valiosas (novo)
        for dir in Consts.DIRECTIONS:
            threat_pos = (end[0] + dir[0], end[1] + dir[1])
            if (0 <= threat_pos[0] < 7 and 0 <= threat_pos[1] < 6):
                threat_piece = self.model.game_board[threat_pos[0], threat_pos[1]]
                if threat_piece != 0 and abs(threat_piece) >= 6:
                    if (piece < 0 and threat_piece > 0) or (piece > 0 and threat_piece < 0):
                        if self.model.is_self_rank_higher(piece, threat_piece):
                            score += 8  # Ligeiro Aumento
        
        return score

    def get_best_move(self) -> tuple:
        """Retorna a melhor jogada para a IA"""
        # Verifica primeiro se há um movimento vitorioso direto
        all_moves = self.get_all_possible_moves(self.model.turn == 1)
        
        # Remove o movimento proibido da lista, se existir
        if self.model.forbidden_move and self.model.cycle_detected:
            all_moves = [move for move in all_moves if move != self.model.forbidden_move]
        
        # Se depois de remover o movimento proibido não sobrar nenhum movimento, 
        # retornamos todos os movimentos novamente
        if not all_moves:
            all_moves = self.get_all_possible_moves(self.model.turn == 1)
        
        for start, end in all_moves:
            # Verifica se pode entrar no covil adversário
            if (self.model.turn == 0 and end == (0, 3)) or (self.model.turn == 1 and end == (6, 2)):
                return (start, end)
            
            # Ou verifica se o movimento é vitorioso usando o método is_winning_move
            if self.model.is_winning_move(start, end):
                return (start, end)
                
        # Se não houver movimento vitorioso, continua com a lógica normal
        self.position_cache.clear()
        # Determina se é o turno da IA baseado no turno atual
        is_ai_turn = self.model.turn == 1  # Se turn == 1, é o turno da IA vermelha
        
        # Adiciona um pouco de aleatoriedade para evitar ficar preso em padrões
        if self.model.cycle_detected:
            # Adiciona uma pequena perturbação aleatória à avaliação
            add_noise = True
        else:
            add_noise = False
            
        # Corrigido: usando o color adequado para o negamax com base no turno atual
        color = 1 if is_ai_turn else -1
        _, best_move = self.negamax(self.max_depth, float('-inf'), float('inf'), color, add_noise)
        
        # Se o melhor movimento for o movimento proibido, escolhe um alternativo
        if self.model.forbidden_move and best_move == self.model.forbidden_move and self.model.cycle_detected:
            return self.get_alternative_move()
            
        return best_move

    def get_alternative_move(self) -> tuple:
        """Retorna um movimento alternativo quando o melhor movimento está proibido, priorizando movimentos em direção ao covil"""
        # Obtém todas as jogadas possíveis
        possible_moves = []
        for i in range(7):
            for j in range(6):
                piece = self.model.game_board[i, j]
                if (piece < 0 and self.model.turn == 1) or (piece > 0 and self.model.turn == 0):
                    moves = self.model.get_possible_moves((i, j))
                    if moves:
                        for move in moves:
                            possible_moves.append(((i, j), move))
        
        # Remove o movimento proibido da lista
        if self.model.forbidden_move:
            if self.model.forbidden_move in possible_moves:
                possible_moves.remove(self.model.forbidden_move)
        
        # Se não houver movimentos alternativos, retorna None
        if not possible_moves:
            return None
        
        # Verifica se algum movimento leva diretamente ao covil
        for start, end in possible_moves:
            if (self.model.turn == 0 and end == (0, 3)) or (self.model.turn == 1 and end == (6, 2)):
                return (start, end)
        
        # Avalia e ordena os movimentos
        scored_moves = [(self.evaluate_move((start, end)), (start, end)) for start, end in possible_moves]
        scored_moves.sort(reverse=True)  # Ordena por pontuação, do maior para o menor
        
        # Retorna o melhor movimento alternativo
        return scored_moves[0][1]