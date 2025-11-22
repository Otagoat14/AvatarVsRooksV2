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
        self.ultimo_ataque = time.time()  # Inicializar con tiempo actual
        self.personaje_vivo = True
        self.balas = []
        self.rango_ataque = 1.0

    def recibir_daño(self, daño):
        self.vida -= daño
        if self.vida <= 0:
            self.personaje_vivo = False
    
    def tiene_rook_al_frente(self, juego):
        """Verifica si hay un rook en la casilla inmediatamente adelante"""
        fila_adelante = int(self.y_fila) - 1  # Casilla inmediatamente arriba
        if fila_adelante < 0:  # Si está en la primera fila
            return False
            
        # Verificar si hay rook en esa posición
        for rook in juego.rooks_activos:
            if (rook.personaje_vivo and 
                int(rook.y_fila) == fila_adelante and 
                rook.x_columna == self.x_columna):
                return True
        return False

    def puede_atacar(self, juego):
        """Verifica si puede atacar (rook al frente y en rango)"""
        if not self.tiene_rook_al_frente(juego):
            return False
            
        # Para ataque cuerpo a cuerpo, siempre puede atacar si hay rook al frente
        return True

    def disparar(self, direccion='arriba', juego=None): 
        tiempo_actual = time.time()
        if juego and juego.juego_pausado:
            return None
            
        if self.ultimo_ataque == 0:  # Primera vez
            self.ultimo_ataque = tiempo_actual
            return None
            
        if tiempo_actual - self.ultimo_ataque >= self.velocidad_ataque:
            # Verificar si puede atacar (solo para cuerpo a cuerpo)
            if juego and self.rango_ataque <= 1.0:
                if not self.puede_atacar(juego):
                    return None
            
            nueva_bala = Bala(self.y_fila, self.x_columna, direccion, self.rango_ataque)
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
    def __init__(self, y_fila, x_columna, direccion='arriba', rango=1.0):
        self.y_fila = float(y_fila)
        self.x_columna = x_columna
        self.direccion = direccion
        self.velocidad_bala = 0.30 
        self.color = COLOR_BALA
        self.bala_activa = True
        self.rango_maximo = rango  # Rango máximo de la bala
        self.distancia_recorrida = 0.0

    def desplazarse(self):
        if self.direccion == 'arriba':
            self.y_fila -= self.velocidad_bala
        else:  
            self.y_fila += self.velocidad_bala

        self.distancia_recorrida += self.velocidad_bala
        
        # Desactivar si supera el rango máximo o sale de los límites
        if (self.distancia_recorrida >= self.rango_maximo or 
            self.y_fila < 0 or self.y_fila >= FILAS):
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
        self.rango_ataque = 10.0  # Rooks tienen ataque a distancia

    def disparar(self, juego=None):
        return super().disparar(direccion='abajo', juego=juego)
    
    def disparar_manual(self):
        if not self.personaje_vivo:
            return

        direccion_bala = "abajo"

        nueva_bala = Bala(
            y_fila=self.y_fila,
            x_columna=self.x_columna,
            direccion=direccion_bala,
            rango=self.rango_ataque
        )
        self.balas.append(nueva_bala)


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
        self.velocidad_movimiento = velocidad_movimiento
        self.tipo_avatar = tipo_avatar  
        self.valor_monedas = valor_monedas  
        self.ultimo_movimiento = time.time()  # Inicializar con tiempo actual
        self.y_fila_objetivo = float(y_fila)
        self.en_movimiento = False
        
        self._configurar_tipo_ataque()


    def _configurar_tipo_ataque(self):
        """Configura el rango de ataque según el tipo de avatar"""
        if self.tipo_avatar in ["Leñador", "Caníbal"]:
            self.rango_ataque = 1.0  # Ataque cuerpo a cuerpo
        else:
            self.rango_ataque = 10.0  # Ataque a distancia (Flechero, Escudero)

    def puede_moverse(self, juego):
        """Verifica si el avatar puede moverse (no tiene rook al frente)"""
        return not self.tiene_rook_al_frente(juego)

    def mover(self, juego):
        """Intenta mover el avatar, considerando si hay rook al frente"""
        if juego and juego.juego_pausado:
            return False
            
        tiempo_actual = time.time()
        
        if self.ultimo_movimiento == 0:  # Primera vez
            self.ultimo_movimiento = tiempo_actual
            return False
        
        # Si no está en movimiento y ha pasado el tiempo suficiente, intentar mover
        if not self.en_movimiento and tiempo_actual - self.ultimo_movimiento >= self.velocidad_movimiento:
            
            # Verificar si puede moverse (no hay rook al frente)
            if not self.puede_moverse(juego):
                self.en_movimiento = False
                return False
                
            # Mover una casilla hacia arriba
            self.y_fila_objetivo = self.y_fila - 1.0
            self.ultimo_movimiento = tiempo_actual
            self.en_movimiento = True
            
            if self.y_fila_objetivo < 0:
                return True
        
        # Suavizar movimiento si está en transición
        if self.en_movimiento:
            if abs(self.y_fila - self.y_fila_objetivo) > 0.05:
                diferencia = self.y_fila_objetivo - self.y_fila
                self.y_fila += diferencia * 0.2
            else:
                self.y_fila = self.y_fila_objetivo
                self.en_movimiento = False
        
        return False

    def disparar(self, juego):
        """Sobrescribir disparar para pasar el juego como parámetro"""
        return super().disparar(direccion='arriba', juego=juego)

    def dibujar(self, pantalla, offset_x=0, offset_y=0):
        x = int(self.x_columna * TAMAÑO_CELDA) + offset_x
        y = int(self.y_fila * TAMAÑO_CELDA) + offset_y
        
        # Mantener el dibujo original con texturas (se maneja en Interfaz_Juego.py)
        pygame.draw.rect(pantalla, COLOR_AVATAR, 
                        (x + 10, y + 10, TAMAÑO_CELDA - 20, TAMAÑO_CELDA - 20), 
                        border_radius=10)
        
        barra_ancho = TAMAÑO_CELDA - 20
        barra_alto = 5
        porcentaje_vida = self.vida / self.vida_maxima
        
        pygame.draw.rect(pantalla, (100, 0, 0), (x + 10, y + 5, barra_ancho, barra_alto))
        pygame.draw.rect(pantalla, (0, 255, 0), (x + 10, y + 5, int(barra_ancho * porcentaje_vida), barra_alto))

class Moneda:
    def __init__(self, fila, columna, valor, tipo_imagen):
        self.fila = fila
        self.columna = columna
        self.valor = valor
        self.tipo_imagen = tipo_imagen  # "25", "25y50", "100"
        self.activa = True
        
    def recoger(self):
        if self.activa:
            self.activa = False
            return self.valor
        return 0
    
    def dibujar(self, pantalla, offset_x=0, offset_y=0):
        if not self.activa:
            return
            
        x = int(self.columna * TAMAÑO_CELDA) + offset_x
        y = int(self.fila * TAMAÑO_CELDA) + offset_y
        
        # El dibujo se manejará en Interfaz_Juego.py con las imágenes reales
        # Aquí solo un placeholder
        pygame.draw.circle(pantalla, (255, 215, 0), 
                         (x + TAMAÑO_CELDA // 2, y + TAMAÑO_CELDA // 2), 15)