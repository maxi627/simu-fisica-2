import pygame

from config import *


class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, start_val, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.label = label
        self.dragging = False
        self.font = pygame.font.Font(None, 24)
        
        self.handle_rect = pygame.Rect(x, y - 5, 10, h + 10)
        self.update_handle_pos()

    def update_handle_pos(self):
        ratio = (self.val - self.min_val) / (self.max_val - self.min_val)
        self.handle_rect.centerx = self.rect.x + ratio * self.rect.width

    def manejar_evento(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.handle_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.dragging = True
                self.update_val_from_mouse(event.pos[0])
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.update_val_from_mouse(event.pos[0])

    def update_val_from_mouse(self, mouse_x):
        x = max(self.rect.left, min(mouse_x, self.rect.right))
        ratio = (x - self.rect.left) / self.rect.width
        self.val = self.min_val + ratio * (self.max_val - self.min_val)
        self.update_handle_pos()

    def dibujar(self, screen):
        # Fondo
        pygame.draw.rect(screen, (180, 180, 180), self.rect, border_radius=5)
        # Relleno activo
        active_rect = pygame.Rect(self.rect.x, self.rect.y, self.handle_rect.centerx - self.rect.x, self.rect.height)
        pygame.draw.rect(screen, (100, 150, 255), active_rect, border_radius=5)
        
        # Mango
        color_handle = (50, 100, 200) if self.dragging else (100, 100, 100)
        pygame.draw.rect(screen, color_handle, self.handle_rect, border_radius=2)
        
        # --- FORMATEO DEL TEXTO ---
        val_str = f"{self.val:.1f}"
        if "Potencia" in self.label: 
            val_str = f"{self.val:.0f} W"
        elif "Ambiente" in self.label: 
            val_str = f"{self.val:.1f} °C"
        elif "Corte" in self.label: 
            val_str = f"{self.val:.0f} °C"
        elif "Aislamiento" in self.label: 
            val_str = f"k = {self.val:.5f}"
            
        lbl_surf = self.font.render(f"{self.label}: {val_str}", True, (0, 0, 0))
        screen.blit(lbl_surf, (self.rect.x, self.rect.y - 18))

class HUD:
    def __init__(self):
        self.font = pygame.font.Font(None, 30)
        self.font_small = pygame.font.Font(None, 24)
        self.font_formula = pygame.font.SysFont("arial", 20) 
        self.x_anchor = 750
        
        # Botones
        self.btn_mate = pygame.Rect(self.x_anchor, 80, 100, 30)
        self.btn_hervir = pygame.Rect(self.x_anchor + 110, 80, 100, 30)
        self.btn_manual = pygame.Rect(self.x_anchor + 220, 80, 100, 30)

    
        # 1. Temp. de Corte
        self.slider_target = Slider(self.x_anchor, 510, 200, 10, 20, 100, 80, "Temp. Corte")
        # 2. Potencia
        self.slider_potencia = Slider(self.x_anchor, 570, 200, 10, 0, 3000, POTENCIA_FIJA, "Potencia")
        # 3. Temp. Ambiente
        self.slider_ambiente = Slider(self.x_anchor, 630, 200, 10, 0, 40, TEMP_AMBIENTE, "Temp. Ambiente")
        # 4. Aislamiento
        self.slider_aislamiento = Slider(self.x_anchor, 690, 200, 10, 0.0, 0.02, K_ENFRIAMIENTO_PARTICULA, "Aislamiento")

    def manejar_eventos_input(self, event, modo_actual, modo_manual_activo):
        nuevo_modo = modo_actual
        nuevo_estado_manual = modo_manual_activo

        # Solo activar sliders en modo manual
        if modo_manual_activo:
            self.slider_target.manejar_evento(event)
            self.slider_potencia.manejar_evento(event)
            self.slider_ambiente.manejar_evento(event)
            self.slider_aislamiento.manejar_evento(event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.btn_mate.collidepoint(pos):
                nuevo_modo = TEMP_MATE
                nuevo_estado_manual = False
            elif self.btn_hervir.collidepoint(pos):
                nuevo_modo = TEMP_HERVIR
                nuevo_estado_manual = False
            elif self.btn_manual.collidepoint(pos):
                nuevo_estado_manual = True 
                
        return nuevo_modo, nuevo_estado_manual

    def dibujar(self, screen, data):
        mouse_pos = pygame.mouse.get_pos()
        tooltip_a_mostrar = None 
        
        # Colores botones
        color_mate = COLOR_BOTON_ACTIVO if (data['target_temp'] == TEMP_MATE and not data['modo_manual']) else COLOR_BOTON
        color_hervir = COLOR_BOTON_ACTIVO if (data['target_temp'] == TEMP_HERVIR and not data['modo_manual']) else COLOR_BOTON
        color_manual = COLOR_BOTON_ACTIVO if data['modo_manual'] else COLOR_BOTON
        
        pygame.draw.rect(screen, color_mate, self.btn_mate)
        pygame.draw.rect(screen, color_hervir, self.btn_hervir)
        pygame.draw.rect(screen, color_manual, self.btn_manual)
        
        txt_mate = self.font_small.render("MATE (80°)", True, (0,0,0))
        txt_hervir = self.font_small.render("HERVIR", True, (0,0,0))
        txt_manual = self.font_small.render("MANUAL", True, (0,0,0))
        
        screen.blit(txt_mate, (self.btn_mate.x + 5, self.btn_mate.y + 7))
        screen.blit(txt_hervir, (self.btn_hervir.x + 15, self.btn_hervir.y + 7))
        screen.blit(txt_manual, (self.btn_manual.x + 15, self.btn_manual.y + 7))

        # --- DIBUJAR SLIDERS ---
        if data['modo_manual']:
            self.slider_target.dibujar(screen)
            self.slider_potencia.dibujar(screen)
            self.slider_ambiente.dibujar(screen)
            self.slider_aislamiento.dibujar(screen)

        # --- DATOS ---
        color_estado = (0, 150, 0) if data['encendida'] else (200, 0, 0)
        estado_txt = "ENCENDIDA" if data['encendida'] else "APAGADA"
        
        if not data['encendida'] and data['temp'] >= data['target_temp'] - 2.0:
             estado_txt = "LISTO"
             color_estado = (0, 100, 200)

        if abs(data['delta_u']) < 10000: du_str = f"{data['delta_u']:.0f}"
        else: du_str = f"{data['delta_u']/1000:.1f}k"
        def fmt_j(valor): return f"{valor:.0f}" if valor < 10000 else f"{valor/1000:.1f}k"

        potencia_mostrar = data['potencia_actual']
        
        if data['modo_manual']:
            str_objetivo = f"MANUAL ({data['target_temp']:.0f}°C)"
        else:
            str_objetivo = f"{data['target_temp']:.0f}°C"

        info = [
            (f"Temp Agua: {data['temp']:.1f}°C", 20),
            (f"Objetivo: {str_objetivo}", 50),
            (f"Masa: {data['masa']:.2f} kg", 130),
            (f"Potencia: {potencia_mostrar:.0f} W", 155),

            (f"ΔU (1° Ley): {du_str} J", 190, 0, (0, 0, 150), "FORMULA_1"),
            (f"ΔS (2° Ley): {data['delta_s']:.1f} J/K", 220, 0, (100, 0, 100), "FORMULA_2"),

            (f"Q_p (Total): {fmt_j(data['q_p'])} J", 260, 0, (80,80,80), "FORMULA_QP"),
            (f"Q_a (Agua): {fmt_j(data['q_a'])} J", 285, 0, (80,80,80), "FORMULA_QA"),
            (f"Q_l (Vapor): {fmt_j(data['q_l'])} J", 310, 0, (80,80,80), "FORMULA_QL"),

            (f"Estado: {estado_txt}", 350, 0, color_estado),
            (f"Tiempo: {data['tiempo']:.1f} s", 380),
            
            ("Presiona 'R' para reiniciar", 410, 0, (50,50,50)),
            ("Presiona 'ESC' para menú", 430, 0, (50,50,50)),
            ("[ESPACIO] ON/OFF", 450, 0, (50,50,50)),
        ]

        for item in info:
            texto = item[0]
            y = item[1]
            offset_x = item[2] if len(item) > 2 else 0
            color = item[3] if len(item) > 3 else (0,0,0)
            
            surf = self.font.render(texto, True, color)
            rect_texto = screen.blit(surf, (self.x_anchor + offset_x, y))

            if len(item) > 4:
                tag = item[4]
                if rect_texto.collidepoint(mouse_pos):
                    if tag == "FORMULA_1": tooltip_a_mostrar = "ΔU = Q - W (Energía Interna)"
                    elif tag == "FORMULA_2": tooltip_a_mostrar = "ΔS = m · c · ln(Tf / Ti)"
                    elif tag == "FORMULA_QP": tooltip_a_mostrar = f"Qp = P({potencia_mostrar:.0f}W) * Tiempo"
                    elif tag == "FORMULA_QA": tooltip_a_mostrar = "Qa = m * c * ΔT"
                    elif tag == "FORMULA_QL": tooltip_a_mostrar = "Ql = m_vap * L_vap"

        if tooltip_a_mostrar:
            self.dibujar_tooltip(screen, tooltip_a_mostrar, mouse_pos)

    def dibujar_tooltip(self, screen, texto, pos):
        padding = 5
        surf_texto = self.font_formula.render(texto, True, (0, 0, 0))
        bg_rect = surf_texto.get_rect()
        bg_rect.topleft = (pos[0] + 15, pos[1] + 15)
        bg_rect.width += padding * 2; bg_rect.height += padding * 2
        pygame.draw.rect(screen, (255, 255, 220), bg_rect) 
        pygame.draw.rect(screen, (0, 0, 0), bg_rect, 1)
        screen.blit(surf_texto, (bg_rect.x + padding, bg_rect.y + padding))


class MenuPrincipal:
    def __init__(self):
        self.font_titulo = pygame.font.Font(None, 80)
        self.font_botones = pygame.font.Font(None, 50)
        self.font_footer = pygame.font.Font(None, 24) 
        center_x = ANCHO // 2; start_y = 300
        self.btn_iniciar = pygame.Rect(center_x - 100, start_y, 200, 50)
        self.btn_teoria = pygame.Rect(center_x - 100, start_y + 80, 200, 50)
        self.btn_salir = pygame.Rect(center_x - 100, start_y + 160, 200, 50)
        self.integrantes = ["Integrantes:", "Burgos Pablo", "Genaro de Boni", "Eula Maximiliano", "Sajnovsky Jose"]

    def dibujar(self, screen):
        screen.fill(COLOR_FONDO)
        titulo = self.font_titulo.render("Simulación Termodinámica", True, (0, 0, 0))
        rect_titulo = titulo.get_rect(center=(ANCHO//2, 150))
        screen.blit(titulo, rect_titulo)
        botones = [(self.btn_iniciar, "Iniciar", (100, 200, 100)), (self.btn_teoria, "Teoría", (100, 150, 255)), (self.btn_salir, "Salir", (255, 100, 100))]
        for rect, texto, color in botones:
            pygame.draw.rect(screen, color, rect, border_radius=10)
            pygame.draw.rect(screen, (0,0,0), rect, 2, border_radius=10)
            surf = self.font_botones.render(texto, True, (255, 255, 255))
            text_rect = surf.get_rect(center=rect.center)
            screen.blit(surf, text_rect)
        start_y_nombres = ALTO - 20 - (len(self.integrantes) * 20) 
        for i, linea in enumerate(self.integrantes):
            surf_nombre = self.font_footer.render(linea, True, (80, 80, 80)) 
            screen.blit(surf_nombre, (20, start_y_nombres + (i * 20)))

    def manejar_clic(self, pos):
        if self.btn_iniciar.collidepoint(pos): return "SIMULACION"
        if self.btn_teoria.collidepoint(pos): return "TEORIA"
        if self.btn_salir.collidepoint(pos): return "SALIR"
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
        screen.fill((240, 240, 250)) 
        titulo = self.font_titulo.render("Teoría Aplicada", True, (0, 0, 0))
        screen.blit(titulo, (50, 50))
        y = 120
        for linea in self.textos:
            color = (0, 0, 150) if "Ley" in linea else (50, 50, 50)
            surf = self.font_texto.render(linea, True, color)
            screen.blit(surf, (50, y)); y += 35
        pygame.draw.rect(screen, (100, 100, 100), self.btn_volver, border_radius=10)
        txt = self.font_boton.render("Volver", True, (255, 255, 255))
        screen.blit(txt, txt.get_rect(center=self.btn_volver.center))
    def manejar_clic(self, pos):
        if self.btn_volver.collidepoint(pos): return "MENU"
        return None