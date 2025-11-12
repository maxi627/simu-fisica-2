import math
import random
import sys

import pygame

# 1. Inicialización
pygame.init()
pygame.font.init() # Inicializa el módulo de fuentes
ancho, alto = 1280, 720
screen = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Simulación Termodinámica")
clock = pygame.time.Clock()

# Fuente para el HUD
font_hud = pygame.font.Font(None, 30)


# --- CLASE PARTICULA 
class Particula:
    def __init__(self, x, y, radio, color_inicial, vel_max):
        self.x = x
        self.y = y
        self.radio = radio
        self.color = color_inicial
        self.vx = random.uniform(-vel_max, vel_max)
        self.vy = random.uniform(-vel_max, vel_max)
    def mover(self, num_steps):
        self.x += self.vx / num_steps
        self.y += self.vy / num_steps
    def dibujar(self, superficie):
        pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), self.radio)
    def update_color(self, min_vel, max_vel, color_frio, color_caliente):
        velocidad = math.sqrt(self.vx**2 + self.vy**2)
        ratio = (velocidad - min_vel) / (max_vel - min_vel)
        ratio = max(0, min(1, ratio))
        r = int(color_frio[0] + (color_caliente[0] - color_frio[0]) * ratio)
        g = int(color_frio[1] + (color_caliente[1] - color_frio[1]) * ratio)
        b = int(color_frio[2] + (color_caliente[2] - color_frio[2]) * ratio)
        self.color = (r, g, b)


# --- FUNCIÓN DE COLISIÓN 
def detectar_y_rebotar_circulo_linea(particula, p1, p2):
    dx_line = p2[0] - p1[0]; dy_line = p2[1] - p1[1]; longitud_cuadrada = dx_line**2 + dy_line**2
    if longitud_cuadrada == 0: return
    t = ((particula.x - p1[0]) * dx_line + (particula.y - p1[1]) * dy_line) / longitud_cuadrada
    t = max(0, min(1, t)) 
    punto_mas_cercano_x = p1[0] + t * dx_line; punto_mas_cercano_y = p1[1] + t * dy_line
    distancia_x = particula.x - punto_mas_cercano_x; distancia_y = particula.y - punto_mas_cercano_y
    distancia = math.sqrt(distancia_x**2 + distancia_y**2)
    if distancia < particula.radio and distancia > 0.001:
        normal_x = distancia_x / distancia; normal_y = distancia_y / distancia
        overlap = particula.radio - distancia
        particula.x += normal_x * overlap; particula.y += normal_y * overlap
        dot_product = particula.vx * normal_x + particula.vy * normal_y
        particula.vx -= 2 * dot_product * normal_x; particula.vy -= 2 * dot_product * normal_y
        particula.vx *= 0.95


# --- CONFIGURACIÓN DE GRÁFICOS Y FÍSICA ---
ruta_imagen = 'pava.webp'
try:
    pava_img = pygame.image.load(ruta_imagen)
    pava_img_escalada = pygame.transform.scale(pava_img, (500, 500))
except pygame.error as e:
    print(f"Error al cargar la imagen: {e}")
    sys.exit()

# CONFIGURACIÓN DE SUB-PASOS
SUB_STEPS = 8

# Constantes Termodinámicas
CALOR_ESPECIFICO_AGUA = 4186
TEMP_AMBIENTE = 20.0
TEMP_EBULLICION = 100.0
K_DISIPACION = 10.0

# Constantes Físicas Base
GRAVEDAD = 0.02
MAX_EMPUJE_CALOR = 0.05
MAX_VELOCIDAD_BASE = 2.0
MAX_VELOCIDAD_TOPE = 5.0

# CONSTANTES DE NIVEL
MASA_MIN = 0.5 # kg
MASA_MAX = 2.0 # kg
Y_NIVEL_BAJO = 400 # Y-pixel para la masa mínima
Y_NIVEL_ALTO = 160 # Y-pixel para la masa máxima


def map_value(value, from_low, from_high, to_low, to_high):
    """ Mapea un valor de un rango a otro """
    # Asegurar que el valor esté dentro del rango original
    value = max(from_low, min(from_high, value))
    return to_low + (value - from_low) * (to_high - to_low) / (from_high - from_low)

# Variables de Control (Mutables)
POTENCIA_PAVA = 2000.0
MASA_AGUA = 1.0 # Empezamos con 1.0 kg

# Variables de Estado
temperatura_actual = TEMP_AMBIENTE
tiempo_simulado = 0.0
esta_hirviendo = False

# Constantes de Color
COLOR_FRIO = (255,0,0); COLOR_CALIENTE = (0,100,255); VEL_MIN_COLOR = 0.0 

# Coordenadas de las paredes
PAREDES_CONTENEDOR = [
    ((260, 150), (505, 150)), ((505, 150), (520, 200)), ((520, 200), (535, 300)),
    ((535, 300), (550, 450)), ((230, 450), (245, 300)), ((245, 300), (260, 150)),
]

# --- APROXIMACIÓN DEL ARCO INFERIOR ---
puntos_del_arco = []
num_segmentos = 10 
centro_x_arco = 390; centro_y_arco = 450; radio_x_arco = 165; radio_y_arco = 50   
for i in range(num_segmentos + 1):
    angulo = (i / num_segmentos) * math.pi
    x = centro_x_arco + radio_x_arco * math.cos(angulo + math.pi)
    y = centro_y_arco + radio_y_arco * math.sin(angulo)
    puntos_del_arco.append((int(x), int(y)))
for i in range(num_segmentos):
    PAREDES_CONTENEDOR.append((puntos_del_arco[i], puntos_del_arco[i+1]))
PAREDES_CONTENEDOR.append(((230, 450), puntos_del_arco[0]))
PAREDES_CONTENEDOR.append(((550, 450), puntos_del_arco[-1])) 


# --- DEFINICIÓN DE BOTONES DEL MENÚ 
X_MENU_ANCLA = 750
COLOR_BOTON = (220, 220, 220)
COLOR_TEXTO_BOTON = (0, 0, 0)
pot_down_rect = pygame.Rect(X_MENU_ANCLA, 80, 25, 25); pot_up_rect = pygame.Rect(X_MENU_ANCLA + 30, 80, 25, 25)
masa_down_rect = pygame.Rect(X_MENU_ANCLA, 110, 25, 25); masa_up_rect = pygame.Rect(X_MENU_ANCLA + 30, 110, 25, 25)
texto_plus = font_hud.render("+", True, COLOR_TEXTO_BOTON); texto_minus = font_hud.render("-", True, COLOR_TEXTO_BOTON)


#VARIABLES DE SIMULACIÓN Y FUNCIÓN DE CREACIÓN ---
PARTICULAS = []
RADIO_PARTICULA = 5
VELOCIDAD_MAX_INICIAL = 2.0 
PARTICULAS_POR_KG = 150 

min_x_spawn = 265; max_x_spawn = 500 

def crear_particula(masa_actual):
    """Crea y devuelve una nueva partícula DENTRO del volumen de agua actual."""
    nivel_superior_y = map_value(masa_actual, MASA_MIN, MASA_MAX, Y_NIVEL_BAJO, Y_NIVEL_ALTO)
    
    # El spawn ocurre entre el nuevo nivel superior y el nivel más bajo
    px = random.randint(min_x_spawn, max_x_spawn)
    py = random.randint(int(nivel_superior_y), Y_NIVEL_BAJO) 
    
    return Particula(px, py, RADIO_PARTICULA, COLOR_FRIO, VELOCIDAD_MAX_INICIAL)

# Creación inicial de partículas
cantidad_inicial = int(MASA_AGUA * PARTICULAS_POR_KG)
for _ in range(cantidad_inicial):
    PARTICULAS.append(crear_particula(MASA_AGUA))
    
run = True

# 2. Bucle Principal del Juego
while run:
    
    dt = clock.get_time() / 1000.0
    
    # A. Gestión de Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            run = False
        
        #LÓGICA DE CLICS (ACTUALIZADA PARA MASA)
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if pot_up_rect.collidepoint(mouse_pos):
                POTENCIA_PAVA += 100
            elif pot_down_rect.collidepoint(mouse_pos):
                POTENCIA_PAVA -= 100; 
                if POTENCIA_PAVA < 0: POTENCIA_PAVA = 0
                
            elif masa_up_rect.collidepoint(mouse_pos):
                if MASA_AGUA < MASA_MAX:
                    MASA_AGUA += 0.1
                    # Añadir partículas (7 en este caso)
                    for _ in range(int(PARTICULAS_POR_KG / 10)):
                        PARTICULAS.append(crear_particula(MASA_AGUA))
                    
            elif masa_down_rect.collidepoint(mouse_pos):
                if MASA_AGUA > MASA_MIN:
                    MASA_AGUA -= 0.1
                    # Quitar partículas
                    for _ in range(int(PARTICULAS_POR_KG / 10)):
                        if PARTICULAS: PARTICULAS.pop()

        #Lógica de teclado (ACTUALIZADA PARA RESET)
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_r:
                temperatura_actual = TEMP_AMBIENTE
                tiempo_simulado = 0.0
                esta_hirviendo = False
                
                # Resetear partículas a la masa actual
                PARTICULAS.clear()
                cantidad_actual = int(MASA_AGUA * PARTICULAS_POR_KG)
                for _ in range(cantidad_actual):
                    PARTICULAS.append(crear_particula(MASA_AGUA)) # Rellena al nivel actual
            
    # B. ACTUALIZACIÓN DE LA LÓGICA
    
    # --- 1. CÁLCULO TERMODINÁMICO ---
    if not esta_hirviendo:
        P_perdida = K_DISIPACION * (temperatura_actual - TEMP_AMBIENTE)
        P_neta = POTENCIA_PAVA - P_perdida
        
        if P_neta > 0 and MASA_AGUA > 0:
            dT = (P_neta / (MASA_AGUA * CALOR_ESPECIFICO_AGUA)) * dt
            temperatura_actual += dT
        
        tiempo_simulado += dt

        if temperatura_actual >= TEMP_EBULLICION:
            temperatura_actual = TEMP_EBULLICION
            esta_hirviendo = True
            print(f"¡Hervido en {tiempo_simulado:.2f} segundos!")

    # --- 2. MAPEAR TEMPERATURA A FÍSICA ---
    temp_ratio = (temperatura_actual - TEMP_AMBIENTE) / (TEMP_EBULLICION - TEMP_AMBIENTE)
    temp_ratio = max(0, min(1, temp_ratio))
    empuje_actual = temp_ratio * MAX_EMPUJE_CALOR
    max_vel_actual = MAX_VELOCIDAD_BASE + (temp_ratio * (MAX_VELOCIDAD_TOPE - MAX_VELOCIDAD_BASE))

    # --- 3. BUCLE DE SUB-PASOS (Física de colisión) ---
    for p in PARTICULAS:
        
        for _ in range(SUB_STEPS):
            p.mover(SUB_STEPS) 
            
            for pared_p1, pared_p2 in PAREDES_CONTENEDOR:
                detectar_y_rebotar_circulo_linea(p, pared_p1, pared_p2)

            p.vy += GRAVEDAD / SUB_STEPS
            
            ZONA_CALOR_Y = 430 
            if p.y > ZONA_CALOR_Y:
                p.vy -= empuje_actual / SUB_STEPS
            
            velocidad_actual = math.sqrt(p.vx**2 + p.vy**2)
            if velocidad_actual > max_vel_actual:
                factor = max_vel_actual / velocidad_actual
                p.vx *= factor
                p.vy *= factor
        
        p.update_color(VEL_MIN_COLOR, max_vel_actual, COLOR_FRIO, COLOR_CALIENTE)

    # C. DIBUJO / RENDERIZADO
    screen.fill("white")

    for p1, p2 in PAREDES_CONTENEDOR:
        pygame.draw.line(screen, "black", p1, p2, 8) 
    
    screen.blit(pava_img_escalada, (200, 100))

    for p in PARTICULAS:
        p.dibujar(screen)
        
    # 4. DIBUJAR EL HUD (Posición Corregida)
    
    pygame.draw.rect(screen, COLOR_BOTON, pot_up_rect)
    pygame.draw.rect(screen, COLOR_BOTON, pot_down_rect)
    pygame.draw.rect(screen, COLOR_BOTON, masa_up_rect)
    pygame.draw.rect(screen, COLOR_BOTON, masa_down_rect)
    
    screen.blit(texto_plus, (pot_up_rect.x + 7, pot_up_rect.y + 2))
    screen.blit(texto_minus, (pot_down_rect.x + 8, pot_down_rect.y + 2))
    screen.blit(texto_plus, (masa_up_rect.x + 7, masa_up_rect.y + 2))
    screen.blit(texto_minus, (masa_down_rect.x + 8, masa_down_rect.y + 2))
    
    texto_temp = font_hud.render(f"Temp: {temperatura_actual:.1f}°C", True, (0,0,0))
    texto_tiempo = font_hud.render(f"Tiempo: {tiempo_simulado:.1f} s", True, (0,0,0))
    texto_potencia = font_hud.render(f"Potencia: {POTENCIA_PAVA:.0f} W", True, (0,0,0))
    texto_masa = font_hud.render(f"Masa: {MASA_AGUA:.1f} kg", True, (0,0,0))
    texto_particulas = font_hud.render(f"Partículas: {len(PARTICULAS)}", True, (100,100,100))
    texto_reset = font_hud.render("Presiona 'R' para reiniciar", True, (50,50,50))
    
    screen.blit(texto_temp, (X_MENU_ANCLA, 20))
    screen.blit(texto_tiempo, (X_MENU_ANCLA, 50))
    screen.blit(texto_potencia, (X_MENU_ANCLA + 65, 85)) 
    screen.blit(texto_masa, (X_MENU_ANCLA + 65, 115))   
    screen.blit(texto_particulas, (X_MENU_ANCLA, 145))
    screen.blit(texto_reset, (X_MENU_ANCLA, 175))


    # D. Actualizar pantalla y controlar FPS
    pygame.display.flip()
    clock.tick(120)

# 3. Finalización:
pygame.quit()
sys.exit()