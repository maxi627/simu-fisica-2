import math
import random
import sys

import pygame

pygame.init()
ancho, alto = 1280, 720
screen = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Simulación Termodinámica")
clock = pygame.time.Clock()

class Particula:
    def __init__(self, x, y, radio, color, vel_max):
        self.x = x
        self.y = y
        self.radio = radio
        self.color = color
        self.vx = random.uniform(-vel_max, vel_max)
        self.vy = random.uniform(-vel_max, vel_max)

    def mover(self, num_steps):
        self.x += self.vx / num_steps
        self.y += self.vy / num_steps

    def dibujar(self, superficie):
        pygame.draw.circle(superficie, self.color, (int(self.x), int(self.y)), self.radio)


def detectar_y_rebotar_circulo_linea(particula, p1, p2):
    
    # 1. Encontrar el punto más cercano en el segmento de línea
    dx_line = p2[0] - p1[0]
    dy_line = p2[1] - p1[1]
    longitud_cuadrada = dx_line**2 + dy_line**2

    if longitud_cuadrada == 0: # Es un punto
        return

    t = ((particula.x - p1[0]) * dx_line + (particula.y - p1[1]) * dy_line) / longitud_cuadrada
    t = max(0, min(1, t)) # Limitar al segmento

    punto_mas_cercano_x = p1[0] + t * dx_line
    punto_mas_cercano_y = p1[1] + t * dy_line

    # 2. Vector desde el punto de la pared al centro de la partícula
    distancia_x = particula.x - punto_mas_cercano_x
    distancia_y = particula.y - punto_mas_cercano_y
    distancia = math.sqrt(distancia_x**2 + distancia_y**2)

    # 3. Colisión detectada
    if distancia < particula.radio and distancia > 0.001:
        
        # 4. LA NORMAL es el vector desde la pared a la partícula
        normal_x = distancia_x / distancia
        normal_y = distancia_y / distancia
        
        overlap = particula.radio - distancia
        
        # 5. "Push" (Empuje) fuera de la pared
        particula.x += normal_x * overlap
        particula.y += normal_y * overlap
        
        # 6. Reflexión (Rebote)
        dot_product = particula.vx * normal_x + particula.vy * normal_y
        
        particula.vx -= 2 * dot_product * normal_x
        particula.vy -= 2 * dot_product * normal_y
        
        particula.vx *= 0.95 # Fricción lateral


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

# Constantes de Física (Valores totales por fotograma)
GRAVEDAD = 0.02
EMPUJE_CALOR = 0.05
MAX_VELOCIDAD = 5.0 # LÍMITE DE VELOCIDAD MÁXIMA

# Coordenadas de las paredes del contenedor
PAREDES_CONTENEDOR = [
    ((260, 150), (505, 150)), 
    ((505, 150), (520, 200)),
    ((520, 200), (535, 300)),
    ((535, 300), (550, 450)),
    ((230, 450), (245, 300)), 
    ((245, 300), (260, 150)),
]

# --- APROXIMACIÓN DEL ARCO INFERIOR DE LA PAVA ---
puntos_del_arco = []
num_segmentos = 10 

centro_x_arco = 390; centro_y_arco = 450 
radio_x_arco = 165; radio_y_arco = 50

for i in range(num_segmentos + 1):
    angulo = (i / num_segmentos) * math.pi
    x = centro_x_arco + radio_x_arco * math.cos(angulo + math.pi)
    y = centro_y_arco + radio_y_arco * math.sin(angulo)
    puntos_del_arco.append((int(x), int(y)))

for i in range(num_segmentos):
    PAREDES_CONTENEDOR.append((puntos_del_arco[i], puntos_del_arco[i+1]))
    
PAREDES_CONTENEDOR.append(((230, 450), puntos_del_arco[0]))
PAREDES_CONTENEDOR.append(((550, 450), puntos_del_arco[-1])) 


# Variables de la simulación
PARTICULAS = []
RADIO_PARTICULA = 5
CANTIDAD_PARTICULAS = 70
VELOCIDAD_MAX_INICIAL = 2.0 

# Área de SPAWN
min_x_spawn = 265; max_x_spawn = 500
min_y_spawn = 160; max_y_spawn = 400

for _ in range(CANTIDAD_PARTICULAS):
    px = random.randint(min_x_spawn, max_x_spawn)
    py = random.randint(min_y_spawn, max_y_spawn)
    nueva_particula = Particula(px, py, RADIO_PARTICULA, (0, 100, 255), VELOCIDAD_MAX_INICIAL)
    PARTICULAS.append(nueva_particula)
    
run = True

while run:
    # A. Gestión de Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            run = False
            
    # B. ACTUALIZACIÓN DE LA LÓGICA (CON SUB-PASOS)
    for p in PARTICULAS:
        
        # Bucle de Sub-Pasos: 
        for _ in range(SUB_STEPS):
            
            # 1. Mover (1/8 de la velocidad)
            p.mover(SUB_STEPS) 
            
            # 2. Resolver todas las colisiones
            for pared_p1, pared_p2 in PAREDES_CONTENEDOR:
                detectar_y_rebotar_circulo_linea(p, pared_p1, pared_p2)

            # 3. Aplicar nuevas fuerzas (1/8 de la fuerza)
            p.vy += GRAVEDAD / SUB_STEPS
            
            ZONA_CALOR_Y = 430
            if p.y > ZONA_CALOR_Y:
                p.vy -= EMPUJE_CALOR / SUB_STEPS
            
            # 4. LÍMITE DE VELOCIDAD
            velocidad_actual = math.sqrt(p.vx**2 + p.vy**2)
            
            if velocidad_actual > MAX_VELOCIDAD:
                factor = MAX_VELOCIDAD / velocidad_actual
                p.vx *= factor
                p.vy *= factor

    # C. DIBUJO / RENDERIZADO (Solo se dibuja UNA VEZ por frame)
    screen.fill("white")


    # 1. Dibuja las PAREDES (quedarán ABAJO de la imagen de la pava)
    for p1, p2 in PAREDES_CONTENEDOR:
        pygame.draw.line(screen, "black", p1, p2, 8)
    
    # 2. Dibuja la IMAGEN de la pava (quedará ENCIMA de las paredes)
    screen.blit(pava_img_escalada, (200, 100))

    # 3. Dibuja las PARTICULAS (quedarán ENCIMA de la imagen de la pava)
    for p in PARTICULAS:
        p.dibujar(screen)

    # D. Actualizar pantalla y controlar FPS
    pygame.display.flip()
    clock.tick(120)

# 3. Finalización:
pygame.quit()
sys.exit()