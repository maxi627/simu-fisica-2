import random

import pygame

from config import *


class Particula:
    def __init__(self, x, y, vel_max_ini):
        self.x = x
        self.y = y
        self.radio = RADIO_PARTICULA
        self.color = COLOR_FRIO
        # Velocidad inicial aleatoria
        self.vx = random.uniform(-vel_max_ini, vel_max_ini)
        self.vy = random.uniform(-vel_max_ini, vel_max_ini)
        
        self.temperatura = TEMP_AMBIENTE
        
    def mover(self, divisor_pasos):
        self.x += self.vx / divisor_pasos
        self.y += self.vy / divisor_pasos

    def update_color(self):
        """Actualiza color basado en temperatura individual."""
        ratio = (self.temperatura - TEMP_AMBIENTE) / (TEMP_EBULLICION - TEMP_AMBIENTE)
        ratio = max(0, min(1, ratio))
        
        r = int(COLOR_FRIO[0] + (COLOR_CALIENTE[0] - COLOR_FRIO[0]) * ratio)
        g = int(COLOR_FRIO[1] + (COLOR_CALIENTE[1] - COLOR_FRIO[1]) * ratio)
        b = int(COLOR_FRIO[2] + (COLOR_CALIENTE[2] - COLOR_FRIO[2]) * ratio)
        self.color = (r, g, b)

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), self.radio)

class ParticulaVapor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radio = random.randint(4, 7)
        self.color = COLOR_VAPOR
        self.vx = random.uniform(-0.4, 0.4)
        self.vy = random.uniform(-1.2, -0.7) # Hacia arriba
        
        self.vida_total = VIDA_PARTICULA_VAPOR + random.uniform(-0.5, 0.5)
        self.vida_restante = self.vida_total
        self.viva = True
        self.surface = pygame.Surface((self.radio * 2, self.radio * 2), pygame.SRCALPHA)

    def update(self, dt):
        self.vida_restante -= dt
        if self.vida_restante <= 0:
            self.viva = False
            return
        self.x += self.vx
        self.y += self.vy

    def dibujar(self, superficie):
        if not self.viva: return
        
        ratio = self.vida_restante / self.vida_total
        alpha = int(150 * ratio)
        alpha = max(0, min(alpha, 255))
        
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.circle(self.surface, (*self.color, alpha), (self.radio, self.radio), self.radio)
        superficie.blit(self.surface, (int(self.x - self.radio), int(self.y - self.radio)))