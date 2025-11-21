import math

from config import PAREDES_ESTATICAS


def map_value(value, from_low, from_high, to_low, to_high):
    """Mapea un valor de un rango a otro."""
    value = max(from_low, min(from_high, value))
    return to_low + (value - from_low) * (to_high - to_low) / (from_high - from_low)

def generar_paredes_pava():
    """Genera la lista completa de paredes incluyendo el arco inferior."""
    paredes = list(PAREDES_ESTATICAS) 
    puntos_del_arco = []
    num_segmentos = 10
    centro_x_arco = 390; centro_y_arco = 450; radio_x_arco = 165; radio_y_arco = 50
    
    for i in range(num_segmentos + 1):
        angulo = (i / num_segmentos) * math.pi
        x = centro_x_arco + radio_x_arco * math.cos(angulo + math.pi)
        y = centro_y_arco + radio_y_arco * math.sin(angulo)
        puntos_del_arco.append((int(x), int(y)))
        
    for i in range(num_segmentos):
        paredes.append((puntos_del_arco[i], puntos_del_arco[i+1]))
        
    paredes.append(((230, 450), puntos_del_arco[0]))
    paredes.append(((550, 450), puntos_del_arco[-1]))
    return paredes

def detectar_y_rebotar_circulo_linea(particula, p1, p2):
    """Lógica de colisión matemática."""
    dx_line = p2[0] - p1[0]
    dy_line = p2[1] - p1[1]
    longitud_cuadrada = dx_line**2 + dy_line**2
    
    if longitud_cuadrada == 0: return

    t = ((particula.x - p1[0]) * dx_line + (particula.y - p1[1]) * dy_line) / longitud_cuadrada
    t = max(0, min(1, t))
    
    punto_cercano_x = p1[0] + t * dx_line
    punto_cercano_y = p1[1] + t * dy_line
    
    dist_x = particula.x - punto_cercano_x
    dist_y = particula.y - punto_cercano_y
    distancia = math.sqrt(dist_x**2 + dist_y**2)
    
    if 0.001 < distancia < particula.radio:
        normal_x = dist_x / distancia
        normal_y = dist_y / distancia
        overlap = particula.radio - distancia
        
        particula.x += normal_x * overlap
        particula.y += normal_y * overlap
        
        dot_product = particula.vx * normal_x + particula.vy * normal_y
        particula.vx -= 2 * dot_product * normal_x
        particula.vy -= 2 * dot_product * normal_y
        particula.vx *= 0.99
        particula.vy *= 0.99