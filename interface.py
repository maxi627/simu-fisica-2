import pygame

from config import *


class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 30)
        self.x_anchor = 750
        
        # Definición de botones
        self.btn_pot_down = pygame.Rect(self.x_anchor, 80, 25, 25)
        self.btn_pot_up = pygame.Rect(self.x_anchor + 30, 80, 25, 25)
        self.btn_masa_down = pygame.Rect(self.x_anchor, 110, 25, 25)
        self.btn_masa_up = pygame.Rect(self.x_anchor + 30, 110, 25, 25)
        
        self.txt_plus = self.font.render("+", True, COLOR_TEXTO_BOTON)
        self.txt_minus = self.font.render("-", True, COLOR_TEXTO_BOTON)

    def manejar_clic(self, pos, potencia_actual, masa_actual):
        """Devuelve una tupla (nueva_potencia, nueva_masa) si hubo cambios."""
        nueva_pot = potencia_actual
        nueva_masa = masa_actual
        
        if self.btn_pot_up.collidepoint(pos):
            nueva_pot += 100
        elif self.btn_pot_down.collidepoint(pos):
            nueva_pot = max(0, nueva_pot - 100)
        elif self.btn_masa_up.collidepoint(pos):
            if nueva_masa < MASA_MAX: nueva_masa += 0.1
        elif self.btn_masa_down.collidepoint(pos):
            if nueva_masa > MASA_MIN + 0.05: nueva_masa -= 0.1
            
        return nueva_pot, nueva_masa

    def dibujar(self, screen, data):
        """Data es un diccionario con el estado actual."""
        # Botones
        for rect in [self.btn_pot_up, self.btn_pot_down, self.btn_masa_up, self.btn_masa_down]:
            pygame.draw.rect(screen, COLOR_BOTON, rect)
            
        screen.blit(self.txt_plus, (self.btn_pot_up.x + 7, self.btn_pot_up.y + 2))
        screen.blit(self.txt_minus, (self.btn_pot_down.x + 8, self.btn_pot_down.y + 2))
        screen.blit(self.txt_plus, (self.btn_masa_up.x + 7, self.btn_masa_up.y + 2))
        screen.blit(self.txt_minus, (self.btn_masa_down.x + 8, self.btn_masa_down.y + 2))

        # Textos
        info = [
            (f"Temp Prom: {data['temp']:.1f}°C", 20),
            (f"Tiempo: {data['tiempo']:.1f} s", 50),
            (f"Potencia: {data['potencia']:.0f} W", 85, 65),
            (f"Masa: {data['masa']:.1f} kg", 115, 65),
            (f"Estado: {'ENCENDIDA' if data['encendida'] else 'APAGADA'}", 145, 0, (0, 150, 0) if data['encendida'] else (200, 0, 0)),
            (f"Partículas: {data['n_particulas']}", 175, 0, (100,100,100)),
            ("Presiona 'R' para reiniciar", 205, 0, (50,50,50)),
            ("[ESPACIO] para On/Off", 225, 0, (50,50,50)),
            (f"T. Ambiente: {TEMP_AMBIENTE:.1f}°C", 255, 0, (100,100,100))
        ]

        for item in info:
            texto = item[0]
            y = item[1]
            offset_x = item[2] if len(item) > 2 else 0
            color = item[3] if len(item) > 3 else (0,0,0)
            surf = self.font.render(texto, True, color)
            screen.blit(surf, (self.x_anchor + offset_x, y))