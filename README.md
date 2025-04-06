# Jungle Chess

> Um jogo tradicional chinês implementado em Python com inteligência artificial

## Sobre o Projeto

Jungle Chess (Dou Shou Qi 鬥獸棋, ou Xadrez da Selva) é um jogo tradicional chinês implementado em Python. O projeto inclui um algoritmo minimax e um algoritmo negamax para um oponente computadorizado, permitindo que os jogadores enfrentem a IA em diferentes níveis de dificuldade.


## Funcionalidades

- Interface gráfica completa usando Pygame
- Modos de jogo: Jogador vs Jogador, Jogador vs IA, IA vs IA
- Algoritmos de IA: Minimax e Negamax com diferentes níveis de dificuldade
- Sistema de salvamento e carregamento de jogos
- Menu de regras detalhado com explicações sobre o jogo

## Tecnologias Utilizadas

- **Python**: Linguagem de programação principal
- **Pygame**: Biblioteca para desenvolvimento de jogos
- **NumPy**: Biblioteca para cálculos matemáticos
- **Padrão MVC**: Arquitetura de software para organização do código

## Estrutura do Projeto

O jogo utiliza um padrão de design de software MVC:
- **Model**: Armazena, modifica e usa as estruturas de dados do jogo - um array 2D representando o rank das peças e sua posição no tabuleiro.
- **View**: Implementa a representação visual do jogo, usando Pygame como biblioteca gráfica.
- **Controller**: Gerencia o fluxo do jogo, as comunicações entre a view e o model.

### Arquivos do Projeto

O projeto é composto pelos seguintes arquivos Python:

- **main.py**: Ponto de entrada do jogo, inicializa o pygame e inicia o menu principal.
- **assets/button.py**: Classe para criação de botões interativos na interface.
- **assets/consts.py**: Contém constantes utilizadas em todo o projeto, como cores, tamanhos e configurações.
- **MVC/controller.py**: Controla o fluxo do jogo, processando eventos e coordenando a interação entre model e view.
- **MVC/model.py**: Implementa a lógica do jogo, incluindo o tabuleiro, movimentos válidos e regras.
- **MVC/save_manager.py**: Funcionalidades para salvar e carregar jogos.
- **MVC/view.py**: Responsável pela interface gráfica, renderizando o tabuleiro, peças e menus.
- **screens/main_menu.py**: Implementa o menu principal e submenus do jogo.


## Como Jogar

1. Execute o arquivo `main.py`
2. Escolha um modo de jogo no menu principal:
   - Jogar PxP: Jogador contra Jogador
   - Jogar PxIA: Jogador contra Inteligência Artificial
   - Jogar IAxIA: Inteligência Artificial contra Inteligência Artificial
3. Selecione a dificuldade da IA (se aplicável)
4. Siga as regras do jogo para jogar

## Regras do Jogo

O Jungle Chess é jogado em um tabuleiro 6x7 com campos de água, tocas dos jogadores e armadilhas. Cada jogador controla 6 peças que representam animais diferentes (elefante, leão, leopardo, lobo, gato e rato), cada um com habilidades únicas.

O objetivo é conquistar a toca do adversário ou capturar todas as peças inimigas.

Para mais detalhes sobre as regras, consulte o menu "Regras" no jogo.

## Créditos

Este projeto foi desenvolvido por:
- Afonso Santos
- Hugo Pina
- Xavier Teixeira

## Licença e Uso

Este projeto está disponível para uso público, desde que os créditos sejam atribuídos aos criadores originais. Qualquer utilização, modificação ou distribuição do código deve incluir uma referência aos autores:

```
Jungle Chess - Desenvolvido por Afonso Santos, Hugo Pina e Xavier Teixeira
```

## Instalação

1. Clone este repositório:
   ```
   git clone https://github.com/xaviert15/jungle-chess.git
   cd jungle-chess
   ```

2. Instale as dependências necessárias:

   **Usando pip:**
   ```
   pip install -r requirements.txt
   ```

   **Instalação manual das bibliotecas principais:**
   ```
   pip install pygame
   pip install numpy
   ```

   **Para usuários Windows:**
   Se encontrar problemas com a instalação do Pygame, você pode tentar:
   ```
   pip install pygame --pre
   ```
   ou baixar o instalador apropriado para sua versão do Python em [pygame.org](https://www.pygame.org/download.shtml).

   **Para usuários Linux:**
   Pode ser necessário instalar algumas dependências do sistema antes:
   ```
   sudo apt-get install python3-pygame
   sudo apt-get install python3-numpy
   ```

3. Execute o jogo:
   ```
   python main.py
   ```

## Requisitos

- Python 3.6 ou superior
- Pygame 2.0.0 ou superior
- NumPy 1.19.0 ou superior
- Sistema operacional: Windows, macOS ou Linux

---

Desenvolvido como parte da unidade curricular de Elementos de Inteligência Artificial e Ciência de Dados.

