import time
import pygame

# Constantes
TAMAÑO_CELDA = 50  # tamaño de cada celda en la grilla
FILAS = 9  # número de filas

# Colores de prueba
COLOR_FONDO = (30, 30, 40)
COLOR_GRID = (60, 60, 80)
COLOR_ROOK = (100, 200, 255)
COLOR_AVATAR = (255, 100, 100)
COLOR_BALA = (255, 255, 100)


# Clase Personaje
class Personaje:
    def __init__(self, vida, daño, velocidad_ataque, velocidad, y_fila, x_columna):
        self.y_fila = y_fila
        self.x_columna = x_columna
        self.vida = vida
        self.daño = daño
        self.velocidad_ataque = velocidad_ataque
        self.velocidad = velocidad
        self.ultimo_ataque = 0
        self.personaje_vivo = True
        self.balas = []

    def recibir_daño(self, daño):
        self.vida -= daño
        if self.vida <= 0:
            self.personaje_vivo = False
        print("La vida del personaje es:", self.vida)

    def disparar(self):
        tiempo_actual = time.time()
        if tiempo_actual - self.ultimo_ataque >= self.velocidad_ataque:
            nueva_bala = Bala(self.y_fila, self.x_columna)
            self.balas.append(nueva_bala)
            self.ultimo_ataque = tiempo_actual
            return nueva_bala

    def actualizar_balas(self):
        for bala in self.balas:
            bala.desplazarse()

        self.balas = [bala for bala in self.balas if bala.bala_activa]

    def dibujar_balas(self, pantalla):
        for bala in self.balas:
            bala.dibujar(pantalla)


class Bala:
    def __init__(self, y_fila, x_columna, direccion='arriba'):
        self.y_fila = y_fila
        self.x_columna = x_columna
        self.direccion = direccion
        self.velocidad_bala = 0.1
        self.color = COLOR_BALA
        self.bala_activa = True

    def desplazarse(self):
        if self.direccion == 'arriba':
            self.y_fila -= self.velocidad_bala
        else:
            self.y_fila += self.velocidad_bala

        if self.y_fila < 0 or self.y_fila >= FILAS:
            self.bala_activa = False

    def dibujar(self, pantalla):
        x = self.x_columna * TAMAÑO_CELDA + TAMAÑO_CELDA // 2
        y = int(self.y_fila * TAMAÑO_CELDA) + TAMAÑO_CELDA // 2
        pygame.draw.circle(pantalla, self.color, (x, y), 8)


class Rooks(Personaje):
    def __init__(self, vida, daño, velocidad_ataque, y_fila, x_columna):
        super().__init__(vida, daño, velocidad_ataque, velocidad=0, y_fila=y_fila, x_columna=x_columna)

    def dibujar(self, pantalla):
        x = self.x_columna * TAMAÑO_CELDA
        y = self.y_fila * TAMAÑO_CELDA
        pygame.draw.circle(pantalla, COLOR_ROOK, (x + TAMAÑO_CELDA // 2, y + TAMAÑO_CELDA // 2), 15)


class Avatar(Personaje):
    def __init__(self, vida, daño, velocidad_ataque, y_fila, x_columna, velocidad_movimiento):
        super().__init__(vida, daño, velocidad_ataque, velocidad=0, y_fila=y_fila, x_columna=x_columna)
        self.velocidad_movimiento = velocidad_movimiento

    def mover(self):
        if self.y_fila > 1:
            self.y_fila -= self.velocidad_movimiento
        else:
            self.y_fila = 1  

    def colocar_avatar(self, pantalla):
        x = self.x_columna * TAMAÑO_CELDA
        y = self.y_fila * TAMAÑO_CELDA
        pygame.draw.rect(pantalla, COLOR_AVATAR, (x + 10, y + 10, TAMAÑO_CELDA - 20, TAMAÑO_CELDA - 20), border_radius=10)



