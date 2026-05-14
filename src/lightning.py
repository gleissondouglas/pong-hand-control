import pygame
import random

class LightningEffect:
    def __init__(self):
        self.points = []
        self.timer = 0

    def update_and_draw(self, surface, x_start, x_end, height):
        self.timer -= 1
        
        # Gera um novo raio ocasionalmente
        if self.timer <= 0:
            self.points = []
            if random.random() < 0.3: # Chance de gerar raio
                curr_x = random.randint(x_start, x_end)
                curr_y = 0
                self.points.append((curr_x, curr_y))
                
                while curr_y < height:
                    curr_y += random.randint(20, 50)
                    curr_x += random.randint(-30, 30)
                    # Mantém dentro dos limites laterais
                    curr_x = max(x_start, min(x_end, curr_x))
                    self.points.append((curr_x, curr_y))
                
                self.timer = random.randint(3, 8) # Duração do brilho
        
        # Desenha o raio se ele existir
        if self.points and self.timer > 0:
            color = random.choice([(255, 255, 255), (100, 200, 255)]) # Branco ou Azul elétrico
            pygame.draw.lines(surface, color, False, self.points, 2)
            
            # Adiciona um brilho simples (linha mais grossa com alpha ou apenas outra cor)
            if len(self.points) > 1:
                pygame.draw.lines(surface, (50, 100, 255), False, self.points, 4)
