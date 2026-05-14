# Configurações do Jogo
WIDTH = 800
HEIGHT = 600
FPS = 60
WINNING_SCORE = 5

# Cores (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
GRAY = (100, 100, 100)

# Configurações das Raquetes
PADDLE_WIDTH = 15
PADDLE_HEIGHT = 150
PADDLE_SPEED = 10
SMOOTHING = 0.15  

# Configurações de Rastreamento
HAND_MEMORY_SENSITIVITY = 0.2
HAND_LOST_TIMEOUT = 10        
CALIB_Y_MIN_DEFAULT = 0.15
CALIB_Y_MAX_DEFAULT = 0.85

# Configurações da Bola
BALL_SIZE = 20
BALL_INITIAL_SPEED_X = 5
BALL_INITIAL_SPEED_Y = 5
BALL_ACCEL_PER_HIT = 1.08  # Aumenta 8% a cada rebatida
BALL_MAX_SPEED = 18        # Velocidade máxima saudável para 60 FPS
BALL_TRAIL_LENGTH = 6      # Quantos frames de rastro mostrar
