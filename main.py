import pygame
import os
import sys

# 1. Mitigação de conflito SDL no macOS: Inicializa pygame ANTES de importar cv2
pygame.init()

try:
    import cv2
except ImportError:
    print("Erro: OpenCV (cv2) não encontrado. Instale com 'pip install opencv-python'")
    sys.exit(1)

from src.camera import Camera, CameraStream
from src.hand_tracker import HandTracker
from src.paddle import Paddle
from src.ball import Ball
from src.ui import UI
from src.fire import FireEffect
from src.lightning import LightningEffect
from src.config import WIDTH, HEIGHT, BLACK, FPS, WINNING_SCORE, CALIB_Y_MIN_DEFAULT, CALIB_Y_MAX_DEFAULT
from src.utils import EffectManager

# Estados do Jogo
MENU = 0
PLAYING = 1
GAMEOVER = 2
SCORING_DELAY = 3
CALIBRATION = 4

class HandPongGame:
    def __init__(self):
        # Verifica se os assets existem
        if not os.path.exists("assets"):
            print("Erro: Pasta 'assets' não encontrada.")
            sys.exit(1)

        # Inicializa o Mixer
        try:
            pygame.mixer.init()
            self.hit_sound = pygame.mixer.Sound("assets/sounds/hit.wav")
            self.score_sound = pygame.mixer.Sound("assets/sounds/score.wav")
        except Exception as e:
            print(f"Aviso: Áudio não disponível ({e})")
            self.hit_sound = None
            self.score_sound = None

        # Janela e Superfícies
        self.current_width, self.current_height = WIDTH, HEIGHT
        self.screen = pygame.display.set_mode((self.current_width, self.current_height), pygame.RESIZABLE)
        self.game_surface = pygame.Surface((WIDTH, HEIGHT))
        pygame.display.set_caption("Hand Pong")
        
        self.clock = pygame.time.Clock()
        self.running = True

        # Recursos do Jogo
        print("Inicializando câmera e rastreador de mãos...")
        self.cam = Camera()
        self.tracker = HandTracker()
        
        # Inicia a Thread de Câmera e IA
        print("Iniciando fluxo assíncrono (Threading)...")
        self.stream = CameraStream(self.cam, self.tracker).start()
        
        # Elementos do Jogo
        self.left_paddle = Paddle(20)
        self.right_paddle = Paddle(WIDTH - 35)
        self.effects = EffectManager()
        self.ball = Ball(hit_sound=self.hit_sound, effect_manager=self.effects)
        
        self.ui = UI()
        self.fire_effect = FireEffect()
        self.lightning_effect = LightningEffect()

        # Estado do Jogo
        self.score_left = 0
        self.score_right = 0
        self.state = MENU
        self.winner = 0
        self.scoring_timer = 0
        self.scoring_side = 0
        
        # Calibração de Altura
        self.y_min = CALIB_Y_MIN_DEFAULT
        self.y_max = CALIB_Y_MAX_DEFAULT
        self.calib_timer = 0
        self.calib_max_time = FPS * 5
        self.temp_y_min = 1.0
        self.temp_y_max = 0.0

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.VIDEORESIZE:
                self.current_width, self.current_height = event.w, event.h
                self.screen = pygame.display.set_mode((self.current_width, self.current_height), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state == MENU or self.state == GAMEOVER:
                        self.score_left = 0
                        self.score_right = 0
                        self.ball.reset()
                        self.fire_effect.clear()
                        self.state = PLAYING
                if event.key == pygame.K_c:
                    if self.state == MENU:
                        self.state = CALIBRATION
                        self.calib_timer = self.calib_max_time
                        self.temp_y_min = 1.0
                        self.temp_y_max = 0.0
                if event.key == pygame.K_q:
                    self.running = False

    def _update(self, hands):
        self.effects.update()
        
        y_left_raw = hands["left"]["y"] if "left" in hands and hands["left"] else None
        y_right_raw = hands["right"]["y"] if "right" in hands and hands["right"] else None

        if self.state == CALIBRATION:
            self.calib_timer -= 1
            # Coleta extremos de qualquer mão visível
            for side in ["left", "right"]:
                if hands[side]:
                    y = hands[side]["y"]
                    self.temp_y_min = min(self.temp_y_min, y)
                    self.temp_y_max = max(self.temp_y_max, y)
            
            if self.calib_timer <= 0:
                # Aplica calibração se houver movimento suficiente (mínimo 10% da tela)
                if self.temp_y_max - self.temp_y_min > 0.1:
                    # Adiciona uma pequena folga (5%) para facilitar chegar nos cantos
                    self.y_min = self.temp_y_min + 0.05
                    self.y_max = self.temp_y_max - 0.05
                    print(f"Calibração salva: min={self.y_min:.2f}, max={self.y_max:.2f}")
                self.state = MENU
            return

        # Função de mapeamento que usa os valores calibrados
        def map_y(y):
            if y is None: return None
            mapped = (y - self.y_min) / (self.y_max - self.y_min)
            return max(0.0, min(1.0, mapped))

        y_left = map_y(y_left_raw)
        y_right = map_y(y_right_raw)

        if self.state == PLAYING:
            self.left_paddle.update(y_left)
            
            # IA / Bot: Se não houver mão direita, o computador assume
            if y_right is not None:
                self.right_paddle.update(y_right)
            else:
                self.right_paddle.ai_update(self.ball)
                
            self.ball.update(self.left_paddle, self.right_paddle)

            if self.ball.rect.left <= 0:
                self.state = SCORING_DELAY
                self.scoring_timer = 30
                self.scoring_side = 2
                self.effects.trigger_shake(15)
                self.effects.add_explosion(self.ball.rect.centerx, self.ball.rect.centery, color=(255, 50, 50), count=30)
            elif self.ball.rect.right >= WIDTH:
                self.state = SCORING_DELAY
                self.scoring_timer = 30
                self.scoring_side = 1
                self.effects.trigger_shake(15)
                self.effects.add_explosion(self.ball.rect.centerx, self.ball.rect.centery, color=(255, 50, 50), count=30)
        
        elif self.state == SCORING_DELAY:
            self.scoring_timer -= 1
            if self.scoring_timer <= 0:
                if self.scoring_side == 1:
                    self.score_left += 1
                    if self.score_sound: self.score_sound.play()
                    if self.score_left >= WINNING_SCORE:
                        self.state = GAMEOVER
                        self.winner = 1
                    else:
                        self.ball.reset()
                        self.state = PLAYING
                else:
                    self.score_right += 1
                    if self.score_sound: self.score_sound.play()
                    if self.score_right >= WINNING_SCORE:
                        self.state = GAMEOVER
                        self.winner = 2
                    else:
                        self.ball.reset()
                        self.state = PLAYING

    def _draw(self, frame_surface, hands):
        # Fundo (Câmera)
        if frame_surface:
            self.game_surface.blit(frame_surface, (0, 0))
        else:
            self.game_surface.fill(BLACK)
        
        # UI e Elementos de jogo
        self.ui.draw_vignette(self.game_surface)
        pygame.draw.aaline(self.game_surface, (200, 200, 200), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))
        
        if self.state == SCORING_DELAY:
            elastic_color = (255, 255, 255)
            ball_center = self.ball.rect.center
            if self.scoring_side == 2:
                pygame.draw.line(self.game_surface, elastic_color, (0, 0), ball_center, 2)
                pygame.draw.line(self.game_surface, elastic_color, (0, HEIGHT), ball_center, 2)
            else:
                pygame.draw.line(self.game_surface, elastic_color, (WIDTH, 0), ball_center, 2)
                pygame.draw.line(self.game_surface, elastic_color, (WIDTH, HEIGHT), ball_center, 2)
        
        self.left_paddle.draw(self.game_surface)
        self.right_paddle.draw(self.game_surface)
        self.ball.draw(self.game_surface)
        self.effects.draw_particles(self.game_surface)
        
        if self.state == PLAYING or self.state == SCORING_DELAY:
            if self.score_left == WINNING_SCORE - 1:
                self.lightning_effect.update_and_draw(self.game_surface, WIDTH // 2, WIDTH, HEIGHT)
                self.ui.draw_angry_face(self.game_surface, 3 * WIDTH // 4, HEIGHT // 2, 40)
            if self.score_right == WINNING_SCORE - 1:
                self.lightning_effect.update_and_draw(self.game_surface, 0, WIDTH // 2, HEIGHT)
                self.ui.draw_angry_face(self.game_surface, WIDTH // 4, HEIGHT // 2, 40)
        
        self.ui.draw_score(self.game_surface, self.score_left, self.score_right)
        
        # Prepara o status detalhado para a UI
        status = {
            "left": "ACTIVE" if hands and hands.get("left") else "LOST",
            "right": "ACTIVE" if hands and hands.get("right") else ("BOT" if self.state != MENU else "LOST")
        }
        self.ui.draw_status(self.game_surface, status)

        if self.state == MENU:
            ui_hands = hands if hands else {"left": None, "right": None}
            self.ui.draw_menu(self.game_surface)
        elif self.state == CALIBRATION:
            self.ui.draw_calibration(self.game_surface, self.calib_timer, self.calib_max_time)
        elif self.state == GAMEOVER:
            if self.winner == 1:
                self.fire_effect.update_and_draw(self.game_surface, WIDTH // 2, WIDTH, HEIGHT)
            else:
                self.fire_effect.update_and_draw(self.game_surface, 0, WIDTH // 2, HEIGHT)
            self.ui.draw_winner(self.game_surface, self.winner)
        
        # Aplica Shake e renderiza na tela principal
        shake_ox, shake_oy = self.effects.get_shake_offset()
        scaled_surface = pygame.transform.scale(self.game_surface, (self.current_width, self.current_height))
        self.screen.blit(scaled_surface, (shake_ox, shake_oy))
        
        pygame.display.flip()

    def run(self):
        print("Hand Pong pronto! Pressione ESPAÇO para começar.")
        try:
            while self.running:
                self._handle_events()

                # Leitura assíncrona da thread de câmera
                frame, hands = self.stream.read()
                
                frame_surface = None
                if frame is not None:
                    # O frame já vem redimensionado, convertido para RGB e transposto pela thread
                    frame_surface = pygame.surfarray.make_surface(frame)
                
                self._update(hands)
                self._draw(frame_surface, hands)
                
                self.clock.tick(FPS)
        except Exception as e:
            print(f"Erro inesperado: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        print("Finalizando recursos...")
        if hasattr(self, 'stream'): self.stream.stop()
        if hasattr(self, 'cam'): self.cam.release()
        if hasattr(self, 'tracker'): self.tracker.close()
        pygame.quit()

def main():
    game = HandPongGame()
    game.run()

if __name__ == "__main__":
    main()
