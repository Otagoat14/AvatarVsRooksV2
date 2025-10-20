import time
import pygame
from Constantes import (TAMAÑO_CELDA, FILAS)

# Colores de prueba 
COLOR_FONDO = (30, 30, 40)
COLOR_GRID = (60, 60, 80)
COLOR_ROOK = (100, 200, 255)
COLOR_AVATAR = (255, 100, 100)
COLOR_BALA = (255, 255, 100)

#Manejo de los Avatars
class Avatars :
    def __init__(self, vida, daño, velocidad_ataque, velocidad, tiempo_spawn, y_fila, x_columna):

        #Le damos un float para qeu el movimiento sea mas tipo smooth
        self.y_fila = float(y_fila)
        self.x_columna = x_columna
        self.vida = vida
        self.daño = daño
        self.velocidad_ataque = velocidad_ataque
        self.velocidad = velocidad
        self.tiempo_spawn = tiempo_spawn
        self.ultimo_ataque = 0
        self.avatar_vivo = True
        self.color = COLOR_AVATAR

    def moverse(self) :

        self.fila -= self.velocidad
        if self.fila <= 0 :
            self.avatar_vivo = False

    def recibir_daño (self, daño) :

        self.vida -= daño
        if self.vida <= 0 :
            self.avatar_vivo = False

    def dibujar_avatar_pantalla (self, pantalla, avatar) :

        #posición en píxeles
        x = self.columna * TAMAÑO_CELDA
        y = int(self.fila * TAMAÑO_CELDA)
        
        #El rectnagulo 
        pygame.draw.rect(pantalla, self.color, (x + 10, y + 10, TAMAÑO_CELDA - 20, TAMAÑO_CELDA - 20), border_radius=10)
        
        #Barrita de vida
        barra_ancho = TAMAÑO_CELDA - 20
        barra_alto = 5
        # Barra roja de fondo
        pygame.draw.rect(pantalla, (100, 0, 0), 
                        (x + 10, y + 5, barra_ancho, barra_alto))
        # Barra verde que representa la vida actual
        #En el 3 es donde va la vida del avatar como tal
        vida_ancho = int((self.vida / self.vida) * barra_ancho)
        pygame.draw.rect(pantalla, (0, 255, 0), (x + 10, y + 5, vida_ancho, barra_alto))


    def atacar_rook (self, objetivo_atacar) :

        tiempo_actual = time.time()

        # Verificar si ya pasó el tiempo necesario
        if tiempo_actual - self.ultimo_ataque >= self.velocidad_ataque :
            #Aqui pienso agregar unos ifs para que ataque solo cuando esta en la misma casilla que la rook

            objetivo_atacar.vida -= self.daño
            # Actualizar el tiempo del último ataque
            self.ultimo_ataque = tiempo_actual
            return True
            
        else:
            # Todavía no puede atacar
            tiempo_restante = self.velocidad_ataque - (tiempo_actual - self.ultimo_ataque)
            return False
        

class Bala :
    def __init__(self, y_fila, x_columna):

        self.y_fila = float(y_fila)
        self.x_columna = x_columna
        self.velocidad_bala = 0.1
        self.color = COLOR_BALA
        self.bala_activa = True

    def desplazarse(self):

        self.y_fila += self.velocidad_bala
        if self.y_fila >= FILAS :
            self.bala_activa = False

    def dibujar (self, pantalla) :

        #posición en píxeles
        x = self.x_columna * TAMAÑO_CELDA + TAMAÑO_CELDA // 2
        y = int(self.fila * TAMAÑO_CELDA) + TAMAÑO_CELDA // 2
        
        pygame.draw.circle(pantalla, self.color, (x, y), 8)
    
    
#TIPOS DE AVATARS
Flechero = Avatars(vida = 5, daño = 2, velocidad_ataque = 10, velocidad = 12, tiempo_spawn = 4)
Escudero = Avatars(vida = 10, daño = 3, velocidad_ataque = 15, velocidad = 10, tiempo_spawn = 6)
Leñador = Avatars(vida = 20, daño = 9, velocidad_ataque = 5, velocidad = 13, tiempo_spawn = 8)
Canibal = Avatars(vida = 25, daño = 12, velocidad_ataque = 3, velocidad = 14, tiempo_spawn = 10)





