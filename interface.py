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

    def manejar_clic(self, pos, modo_actual):
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
        color_estado = (0, 150, 0) if data['encendida'] else (200, 0, 0)
        estado_txt = "ENCENDIDA" if data['encendida'] else "APAGADA"
        
        if not data['encendida'] and data['temp'] >= data['target_temp'] - 2.0 and data['target_temp'] == TEMP_MATE:
             estado_txt = "LISTO (MATE)"
             color_estado = (0, 100, 200)

        info = [
            (f"Temp Agua: {data['temp']:.1f}°C", 20),
            (f"Objetivo: {data['target_temp']:.0f}°C", 50),
            (f"Masa: {data['masa']:.2f} kg", 130), 
            (f"Estado: {estado_txt}", 160, 0, color_estado),
            (f"Tiempo: {data['tiempo']:.1f} s", 190),
            ("Presiona 'R' para reiniciar", 240, 0, (50,50,50)),
            ("Presiona 'ESC' para volver al Menu", 260, 0, (50,50,50)), # Agregado
            ("[ESPACIO] ON/OFF manual", 280, 0, (50,50,50)),
        ]

        for item in info:
            texto = item[0]
            y = item[1]
            offset_x = item[2] if len(item) > 2 else 0
            color = item[3] if len(item) > 3 else (0,0,0)
            surf = self.font.render(texto, True, color)
            screen.blit(surf, (self.x_anchor + offset_x, y))

# --- NUEVAS CLASES PARA EL MENÚ ---
class MenuPrincipal:
    def __init__(self):
        self.font_titulo = pygame.font.Font(None, 80)
        self.font_botones = pygame.font.Font(None, 50)
        # Fuente más chica para los nombres
        self.font_footer = pygame.font.Font(None, 24) 
        
        center_x = ANCHO // 2
        start_y = 300
        
        self.btn_iniciar = pygame.Rect(center_x - 100, start_y, 200, 50)
        self.btn_teoria = pygame.Rect(center_x - 100, start_y + 80, 200, 50)
        self.btn_salir = pygame.Rect(center_x - 100, start_y + 160, 200, 50)

        # --- LISTA DE INTEGRANTES ---
        # Edita los nombres aquí:
        self.integrantes = [
            "Integrantes:",
            "Burgos Pablo",
            "Genaro de Boni",
            "Eula Maximiliano",
            "Sajnovsky Jose"
        ]

    def dibujar(self, screen):
        screen.fill(COLOR_FONDO)
        
        # Título
        titulo = self.font_titulo.render("Simulación Termodinámica", True, (0, 0, 0))
        rect_titulo = titulo.get_rect(center=(ANCHO//2, 150))
        screen.blit(titulo, rect_titulo)
        
        # Botones
        botones = [
            (self.btn_iniciar, "Iniciar", (100, 200, 100)),
            (self.btn_teoria, "Teoría", (100, 150, 255)),
            (self.btn_salir, "Salir", (255, 100, 100))
        ]
        
        for rect, texto, color in botones:
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, (0,0,0), rect, 2, border_radius=10) # Borde
            surf = self.font_botones.render(texto, True, (255, 255, 255))
            text_rect = surf.get_rect(center=rect.center)
            screen.blit(surf, text_rect)

        # --- DIBUJAR INTEGRANTES (Pie de página izquierdo) ---
        start_y_nombres = ALTO - 20 - (len(self.integrantes) * 20) # Calcula altura para que quede al fondo
        for i, linea in enumerate(self.integrantes):
            surf_nombre = self.font_footer.render(linea, True, (80, 80, 80)) # Color gris oscuro
            screen.blit(surf_nombre, (20, start_y_nombres + (i * 20)))

    def manejar_clic(self, pos):
        if self.btn_iniciar.collidepoint(pos):
            return "SIMULACION"
        if self.btn_teoria.collidepoint(pos):
            return "TEORIA"
        if self.btn_salir.collidepoint(pos):
            return "SALIR"
        return None

class PantallaTeoria:
    def __init__(self):
        self.font_titulo = pygame.font.Font(None, 60)
        self.font_texto = pygame.font.Font(None, 32)
        self.font_boton = pygame.font.Font(None, 40)
        
        self.btn_volver = pygame.Rect(50, ALTO - 80, 150, 50)
        
        self.textos = [
            "Primera Ley de la Termodinámica (Conservación de la Energía):",
            "La energía no se crea ni se destruye, solo se transforma.",
            "En esta simulación, la energía eléctrica de la pava se transforma en calor",
            "(Efecto Joule), aumentando la energía interna del agua (su temperatura).",
            "Al llegar a 100°C, la energía se usa para romper enlaces (Calor Latente),",
            "convirtiendo el líquido en vapor sin aumentar más la temperatura.",
            "",
            "Segunda Ley de la Termodinámica (Entropía):",
            "El calor fluye espontáneamente del cuerpo caliente (resistencia) al frío (agua).",
            "El proceso de ebullición aumenta el desorden molecular (Entropía).",
            "Es un proceso irreversible: no podemos juntar el vapor para recuperar",
            "la electricidad original fácilmente."
        ]

    def dibujar(self, screen):
        screen.fill((240, 240, 250)) # Fondo ligeramente distinto
        
        titulo = self.font_titulo.render("Teoría Aplicada", True, (0, 0, 0))
        screen.blit(titulo, (50, 50))
        
        y = 120
        for linea in self.textos:
            color = (0, 0, 150) if "Ley" in linea else (50, 50, 50)
            surf = self.font_texto.render(linea, True, color)
            screen.blit(surf, (50, y))
            y += 35
            
        # Botón Volver
        pygame.draw.rect(screen, (100, 100, 100), self.btn_volver, border_radius=10)
        txt = self.font_boton.render("Volver", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.btn_volver.center))

    def manejar_clic(self, pos):
        if self.btn_volver.collidepoint(pos):
            return "MENU"
        return None