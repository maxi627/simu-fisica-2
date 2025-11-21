
import pygame
from config import *
class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 24)
        self.x_anchor = 750
        
        # --- BOTONES DE MODO (MATE / HERVIR) ---
        self.btn_mate = pygame.Rect(self.x_anchor, 80, 100, 30)
        self.btn_hervir = pygame.Rect(self.x_anchor + 110, 80, 100, 30)
        
        # YA NO DEFINIMOS BOTONES DE MASA

    def manejar_clic(self, pos, modo_actual):
        """
        Solo gestiona el cambio de MODO (Mate/Hervir).
        Devuelve el nuevo modo seleccionado.
        """
        nuevo_modo = modo_actual
        
        if self.btn_mate.collidepoint(pos):
            nuevo_modo = TEMP_MATE
        elif self.btn_hervir.collidepoint(pos):
            nuevo_modo = TEMP_HERVIR
            
        return nuevo_modo

    def dibujar(self, screen, data):
        # --- DIBUJAR BOTONES MODO ---
        color_mate = COLOR_BOTON_ACTIVO if data['target_temp'] == TEMP_MATE else COLOR_BOTON
        color_hervir = COLOR_BOTON_ACTIVO if data['target_temp'] == TEMP_HERVIR else COLOR_BOTON
        
        pygame.draw.rect(screen, color_mate, self.btn_mate)
        pygame.draw.rect(screen, color_hervir, self.btn_hervir)
        
        txt_mate = self.font_small.render("MATE (80°)", True, (0,0,0))
        txt_hervir = self.font_small.render("HERVIR", True, (0,0,0))
        screen.blit(txt_mate, (self.btn_mate.x + 5, self.btn_mate.y + 7))
        screen.blit(txt_hervir, (self.btn_hervir.x + 15, self.btn_hervir.y + 7))

        # --- TEXTOS INFORMATIVOS ---
        # Calculamos color de estado
        color_estado = (0, 150, 0) if data['encendida'] else (200, 0, 0)
        estado_txt = "ENCENDIDA" if data['encendida'] else "APAGADA"
        
        # Estado especial "Listo"
        if not data['encendida'] and data['temp'] >= data['target_temp'] - 2.0 and data['target_temp'] == TEMP_MATE:
             estado_txt = "LISTO (MATE)"
             color_estado = (0, 100, 200)

        info = [
            (f"Temp Agua: {data['temp']:.1f}°C", 20),
            (f"Objetivo: {data['target_temp']:.0f}°C", 50),
            # Mantenemos el texto de masa para ver la evaporación, pero sin botones
            (f"Masa: {data['masa']:.2f} kg", 130), 
            (f"Estado: {estado_txt}", 160, 0, color_estado),
            (f"Tiempo: {data['tiempo']:.1f} s", 190),
            ("Presiona 'R' para reiniciar", 240, 0, (50,50,50)),
            ("[ESPACIO] ON/OFF manual", 260, 0, (50,50,50)),
        ]

        for item in info:
            texto = item[0]
            y = item[1]
            offset_x = item[2] if len(item) > 2 else 0
            color = item[3] if len(item) > 3 else (0,0,0)
            surf = self.font.render(texto, True, color)
            screen.blit(surf, (self.x_anchor + offset_x, y))