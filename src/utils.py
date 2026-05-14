import pygame
import random
from .config import CYAN, WHITE

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        self.life = 1.0  # Vida de 1.0 a 0.0
        self.decay = random.uniform(0.02, 0.05)
        self.color = color
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.vx *= 0.95  # Fricção
        self.vy *= 0.95

    def draw(self, surface):
        if self.life > 0:
            s = int(self.size * self.life)
            if s > 0:
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), s)

class EffectManager:
    def __init__(self):
        self.particles = []
        self.shake_amount = 0
        self.shake_decay = 0.9

    def add_explosion(self, x, y, color=CYAN, count=15):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def trigger_shake(self, intensity):
        self.shake_amount = intensity

    def update(self):
        # Atualiza partículas
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]

        # Atualiza shake
        if self.shake_amount > 0:
            self.shake_amount *= self.shake_decay
            if self.shake_amount < 0.5:
                self.shake_amount = 0

    def get_shake_offset(self):
        if self.shake_amount > 0:
            ox = random.uniform(-self.shake_amount, self.shake_amount)
            oy = random.uniform(-self.shake_amount, self.shake_amount)
            return int(ox), int(oy)
        return 0, 0

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)

def lerp(a, b, t):
    return a + (b - a) * t
