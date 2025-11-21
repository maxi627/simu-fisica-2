import sys
import pygame
import math
import random

from config import *
from utils import map_value, generar_paredes_pava, detectar_y_rebotar_circulo_linea
from entities import Particula, ParticulaVapor
from interface import HUD

class SimulacionPava:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption(TITULO)
        self.clock = pygame.time.Clock()
        self.hud = HUD()
        
        # Carga de Assets
        try:
            img = pygame.image.load(RUTA_IMAGEN_PAVA)
            self.img_pava = pygame.transform.scale(img, (500, 500))
            self.snd_hervir = pygame.mixer.Sound(RUTA_SONIDO_HERVIR)
            self.snd_hervir.set_volume(0.5)
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar assets ({e})")
            self.img_pava = None
            self.snd_hervir = None

        self.paredes = generar_paredes_pava()
        self.resetear_simulacion()

    def resetear_simulacion(self):
        self.potencia = 2000.0
        self.masa_agua = 1.0
        self.temperatura_promedio = TEMP_AMBIENTE
        self.tiempo_sim = 0.0
        self.encendida = True
        self.hirviendo = False
        self.snd_reproduciendo = False
        
        self.particulas = []
        self.vapores = []
        self.masa_vaporizada_acum = 0.0
        
        if self.snd_hervir: self.snd_hervir.stop()
        self.ajustar_cantidad_particulas()

    def ajustar_cantidad_particulas(self):
        """Sincroniza la cantidad de partículas con la masa actual."""
        target_count = int(self.masa_agua * PARTICULAS_POR_KG)
        diff = target_count - len(self.particulas)
        
        if diff > 0:
            for _ in range(diff):
                self.crear_particula()
        elif diff < 0:
            for _ in range(abs(diff)):
                if self.particulas: self.particulas.pop()

    def crear_particula(self):
        lvl_top = map_value(self.masa_agua, MASA_MIN, MASA_MAX, Y_NIVEL_FONDO, Y_NIVEL_TOPE)
        y_start = int(lvl_top)
        y_end = Y_NIVEL_FONDO
        if y_start > y_end: y_start = y_end
        
        px = random.randint(MIN_X_SPAWN, MAX_X_SPAWN)
        py = random.randint(y_start, y_end)
        
        self.particulas.append(Particula(px, py, 2.0))

    def crear_vapor(self):
        lvl_top = map_value(self.masa_agua, MASA_MIN, MASA_MAX, Y_NIVEL_FONDO, Y_NIVEL_TOPE)
        px = random.randint(MIN_X_SPAWN + 20, MAX_X_SPAWN - 20)
        py = lvl_top + random.uniform(-5, 5)
        self.vapores.append(ParticulaVapor(px, py))

    def manejar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.resetear_simulacion()
                elif event.key == pygame.K_SPACE:
                    self.encendida = not self.encendida
                    if not self.encendida and self.snd_hervir:
                        self.snd_hervir.stop()
                        self.snd_reproduciendo = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                p, m = self.hud.manejar_clic(pygame.mouse.get_pos(), self.potencia, self.masa_agua)
                self.potencia = p
                if m != self.masa_agua:
                    self.masa_agua = m
                    self.ajustar_cantidad_particulas()
        return True

    def update_fisica(self, dt):
        if not self.particulas: return

        # --- 1. Termodinámica ---
        potencia_aplicada = self.potencia if self.encendida else 0
        perdida_total = 0
        masa_p = self.masa_agua / len(self.particulas)
        particulas_calor = [p for p in self.particulas if p.y > ZONA_CALOR_Y]
        
        pot_por_particula = 0
        if particulas_calor and self.encendida:
            pot_por_particula = potencia_aplicada / len(particulas_calor)

        temp_acum = 0
        for p in self.particulas:
            # Enfriamiento
            if p.temperatura > TEMP_AMBIENTE:
                p_perdida = K_ENFRIAMIENTO_PARTICULA * (p.temperatura - TEMP_AMBIENTE)
                perdida_total += p_perdida
                dT = (p_perdida * dt) / (masa_p * CALOR_ESPECIFICO_AGUA)
                p.temperatura = max(TEMP_AMBIENTE, p.temperatura - dT)
            
            # Calentamiento
            if self.encendida and p in particulas_calor:
                dT = (pot_por_particula * dt) / (masa_p * CALOR_ESPECIFICO_AGUA)
                p.temperatura = min(TEMP_EBULLICION, p.temperatura + dT)
            
            temp_acum += p.temperatura
            p.update_color()

        self.temperatura_promedio = temp_acum / len(self.particulas)
        self.hirviendo = self.temperatura_promedio >= (TEMP_EBULLICION - 0.1)

        # --- 2. Vaporización y Sonido ---
        if self.hirviendo:
            if self.encendida and self.snd_hervir and not self.snd_reproduciendo:
                self.snd_hervir.play(loops=-1)
                self.snd_reproduciendo = True
            
            pot_neta = potencia_aplicada - perdida_total
            if pot_neta > 0 and self.masa_agua > 0:
                masa_vap = (pot_neta * dt) / CALOR_LATENTE_VAPORIZACION
                self.masa_agua = max(0, self.masa_agua - masa_vap)
                self.masa_vaporizada_acum += masa_vap
                
                n_vap = int(self.masa_vaporizada_acum * PARTICULAS_POR_KG)
                if n_vap > 0:
                    self.masa_vaporizada_acum -= n_vap / PARTICULAS_POR_KG
                    # Eliminar partículas más calientes
                    self.particulas.sort(key=lambda x: x.temperatura)
                    for _ in range(min(n_vap, len(self.particulas))):
                        self.particulas.pop()
                        for _ in range(PARTICULAS_VAPOR_POR_LIQUIDA):
                            self.crear_vapor()
        else:
            if self.snd_reproduciendo and self.snd_hervir:
                self.snd_hervir.stop()
                self.snd_reproduciendo = False

        # --- 3. Movimiento y Colisiones (Sub-steps) ---
        for p in self.particulas:
            ratio_temp = (p.temperatura - TEMP_AMBIENTE) / (TEMP_EBULLICION - TEMP_AMBIENTE)
            empuje = ratio_temp * MAX_EMPUJE_CALOR_PARTICULA
            v_max = MAX_VELOCIDAD_BASE + (ratio_temp * (MAX_VELOCIDAD_TOPE - MAX_VELOCIDAD_BASE))
            
            for _ in range(SUB_STEPS):
                p.mover(SUB_STEPS)
                for w1, w2 in self.paredes:
                    detectar_y_rebotar_circulo_linea(p, w1, w2)
                
                p.vy += GRAVEDAD / SUB_STEPS
                p.vy -= empuje / SUB_STEPS # Convección
                
                # Limitar velocidad
                v_actual = math.sqrt(p.vx**2 + p.vy**2)
                if v_actual > v_max:
                    factor = v_max / v_actual
                    p.vx *= factor; p.vy *= factor

        # --- 4. Actualizar Vapor ---
        for pv in self.vapores[:]:
            pv.update(dt)
            if not pv.viva: self.vapores.remove(pv)
            
        if self.encendida: self.tiempo_sim += dt

    def dibujar(self):
        self.screen.fill("white")
        if self.img_pava:
            self.screen.blit(self.img_pava, (200, 100))
        

        for p in self.particulas: p.dibujar(self.screen)
        for pv in self.vapores: pv.dibujar(self.screen)
        
        # Datos para el HUD
        data_hud = {
            'temp': self.temperatura_promedio,
            'tiempo': self.tiempo_sim,
            'potencia': self.potencia,
            'masa': self.masa_agua,
            'encendida': self.encendida,
            'n_particulas': len(self.particulas)
        }
        self.hud.dibujar(self.screen, data_hud)
        
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.get_time() / 1000.0
            if not self.manejar_eventos(): break
            self.update_fisica(dt)
            self.dibujar()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    sim = SimulacionPava()
    sim.run()