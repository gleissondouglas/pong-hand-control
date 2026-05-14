import pygame
import random
from .config import WHITE, CYAN, WIDTH, HEIGHT, BALL_SIZE, BALL_INITIAL_SPEED_X, BALL_INITIAL_SPEED_Y, BALL_ACCEL_PER_HIT, BALL_MAX_SPEED, BALL_TRAIL_LENGTH

class Ball:
    def __init__(self, hit_sound=None, effect_manager=None):
        self.rect = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)
        self.hit_sound = hit_sound
        self.effect_manager = effect_manager
        self.trail = [] # Lista de (x, y) das posições anteriores
        self.reset_speed()

    def reset_speed(self):
        self.speed_x = BALL_INITIAL_SPEED_X * random.choice((1, -1))
        self.speed_y = BALL_INITIAL_SPEED_Y * random.choice((1, -1))

    def update(self, left_paddle, right_paddle):
        # Armazena posição atual para o rastro antes de mover
        self.trail.insert(0, self.rect.center)
        if len(self.trail) > BALL_TRAIL_LENGTH:
            self.trail.pop()

        # Movimento
        self.rect.x += int(self.speed_x)
        self.rect.y += int(self.speed_y)

        # Colisão Topo e Baixo
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y *= -1
            if self.hit_sound: self.hit_sound.play()
            if self.effect_manager:
                self.effect_manager.trigger_shake(3)

        # Colisão com Raquetes (com margem de segurança para evitar colagem)
        if self.rect.colliderect(left_paddle.rect) and self.speed_x < 0:
            self._on_paddle_hit(left_paddle)
        
        elif self.rect.colliderect(right_paddle.rect) and self.speed_x > 0:
            self._on_paddle_hit(right_paddle)

    def _on_paddle_hit(self, paddle):
        # Calcula fator de velocidade (quão rápido está em relação ao início)
        speed_factor = abs(self.speed_x) / BALL_INITIAL_SPEED_X
        
        # Aumenta velocidade
        if abs(self.speed_x) < BALL_MAX_SPEED:
            self.speed_x *= BALL_ACCEL_PER_HIT
            self.speed_y *= BALL_ACCEL_PER_HIT
            
        # Inverte direção
        self.speed_x *= -1
        
        # Ajusta posição para fora da raquete para evitar múltiplas colisões
        if self.speed_x > 0: self.rect.left = paddle.rect.right
        else: self.rect.right = paddle.rect.left
        
        paddle.flash()
        
        # Feedback de Áudio Dinâmico: aumenta volume com a velocidade
        if self.hit_sound:
            volume = min(1.0, 0.4 + (speed_factor * 0.2)) 
            self.hit_sound.set_volume(volume)
            self.hit_sound.play()
            
        # Feedback Visual Dinâmico: Shake e Partículas aumentam com a velocidade
        if self.effect_manager:
            shake_intensity = int(5 * speed_factor)
            particle_count = int(8 * speed_factor)
            self.effect_manager.trigger_shake(shake_intensity)
            self.effect_manager.add_explosion(self.rect.centerx, self.rect.centery, count=particle_count)

    def reset(self):
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.trail = [] # Limpa rastro no ponto
        self.reset_speed()
        self.speed_x *= -1 

    def draw(self, surface):
        # 1. Desenha o Rastro (Trail)
        for i, pos in enumerate(self.trail):
            # Opacidade diminui conforme o rastro fica mais antigo
            alpha = int(100 * (1 - (i / BALL_TRAIL_LENGTH)))
            trail_size = BALL_SIZE - (i * 2) # O rastro afina
            if trail_size < 4: trail_size = 4
            
            trail_surf = pygame.Surface((trail_size, trail_size), pygame.SRCALPHA)
            pygame.draw.ellipse(trail_surf, (*CYAN, alpha), (0, 0, trail_size, trail_size))
            
            trail_rect = trail_surf.get_rect(center=pos)
            surface.blit(trail_surf, trail_rect)

        # 2. Desenha o Brilho Principal (Neon Glow)
        for i in range(3, 0, -1):
            glow_size = BALL_SIZE + (i * 12)
            glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
            alpha = int(120 / (i * 1.5))
            pygame.draw.ellipse(glow_surf, (*CYAN, alpha), (0, 0, glow_size, glow_size))
            
            glow_rect = glow_surf.get_rect(center=self.rect.center)
            surface.blit(glow_surf, glow_rect)

        # 3. Desenha o núcleo (bola branca)
        pygame.draw.ellipse(surface, WHITE, self.rect)
