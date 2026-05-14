# Hand Pong

Jogo de Pong controlado por movimentos das mãos via webcam, utilizando Visão Computacional (MediaPipe).

## Objetivo
Criar uma experiência interativa e robusta onde o jogador controla as raquetes do Pong usando a posição vertical de suas mãos.

## Stack Técnica
- **Linguagem:** Python 3.9+
- **Visão Computacional:** OpenCV, MediaPipe (Tasks)
- **Processamento:** NumPy
- **Interface/Game Engine:** Pygame

## Arquitetura de Pastas
- `main.py`: Ponto de entrada da aplicação.
- `requirements.txt`: Dependências do projeto.
- `assets/`: Sons, modelos de IA e imagens.
- `src/`: Código fonte modular.
  - `camera.py`: Gerenciamento do fluxo de vídeo e warm-up no macOS.
  - `hand_tracker.py`: Rastreamento de mãos usando MediaPipe Landmarker.
  - `paddle.py`: Lógica das raquetes e suavização de movimento.
  - `ball.py`: Física da bola, colisões e aceleração.
  - `ui.py`: Renderização de menus, placar e feedbacks visuais.
  - `config.py`: Constantes globais (cores, dimensões, FPS).
  - `fire.py` & `lightning.py`: Efeitos visuais especiais.
  - `utils.py`: Funções utilitárias.

## Comandos Principais
- Criar venv: `python -m venv venv`
- Ativar venv (Mac/Linux): `source venv/bin/activate`
- Instalar dependências: `pip install -r requirements.txt`
- Rodar o jogo (Mac): `./run_mac.sh`
- Rodar o jogo (Padrão): `python main.py`
