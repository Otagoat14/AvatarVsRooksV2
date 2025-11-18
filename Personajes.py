import time
import pygame


TAMAÑO_CELDA = 80  
FILAS = 9
COLUMNAS = 5

# Colores de prueba
COLOR_FONDO = (30, 30, 40)
COLOR_GRID = (60, 60, 80)
COLOR_ROOK = (100, 200, 255)
COLOR_AVATAR = (255, 100, 100)
COLOR_BALA = (255, 255, 100)


# Clase Personaje
class Personaje:
    def __init__(self, vida, daño, velocidad_ataque, velocidad, y_fila, x_columna):
        self.y_fila = float(y_fila)
        self.x_columna = x_columna   
        self.vida = vida
        self.vida_maxima = vida 
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
    

    def disparar(self, direccion='arriba'): 
        tiempo_actual = time.time()
        if tiempo_actual - self.ultimo_ataque >= self.velocidad_ataque:
            nueva_bala = Bala(self.y_fila, self.x_columna, direccion)
            self.balas.append(nueva_bala)
            self.ultimo_ataque = tiempo_actual
            return nueva_bala
        return None

    def actualizar_balas(self):
        for bala in self.balas:
            bala.desplazarse()
        
        self.balas = [bala for bala in self.balas if bala.bala_activa]

    def dibujar_balas(self, pantalla, offset_x=0, offset_y=0): 
        for bala in self.balas:
            bala.dibujar(pantalla, offset_x, offset_y)


class Bala:
    def __init__(self, y_fila, x_columna, direccion='arriba'):
        self.y_fila = float(y_fila)
        self.x_columna = x_columna
        self.direccion = direccion
        self.velocidad_bala = 0.15 
        self.color = COLOR_BALA
        self.bala_activa = True

    def desplazarse(self):
        if self.direccion == 'arriba':
            self.y_fila -= self.velocidad_bala
        else:  
            self.y_fila += self.velocidad_bala

        if self.y_fila < 0 or self.y_fila >= FILAS:
            self.bala_activa = False

    def dibujar(self, pantalla, offset_x=0, offset_y=0):
        x = int(self.x_columna * TAMAÑO_CELDA + TAMAÑO_CELDA // 2) + offset_x
        y = int(self.y_fila * TAMAÑO_CELDA + TAMAÑO_CELDA // 2) + offset_y
        pygame.draw.circle(pantalla, self.color, (x, y), 6)


class Rooks(Personaje):
    def __init__(self, vida, daño, velocidad_ataque, y_fila, x_columna, tipo_rook, imagen=None):
        super().__init__(vida, daño, velocidad_ataque, velocidad=0, y_fila=y_fila, x_columna=x_columna)
        self.tipo_rook = tipo_rook 
        self.imagen = imagen        

    def disparar(self):
        return super().disparar(direccion='abajo')
    
    #DISPARO MANUAAL
    def disparar_manual(self):
        nueva_bala = Bala(self.y_fila, self.x_columna, direccion='abajo')
        self.balas.append(nueva_bala)
        return nueva_bala


    def dibujar(self, pantalla, offset_x=0, offset_y=0):
        x = int(self.x_columna * TAMAÑO_CELDA) + offset_x
        y = int(self.y_fila * TAMAÑO_CELDA) + offset_y
        
        if self.imagen:
            pantalla.blit(self.imagen, (x + 2, y + 2))
        else:
            pygame.draw.circle(pantalla, COLOR_ROOK, 
                             (x + TAMAÑO_CELDA // 2, y + TAMAÑO_CELDA // 2), 20)
        
        barra_ancho = TAMAÑO_CELDA - 10
        barra_alto = 5
        porcentaje_vida = self.vida / self.vida_maxima
        
        pygame.draw.rect(pantalla, (100, 0, 0), (x + 5, y + 2, barra_ancho, barra_alto))
        pygame.draw.rect(pantalla, (0, 255, 0), (x + 5, y + 2, int(barra_ancho * porcentaje_vida), barra_alto))


class Avatar(Personaje):
    def __init__(self, vida, daño, velocidad_ataque, y_fila, x_columna, velocidad_movimiento, tipo_avatar, valor_monedas):
        super().__init__(vida, daño, velocidad_ataque, velocidad=0, y_fila=y_fila, x_columna=x_columna)
        self.velocidad_movimiento = velocidad_movimiento  # Tiempo en segundos entre movimientos
        self.tipo_avatar = tipo_avatar  
        self.valor_monedas = valor_monedas  
        self.ultimo_movimiento = time.time()  # Tiempo del último movimiento
        self.y_fila_objetivo = float(y_fila)  # Posición objetivo (para movimiento suavizado)
        self.en_movimiento = False

    def mover(self):
        tiempo_actual = time.time()
        
        # Si no está en movimiento y ha pasado el tiempo suficiente, iniciar nuevo movimiento
        if not self.en_movimiento and tiempo_actual - self.ultimo_movimiento >= self.velocidad_movimiento:
            # Mover una casilla hacia arriba
            self.y_fila_objetivo = self.y_fila - 1.0
            self.ultimo_movimiento = tiempo_actual
            self.en_movimiento = True
            
            # Verificar si llegó al final (fila 0)
            if self.y_fila_objetivo <= 0:
                return True 
        
        # Suavizar movimiento si está en transición
        if self.en_movimiento:
            if abs(self.y_fila - self.y_fila_objetivo) > 0.05:
                # Interpolar hacia la posición objetivo
                diferencia = self.y_fila_objetivo - self.y_fila
                self.y_fila += diferencia * 0.2  # Velocidad de interpolación
            else:
                # Llegó a la posición objetivo
                self.y_fila = self.y_fila_objetivo
                self.en_movimiento = False
        
        return False

    def disparar(self):
        return super().disparar(direccion='arriba')

    def dibujar(self, pantalla, offset_x=0, offset_y=0):
        x = int(self.x_columna * TAMAÑO_CELDA) + offset_x
        y = int(self.y_fila * TAMAÑO_CELDA) + offset_y
        
        pygame.draw.rect(pantalla, COLOR_AVATAR, 
                        (x + 10, y + 10, TAMAÑO_CELDA - 20, TAMAÑO_CELDA - 20), 
                        border_radius=10)
        
        barra_ancho = TAMAÑO_CELDA - 20
        barra_alto = 5
        porcentaje_vida = self.vida / self.vida_maxima
        
        pygame.draw.rect(pantalla, (100, 0, 0), (x + 10, y + 5, barra_ancho, barra_alto))
        pygame.draw.rect(pantalla, (0, 255, 0), (x + 10, y + 5, int(barra_ancho * porcentaje_vida), barra_alto))