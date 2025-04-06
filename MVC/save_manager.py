import pickle
import os
import numpy as np
from MVC.model import AI, NegamaxAI, RandomAI

class SaveManager:
    """Classe para gerenciar o salvamento e carregamento de jogos"""
    
    @staticmethod
    def save_game(game_state):
        """Salva o estado atual do jogo em um arquivo
        
        Args:
            game_state (dict): Dicionário contendo o estado do jogo
        
        Returns:
            bool: True se o salvamento foi bem-sucedido, False caso contrário
        """
        try:
            # Certifica-se de que o diretório de salvamento existe
            save_dir = "saves"
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            
            # Salva o estado do jogo
            save_path = os.path.join(save_dir, "savegame.dat")
            with open(save_path, 'wb') as f:
                pickle.dump(game_state, f)
            
            return True
        except Exception as e:
            print(f"Erro ao salvar o jogo: {e}")
            return False
    
    @staticmethod
    def load_game():
        """Carrega o estado do jogo de um arquivo
        
        Returns:
            dict: Estado do jogo carregado ou None se falhar
        """
        try:
            save_path = os.path.join("saves", "savegame.dat")
            if not os.path.exists(save_path):
                return None
            
            with open(save_path, 'rb') as f:
                game_state = pickle.load(f)
            
            return game_state
        except Exception as e:
            print(f"Erro ao carregar o jogo: {e}")
            return None
    
    @staticmethod
    def game_save_exists():
        """Verifica se existe um jogo salvo
        
        Returns:
            bool: True se existe um jogo salvo, False caso contrário
        """
        save_path = os.path.join("saves", "savegame.dat")
        return os.path.exists(save_path)
    
    @staticmethod
    def prepare_game_state(controller):
        """Prepara o estado do jogo para ser salvo
        
        Args:
            controller: Instância do Controller
        
        Returns:
            dict: Estado do jogo preparado para ser salvo
        """
        # Salva o tabuleiro em formato numpy
        game_state = {
            'game_board': controller.model.game_board.tolist(),  # Converter para lista para serialização
            'turn': controller.model.turn,
            'is_pve': controller.is_pve,
            'is_aixai': controller.is_aixai,
            'selected_game_piece': controller.model.selected_game_piece,
            'moves': controller.model.moves,
            'last_move_coords': controller.model.last_move_coords,
            'last_moves': controller.model.last_moves,
            'forbidden_move': controller.model.forbidden_move,
            'move_history': controller.model.move_history,
            'cycle_detected': controller.model.cycle_detected,
            'elapsed_time': controller.view.elapsed_time,
            'game_time': controller.view.game_time,
        }
        
        # Salva o tipo de IA para jogos PvE
        if controller.is_pve and not controller.is_aixai:
            if hasattr(controller, 'ai'):
                if hasattr(controller.ai, 'max_depth'):  # Para Minimax ou Negamax
                    if isinstance(controller.ai, AI):
                        game_state['ai_type'] = 'minimax'
                    else:
                        game_state['ai_type'] = 'negamax'
                    game_state['ai_depth'] = controller.ai.max_depth
                else:  # Para Random
                    game_state['ai_type'] = 'random'
                    game_state['ai_depth'] = 0
        
        # Salva configurações de IA para jogos IAxIA
        if controller.is_aixai:
            # Azul
            if hasattr(controller.blue_ai, 'max_depth'):
                if isinstance(controller.blue_ai, AI):
                    game_state['blue_ai_type'] = 'minimax'
                else:
                    game_state['blue_ai_type'] = 'negamax'
                game_state['blue_ai_depth'] = controller.blue_ai.max_depth
            else:
                game_state['blue_ai_type'] = 'random'
                game_state['blue_ai_depth'] = 0
                
            # Vermelho
            if hasattr(controller.red_ai, 'max_depth'):
                if isinstance(controller.red_ai, AI):
                    game_state['red_ai_type'] = 'minimax'
                else:
                    game_state['red_ai_type'] = 'negamax'
                game_state['red_ai_depth'] = controller.red_ai.max_depth
            else:
                game_state['red_ai_type'] = 'random'
                game_state['red_ai_depth'] = 0
        
        return game_state 