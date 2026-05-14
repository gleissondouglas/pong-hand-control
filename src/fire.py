import pygame
import random
import math

class FireEffect:
    def __init__(self):
        # Cada partícula: [x, y, radius, color, speed_y, offset]
        self.particles = []
        self.cache = {}

    def _get_particle_surf(self, radius, color):
        """Cria e armazena uma superfície de brilho suave em cache."""
        radius = int(radius)
        if radius < 1: return None
        
        # Chave do cache baseada no raio e cor
        cache_key = (radius, color)
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Cria uma superfície com canal Alpha para a partícula
        size = radius * 2
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Desenha círculos concêntricos para criar um degradê radial suave
        # Isso faz com que as partículas pareçam luz em vez de círculos sólidos
        for r in range(radius, 0, -1):
            alpha = int(100 * (1 - r/radius)**2) # Queda quadrática para bordas bem suaves
            pygame.draw.circle(surf, (*color, alpha), (radius, radius), r)
        
        self.cache[cache_key] = surf
        return surf

    def clear(self):
        """Limpa o efeito e o cache para uma nova partida."""
        self.particles = []
        self.cache = {}

    def update_and_draw(self, surface, x_start, x_end, height):
        # 1. Gerar novas partículas
        # Tons mais saturados para funcionar melhor com o modo BLEND_ADD
        fire_colors = [
            (200, 20, 0),   # Vermelho profundo
            (220, 80, 0),   # Laranja vibrante
            (255, 150, 0),  # Amarelo alaranjado
            (180, 40, 0)    # Vermelho escuro (para fumaça/brasa)
        ]

        for _ in range(8): 
            x = random.randint(x_start, x_end)
            y = height + random.randint(0, 30)
            radius = random.randint(10, 30) # Partículas um pouco maiores para o brilho
            color = random.choice(fire_colors)
            speed_y = random.uniform(2, 6)
            offset = random.uniform(0, math.pi * 2) # Para oscilação horizontal
            self.particles.append([x, y, radius, color, speed_y, offset])

        # 2. Atualizar e Desenhar
        remaining_particles = []
        
        for p in self.particles:
            p[1] -= p[4] # Sobe
            p[2] -= 0.3  # Encolhe
            p[5] += 0.1  # Incrementa oscilação

            if p[2] > 1:
                # Calcula posição com oscilação horizontal (onda senoidal)
                draw_x = p[0] + math.sin(p[5]) * 15
                draw_y = p[1]
                
                # Pega a superfície do cache
                p_surf = self._get_particle_surf(p[2], p[3])
                
                if p_surf:
                    # BLEND_RGB_ADD faz as cores se somarem, criando o brilho intenso (glow)
                    # Onde as chamas se cruzam, o centro fica branco/amarelo brilhante
                    rect = p_surf.get_rect(center=(int(draw_x), int(draw_y)))
                    surface.blit(p_surf, rect, special_flags=pygame.BLEND_RGB_ADD)
                    remaining_particles.append(p)
        
        self.particles = remaining_particles
        
        # Limpa cache muito grande para economizar memória (opcional)
        if len(self.cache) > 200:
            self.cache = {}
