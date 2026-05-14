import pygame
import math
from .config import WHITE, GREEN, RED, CYAN, WIDTH, HEIGHT

class UI:
    def __init__(self):
        # Tenta usar fontes mais estilosas se disponíveis, fallback para Arial
        try:
            self.font_score = pygame.font.SysFont("Courier New", 72, bold=True)
            self.font_status = pygame.font.SysFont("Courier New", 18, bold=True)
            self.font_msg = pygame.font.SysFont("Courier New", 24, bold=True)
        except:
            self.font_score = pygame.font.SysFont("Arial", 64, bold=True)
            self.font_status = pygame.font.SysFont("Arial", 20, bold=True)
            self.font_msg = pygame.font.SysFont("Arial", 24)
            
        # Cache para a superfície de vignette (melhora performance)
        self.vignette_surf = self._create_vignette()

    def _create_vignette(self):
        """Cria uma superfície de escurecimento suave nas bordas."""
        vignette = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # Preenche com preto semi-transparente
        vignette.fill((0, 0, 0, 0))
        
        # Desenha um gradiente radial invertido
        for i in range(0, 100, 5):
            alpha = int((i / 100) ** 2 * 180) # Curva quadrática para suavidade
            # Desenha retângulos ocos das bordas para o centro
            rect = pygame.Rect(0, 0, WIDTH, HEIGHT).inflate(-i*8, -i*6)
            # Como inflate reduz, queremos preencher o que sobrou fora dele
            # Mas é mais simples desenhar um overlay fixo e usar blit com opacidade
        
        # Versão simplificada: um gradiente nas bordas
        dark_edge = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for i in range(150): # 150 pixels de borda
            alpha = int(150 * (1 - i/150))
            pygame.draw.rect(dark_edge, (0,0,0, alpha), (i, i, WIDTH-2*i, HEIGHT-2*i), 1)
        return dark_edge

    def draw_vignette(self, surface):
        """Aplica o efeito de profundidade nas bordas."""
        surface.blit(self.vignette_surf, (0, 0))

    def draw_score(self, surface, score_left, score_right):
        # Neon Glow para o placar
        def draw_neon_text(text, x, y, color):
            # Brilho sutil ao redor do texto
            glow = self.font_score.render(text, True, color)
            glow.set_alpha(80)
            for dx, dy in [(-2,0),(2,0),(0,-2),(0,2)]:
                surface.blit(glow, (x + dx - glow.get_width() // 2, y + dy))
            
            # Texto principal
            main_text = self.font_score.render(text, True, WHITE)
            surface.blit(main_text, (x - main_text.get_width() // 2, y))

        draw_neon_text(str(score_left), WIDTH // 4, 30, GREEN)
        draw_neon_text(str(score_right), 3 * WIDTH // 4, 30, CYAN)

    def draw_status(self, surface, status):
        # HUD Holográfico nos cantos
        self._draw_hologram(surface, 20, 20, status["left"], "P1")
        self._draw_hologram(surface, WIDTH - 80, 20, status["right"], "P2")

    def _draw_hologram(self, surface, x, y, state, label):
        # Cores baseadas no estado
        if state == "ACTIVE":
            color = GREEN
            msg = "READY"
        elif state == "BOT":
            color = (255, 200, 0)
            msg = "BOT"
        else: # LOST
            color = RED
            msg = "LOST"
            # Efeito de piscar para o erro
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                color = (150, 0, 0)
        
        # Círculo externo
        pygame.draw.circle(surface, color, (x + 20, y + 20), 18, 2)
        if state != "LOST":
            pygame.draw.circle(surface, color, (x + 20, y + 20), 5)
        else:
            # X no centro para sinal perdido
            pygame.draw.line(surface, color, (x+15, y+15), (x+25, y+25), 2)
            pygame.draw.line(surface, color, (x+25, y+15), (x+15, y+25), 2)
        
        # Texto do Player
        txt_label = self.font_status.render(label, True, color)
        surface.blit(txt_label, (x + 20 - txt_label.get_width() // 2, y + 40))
        
        # Mensagem de status (READY / BOT / LOST)
        txt_msg = self.font_status.render(msg, True, color)
        surface.blit(txt_msg, (x + 20 - txt_msg.get_width() // 2, y + 58))

    def draw_menu(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220)) 
        surface.blit(overlay, (0,0))

        # Título com efeito Scanline/Neon
        title_color = (0, 255, 150)
        title = self.font_score.render("HAND PONG", True, title_color)
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        
        # Linha decorativa
        pygame.draw.line(surface, title_color, (WIDTH//4, HEIGHT//3 + 80), (3*WIDTH//4, HEIGHT//3 + 80), 2)

        instruction = self.font_msg.render("READY TO PLAY?", True, WHITE)
        start_hint = self.font_status.render("PRESS SPACE TO START", True, CYAN)
        calib_hint = self.font_status.render("PRESS 'C' TO CALIBRATE HEIGHT", True, (255, 200, 0))

        surface.blit(instruction, (WIDTH // 2 - instruction.get_width() // 2, HEIGHT // 2))
        surface.blit(start_hint, (WIDTH // 2 - start_hint.get_width() // 2, HEIGHT // 2 + 60))
        surface.blit(calib_hint, (WIDTH // 2 - calib_hint.get_width() // 2, HEIGHT // 2 + 100))

    def draw_calibration(self, surface, timer, max_time):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 240))
        surface.blit(overlay, (0,0))

        title = self.font_msg.render("CALIBRATING HEIGHT...", True, (255, 200, 0))
        instr = self.font_status.render("MOVE YOUR HANDS ALL THE WAY UP AND DOWN", True, WHITE)
        
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 3))
        surface.blit(instr, (WIDTH // 2 - instr.get_width() // 2, HEIGHT // 2))

        # Barra de progresso
        bar_w = 400
        bar_h = 20
        progress = (max_time - timer) / max_time
        
        pygame.draw.rect(surface, (50, 50, 50), (WIDTH // 2 - bar_w // 2, HEIGHT // 2 + 60, bar_w, bar_h))
        pygame.draw.rect(surface, (255, 200, 0), (WIDTH // 2 - bar_w // 2, HEIGHT // 2 + 60, int(bar_w * progress), bar_h))
        pygame.draw.rect(surface, WHITE, (WIDTH // 2 - bar_w // 2, HEIGHT // 2 + 60, bar_w, bar_h), 2)

    def draw_winner(self, surface, winner):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        surface.blit(overlay, (0,0))
        
        msg = f"PLAYER {winner} WINS"
        color = GREEN if winner == 1 else CYAN
        text = self.font_score.render(msg, True, color)
        hint = self.font_msg.render("SPACE TO REPLAY | Q TO QUIT", True, WHITE)

        surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 3))
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2))

    def draw_angry_face(self, surface, x, y, radius):
        # Mantém a lógica original mas com cores neon
        pygame.draw.circle(surface, (255, 20, 20), (x, y), radius)
        pygame.draw.circle(surface, WHITE, (x, y), radius, 2)
        
        # Olhos
        eye_radius = radius // 6
        pygame.draw.circle(surface, WHITE, (x - radius // 3, y - radius // 4), eye_radius)
        pygame.draw.circle(surface, WHITE, (x + radius // 3, y - radius // 4), eye_radius)
        
        # Sobrancelhas (V)
        pygame.draw.line(surface, WHITE, (x - radius // 2, y - radius // 2), (x - 5, y - 5), 3)
        pygame.draw.line(surface, WHITE, (x + radius // 2, y - radius // 2), (x + 5, y - 5), 3)
        
        # Boca (Arco Triste)
        rect_mouth = pygame.Rect(x - radius // 2, y + radius // 4, radius, radius // 2)
        pygame.draw.arc(surface, WHITE, rect_mouth, 0, math.pi, 3)
