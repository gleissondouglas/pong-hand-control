import pygame
from .config import WHITE, CYAN, GRAY, PADDLE_WIDTH, PADDLE_HEIGHT, WIDTH, HEIGHT, SMOOTHING
from .utils import lerp

class Paddle:
    def __init__(self, x):
        self.rect = pygame.Rect(x, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.target_y = self.rect.y
        self.color = WHITE
        self.is_active = False
        self.is_bot = False
        self.flash_timer = 0

    def flash(self):
        self.color = CYAN
        self.flash_timer = 10

    def update(self, hand_y):
        self.is_bot = False
        if self.flash_timer > 0:
            self.flash_timer -= 1
        else:
            if self.is_active:
                self.color = WHITE
            else:
                self.color = GRAY

        if hand_y is not None:
            self.is_active = True
            pixel_y = int(hand_y * HEIGHT)
            self.target_y = pixel_y - PADDLE_HEIGHT // 2
            
            # Limites da tela
            self.target_y = max(0, min(HEIGHT - PADDLE_HEIGHT, self.target_y))
            
            # Suavização (lerp)
            self.rect.y = int(lerp(self.rect.y, self.target_y, SMOOTHING))
        else:
            self.is_active = False

    def ai_update(self, ball):
        self.is_active = True
        self.is_bot = True
        
        if self.flash_timer > 0:
            self.flash_timer -= 1
        else:
            self.color = (255, 200, 0) # Laranja/Amarelo para o Bot
            
        # O Bot só reage se a bola estiver vindo na direção dele
        # (speed_x > 0 para a raquete da direita, x > WIDTH/2)
        if (self.rect.x > WIDTH // 2 and ball.speed_x > 0) or (self.rect.x < WIDTH // 2 and ball.speed_x < 0):
            # Persegue o centro da bola
            if self.rect.centery < ball.rect.centery:
                self.rect.y += 6 # Velocidade do Bot (ajustável)
            elif self.rect.centery > ball.rect.centery:
                self.rect.y -= 6
                
        # Limites da tela
        self.rect.y = max(0, min(HEIGHT - PADDLE_HEIGHT, self.rect.y))

    def draw(self, surface):
        # Desenha um brilho neon se estiver ativa
        if self.is_active:
            for i in range(3, 0, -1):
                glow_rect = self.rect.inflate(i*6, i*6)
                alpha = int(60 / i)
                glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (*self.color, alpha), (0, 0, glow_rect.width, glow_rect.height), border_radius=4)
                surface.blit(glow_surf, glow_rect)
        
        # Corpo principal da raquete
        pygame.draw.rect(surface, self.color, self.rect, border_radius=2)
        # Bordas brancas para destaque
        pygame.draw.rect(surface, WHITE, self.rect, 1, border_radius=2)
