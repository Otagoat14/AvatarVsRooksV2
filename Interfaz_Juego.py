import pygame
import time
import socket
from sys import exit
from Logica_juego import Juego, FILAS, COLUMNAS, VACIO, OCUPADA
from Personajes import TAMAÑO_CELDA
from Salon_fama import SalonFama, IntegradorJuego, InterfazSalonFama
from Animaciones.animacion_game_over import VentanaGameOver
from Animaciones.animacion_salon_fama import VentanaSalonFama
from Animaciones.animacion_win import VentanaWin
import sys
from Animaciones.animacion_final_juego import VentanaFinalJuego
from perfiles import obtener_musica_usuario
from Clases_auxiliares.integracion_spotify import reproducir_uri


PICO_IP = "192.168.151.216"   # <-- pon aquí la IP que imprime la Pico
PICO_PORT_MOTOR = 6000        # puerto para los motores

# Constantes visuales
ANCHO = COLUMNAS * TAMAÑO_CELDA
ALTO = FILAS * TAMAÑO_CELDA

# Colores
COLOR_FONDO = (18, 18, 18)
CELDA_VACIA = "Gray"
CELDA_OCUPADA = "Blue"
LINEA = (60, 60, 60)
COLOR_ROOK = (100, 200, 255)
COLOR_AVATAR = (255, 100, 100)
COLOR_BALA = (255, 255, 100)


# En Interfaz_Juego.py, modifica la clase Interfaz:

class Interfaz:
    def __init__(self, dificultad="facil", puntaje_acumulado=0, usuario = None):  
        pygame.init()

        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
        except Exception as e:
            print("Audio deshabilitado (no se pudo iniciar mixer):", e)

        info = pygame.display.Info()
        self.ANCHO_PANTALLA = info.current_w
        self.ALTO_PANTALLA = info.current_h
        
        self.pantalla = pygame.display.set_mode((self.ANCHO_PANTALLA, self.ALTO_PANTALLA), pygame.FULLSCREEN)
        pygame.display.set_caption("Avatar vs Rooks")
        self.reloj = pygame.time.Clock()
        self.fuente_texto = pygame.font.Font("Fuentes/super_sliced.otf", 20)
        
        # Sistema de niveles progresivos
        self.dificultad_actual = dificultad
        self.niveles = ["facil", "medio", "dificil"]
        self.nivel_actual_index = self.niveles.index(dificultad)

        # PUNTAJE ACUMULADO
        self.puntaje_acumulado = puntaje_acumulado

        # Cargar imágenes de monedas
        self.cargar_imagenes_monedas()
        self.verificar_archivos_imagenes()

        # Usuario actual (preferir el que viene desde la dificultad/login)
        self.usuario_actual = usuario
        if not self.usuario_actual:
            try:
                from Clases_auxiliares.credenciales import cargar_credenciales
                u, _ = cargar_credenciales()
                self.usuario_actual = u or "Jugador"
            except Exception:
                self.usuario_actual = "Jugador"


        # CARGAR PERSONALIZACIÓN DEL USUARIO
        self.cargar_personalizacion()
        self.pantalla.fill(COLOR_FONDO)
        pygame.display.flip()

        # Crear el juego pasando usuario y puntaje acumulado
        self.juego = Juego(dificultad=self.dificultad_actual, 
                          usuario=self.usuario_actual, 
                          puntaje_acumulado=self.puntaje_acumulado)
        

                # ===============================
        # CONTROL PICO (SOCKET UDP)
        # ===============================
        self.sock_control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_control.bind(("0.0.0.0", 5006))   # Debe coincidir con PC_PORT de la Pico
        self.sock_control.setblocking(False)

        self.sock_motor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Para saber cómo están los botones "en reposo" (0 ó 1)
        self.control_base = None    # dict con valores de reposo
        self.control_prev = None    # dict con último estado
        self.ultima_dir = None
        self.ultimo_mov_dir = 0

        # Cursor del joystick en la matriz (fila, columna)
        # Empiezo en la esquina inferior izquierda (ajusta a tu gusto)
        self.cursor_fila = 0
        self.cursor_col = COLUMNAS - 1


        # Al abrir la pantalla de juego, sonar su canción
        self.reproducir_cancion_usuario()
        
        self.campo_matriz = pygame.Surface((ANCHO, ALTO))
        self.campo_tienda = pygame.Surface((ANCHO, ALTO * 2))
        
        
        # Sistema de Salón de la Fama
        self.salon_fama = SalonFama(max_registros=10)
        self.interfaz_salon = InterfazSalonFama(
            self.pantalla,
            pygame.font.Font("Fuentes/super_sliced.otf", 40), 
            self.fuente_texto,
            self.salon_fama
        )
        self.mostrar_salon = False
        self.puntaje_registrado = False
        self.info_resultado = None

        # IMPORTANTE: Cargar usuario actual desde el login !!!!!!!!
        # Reemplaza "Jugador" con el nombre real del usuario logueado
        self.item_seleccionado = None
        
        # Cargar imágenes
        self.cargar_imagenes()
        self.cargar_imagenes_avatares()
        # fondo de la matriz
        self.fondo_matriz = pygame.image.load("Imagenes/fondo.png").convert_alpha()
        self.fondo_matriz = pygame.transform.scale(self.fondo_matriz, (ANCHO, ALTO))

        # Estado de la ronda
        self.ronda_iniciada = False
        self.boton_iniciar_ronda = None
        self._crear_boton_iniciar()
        
        # Estado de pausa
        self.juego_pausado = False
        self.boton_pausa = None
        self.boton_reanudar = None
        self._crear_botones_pausa()
    
    def cargar_imagenes_monedas(self):
        """Carga las imágenes de las monedas"""
        def cargar_imagen(ruta, tamaño):
            try:
                imagen = pygame.image.load(ruta)
                imagen = imagen.convert_alpha()
                return pygame.transform.scale(imagen, (tamaño, tamaño))
            except Exception as e:
                print(f"No se pudo cargar la imagen: {ruta} - Error: {e}")
                # Crear una imagen de fallback
                fallback = pygame.Surface((tamaño, tamaño), pygame.SRCALPHA)
                pygame.draw.circle(fallback, (255, 215, 0), (tamaño//2, tamaño//2), tamaño//2)
                return fallback
        
        tamaño_moneda = TAMAÑO_CELDA - 20
        self.imagenes_monedas = {
            "25": cargar_imagen("Imagenes/25.png", tamaño_moneda),
            "25y50": cargar_imagen("Imagenes/25y50.png", tamaño_moneda),
            "100": cargar_imagen("Imagenes/100.png", tamaño_moneda)
        }
        
        # Verificar que todas las imágenes se cargaron
        for tipo, img in self.imagenes_monedas.items():
            if img:
                print(f"Imagen de moneda {tipo} cargada correctamente")
            else:
                print(f"Error: No se pudo cargar la imagen para moneda {tipo}")
    
    def dibujar_monedas(self):
        """Dibuja las monedas en el tablero"""
        matriz_x = (self.ANCHO_PANTALLA - ANCHO) // 2
        matriz_y = (self.ALTO_PANTALLA - ALTO) // 2
        
        for moneda in self.juego.monedas_en_tablero:
            if moneda.activa:
                x = int(moneda.columna * TAMAÑO_CELDA) + matriz_x
                y = int(moneda.fila * TAMAÑO_CELDA) + matriz_y
                
                # Obtener la imagen correspondiente al tipo de moneda
                imagen = self.imagenes_monedas.get(moneda.tipo_imagen)
                if imagen:
                    # Centrar la imagen en la celda
                    pos_x = x + (TAMAÑO_CELDA - imagen.get_width()) // 2
                    pos_y = y + (TAMAÑO_CELDA - imagen.get_height()) // 2
                    self.pantalla.blit(imagen, (pos_x, pos_y))
                else:
                    # Fallback: dibujar círculo con el valor
                    color = {
                        "25": (255, 215, 0),      # Oro
                        "25y50": (192, 192, 192), # Plata  
                        "100": (205, 127, 50)     # Bronce
                    }.get(moneda.tipo_imagen, (255, 215, 0))
                    
                    pygame.draw.circle(self.pantalla, color, 
                                    (x + TAMAÑO_CELDA // 2, y + TAMAÑO_CELDA // 2), 15)
                    
                    # Mostrar el valor como texto
                    fuente_pequena = pygame.font.Font("Fuentes/super_sliced.otf", 12)
                    texto = fuente_pequena.render(str(moneda.valor), True, (0, 0, 0))
                    texto_rect = texto.get_rect(center=(x + TAMAÑO_CELDA // 2, y + TAMAÑO_CELDA // 2))
                    self.pantalla.blit(texto, texto_rect)
                    
    def _crear_boton_iniciar(self):
        """Crea el botón para iniciar la ronda"""
        ancho_boton = 200
        alto_boton = 60
        x = 50  # Posición en la esquina superior izquierda
        y = 300  # Debajo del puntaje
        
        self.boton_iniciar_ronda = {
            "rect": pygame.Rect(x, y, ancho_boton, alto_boton),
            "texto": "INICIAR RONDA",
            "hover": False,
            "activo": True
        }

    def dibujar_boton_iniciar(self):
        """Dibuja el botón de iniciar ronda"""
        if not self.ronda_iniciada and self.boton_iniciar_ronda["activo"]:
            boton = self.boton_iniciar_ronda
            rect = boton["rect"]
            
            # Color según estado
            if boton["hover"]:
                color = (80, 160, 80)  # Verde más claro al hover
            else:
                color = (60, 140, 60)  # Verde normal
            
            # Dibujar botón
            pygame.draw.rect(self.pantalla, color, rect, border_radius=8)
            pygame.draw.rect(self.pantalla, (200, 200, 200), rect, width=2, border_radius=8)
            
            # Dibujar texto
            try:
                fuente_boton = pygame.font.Font("Fuentes/super_sliced.otf", 20)
            except:
                fuente_boton = pygame.font.SysFont("segoeui", 20, bold=True)
            
            texto_surface = fuente_boton.render(boton["texto"], True, (255, 255, 255))
            texto_rect = texto_surface.get_rect(center=rect.center)
            self.pantalla.blit(texto_surface, texto_rect)

    def verificar_click_boton_iniciar(self, mouse_pos):
        """Verifica si se hizo click en el botón de iniciar ronda"""
        if (not self.ronda_iniciada and 
            self.boton_iniciar_ronda["activo"] and 
            self.boton_iniciar_ronda["rect"].collidepoint(mouse_pos)):
            
            self.ronda_iniciada = True
            self.boton_iniciar_ronda["activo"] = False  # Desactivar después de iniciar
            self.juego.iniciar_ronda()  # Método que agregaremos en Logica_juego.py
            return True
        return False

    def actualizar_estado_boton(self, mouse_pos):
        """Actualiza el estado hover del botón"""
        if self.boton_iniciar_ronda["activo"]:
            self.boton_iniciar_ronda["hover"] = self.boton_iniciar_ronda["rect"].collidepoint(mouse_pos)

    def _crear_botones_pausa(self):
        """Crea los botones de pausa y reanudar"""
        ancho_boton = 180
        alto_boton = 50
        x = 50  # Posición en la esquina superior izquierda
        y_pausa = 380  # Debajo del botón iniciar
        y_reanudar = 440  # Debajo del botón pausa
        
        self.boton_pausa = {
            "rect": pygame.Rect(x, y_pausa, ancho_boton, alto_boton),
            "texto": "⏸️ PAUSAR",
            "hover": False,
            "activo": True,
            "visible": True
        }
        
        self.boton_reanudar = {
            "rect": pygame.Rect(x, y_reanudar, ancho_boton, alto_boton),
            "texto": "▶️ REANUDAR",
            "hover": False,
            "activo": True,
            "visible": False  # Inicialmente oculto
        }

    def dibujar_botones_pausa(self):
        """Dibuja los botones de pausa y reanudar según el estado del juego"""
        # Botón de pausa (solo visible cuando el juego está activo y no pausado)
        if (self.ronda_iniciada and not self.juego_pausado and 
            self.boton_pausa["activo"] and self.boton_pausa["visible"]):
            
            boton = self.boton_pausa
            rect = boton["rect"]
            
            # Color según estado
            if boton["hover"]:
                color = (180, 120, 80)  # Naranja más claro al hover
            else:
                color = (160, 100, 60)  # Naranja normal
            
            # Dibujar botón
            pygame.draw.rect(self.pantalla, color, rect, border_radius=8)
            pygame.draw.rect(self.pantalla, (200, 200, 200), rect, width=2, border_radius=8)
            
            # Dibujar texto
            try:
                fuente_boton = pygame.font.Font("Fuentes/super_sliced.otf", 18)
            except:
                fuente_boton = pygame.font.SysFont("segoeui", 18, bold=True)
            
            texto_surface = fuente_boton.render(boton["texto"], True, (255, 255, 255))
            texto_rect = texto_surface.get_rect(center=rect.center)
            self.pantalla.blit(texto_surface, texto_rect)
        
        # Botón de reanudar (solo visible cuando el juego está pausado)
        if (self.juego_pausado and self.boton_reanudar["activo"] and 
            self.boton_reanudar["visible"]):
            
            boton = self.boton_reanudar
            rect = boton["rect"]
            
            # Color según estado
            if boton["hover"]:
                color = (80, 160, 80)  # Verde más claro al hover
            else:
                color = (60, 140, 60)  # Verde normal
            
            # Dibujar botón
            pygame.draw.rect(self.pantalla, color, rect, border_radius=8)
            pygame.draw.rect(self.pantalla, (200, 200, 200), rect, width=2, border_radius=8)
            
            # Dibujar texto
            try:
                fuente_boton = pygame.font.Font("Fuentes/super_sliced.otf", 18)
            except:
                fuente_boton = pygame.font.SysFont("segoeui", 18, bold=True)
            
            texto_surface = fuente_boton.render(boton["texto"], True, (255, 255, 255))
            texto_rect = texto_surface.get_rect(center=rect.center)
            self.pantalla.blit(texto_surface, texto_rect)

    def verificar_click_botones_pausa(self, mouse_pos):
        """Verifica si se hizo click en los botones de pausa/reanudar"""
        # Botón de pausa
        if (self.ronda_iniciada and not self.juego_pausado and 
            self.boton_pausa["activo"] and self.boton_pausa["visible"] and
            self.boton_pausa["rect"].collidepoint(mouse_pos)):
            
            self.pausar_juego()
            return True
        
        # Botón de reanudar
        if (self.juego_pausado and self.boton_reanudar["activo"] and 
            self.boton_reanudar["visible"] and
            self.boton_reanudar["rect"].collidepoint(mouse_pos)):
            
            self.reanudar_juego()
            return True
        
        return False

    def pausar_juego(self):
        """Pausa el juego"""
        self.juego_pausado = True
        self.boton_pausa["visible"] = False
        self.boton_reanudar["visible"] = True
        self.juego.pausar()  # Método que agregaremos en Logica_juego.py
        print("Juego pausado")

    def reanudar_juego(self):
        """Reanuda el juego"""
        self.juego_pausado = False
        self.boton_pausa["visible"] = True
        self.boton_reanudar["visible"] = False
        self.juego.reanudar()  # Método que agregaremos en Logica_juego.py
        print("Juego reanudado")

    def actualizar_estado_botones_pausa(self, mouse_pos):
        """Actualiza el estado hover de los botones de pausa/reanudar"""
        # Botón de pausa
        if self.boton_pausa["activo"] and self.boton_pausa["visible"]:
            self.boton_pausa["hover"] = self.boton_pausa["rect"].collidepoint(mouse_pos)
        
        # Botón de reanudar
        if self.boton_reanudar["activo"] and self.boton_reanudar["visible"]:
            self.boton_reanudar["hover"] = self.boton_reanudar["rect"].collidepoint(mouse_pos)
    
    def mostrar_mensaje_pausa(self):
        """Muestra mensaje indicando que el juego está pausado"""
        fuente_grande = pygame.font.Font("Fuentes/super_sliced.otf", 48)
        fuente_mediana = pygame.font.Font("Fuentes/super_sliced.otf", 24)
        
        # Fondo semitransparente
        overlay = pygame.Surface((self.ANCHO_PANTALLA, self.ALTO_PANTALLA))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))
        
        # Texto principal
        texto_pausa = fuente_grande.render("JUEGO EN PAUSA", True, (255, 255, 100))
        texto_rect = texto_pausa.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 - 50))
        self.pantalla.blit(texto_pausa, texto_rect)
        
        # Instrucciones
        instrucciones = fuente_mediana.render("Presiona P o el botón REANUDAR para continuar", True, (255, 255, 255))
        inst_rect = instrucciones.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 + 20))
        self.pantalla.blit(instrucciones, inst_rect)
    
    def reproducir_cancion_usuario(self):
        """
        Reproduce la canción que el usuario tiene guardada en su perfil (si hay).
        """
        try:
            uri = obtener_musica_usuario(self.usuario_actual)
            if uri:
                reproducir_uri(uri)
        except Exception as e:
            print("No se pudo reproducir la canción del usuario:", e)


    def avanzar_nivel(self):
        """Avanza al siguiente nivel si es posible"""
        if self.nivel_actual_index < len(self.niveles) - 1:
            self.nivel_actual_index += 1
            self.dificultad_actual = self.niveles[self.nivel_actual_index]
            
            # CALCULAR PUNTAJE ACUMULADO antes de avanzar
            puntaje_nivel_actual = self.juego.obtener_puntaje_actual()
            self.puntaje_acumulado += puntaje_nivel_actual
            
            return True
        return False  # No hay más niveles

    def reiniciar_nivel_actual(self):
        """Reinicia el nivel actual"""
        # Mantener el puntaje acumulado al reiniciar
        self.juego = Juego(dificultad=self.dificultad_actual, 
                        usuario=self.usuario_actual, 
                        puntaje_acumulado=self.puntaje_acumulado)
        self.juego.iniciar_juego(preparacion=True)
        self.puntaje_registrado = False
        self.info_resultado = None
        # También reiniciar el estado del botón
        self.ronda_iniciada = False
        self.juego_pausado = False
        self.boton_iniciar_ronda["activo"] = True
        self.boton_pausa["visible"] = True
        self.boton_reanudar["visible"] = False

        # 🔹 RESET ESTADO DEL CONTROL / JOYSTICK
        self.control_base = None
        self.control_prev = None
        self.ultima_dir = None
        self.ultimo_mov_dir = 0

        # Opcional: devolver el cursor a la posición inicial
        self.cursor_fila = FILAS - 1
        self.cursor_col = 0


    def cargar_personalizacion(self):
        try:
            from perfiles import obtener_colores
            colores = obtener_colores(self.usuario_actual)
            if colores:
                self.aplicar_colores_personalizados(colores)
                return
            self.aplicar_colores_por_defecto()
        except Exception:
            self.aplicar_colores_por_defecto()


    def aplicar_colores_personalizados(self, colores):
        global COLOR_FONDO, CELDA_VACIA, CELDA_OCUPADA, LINEA, COLOR_ROOK, COLOR_AVATAR, COLOR_BALA
        
        try:
            # Esperamos que 'colores' tenga claves como "fondo","ventana","btn_primario","btn_secundario","texto"
            def to_rgb(c):
                try:
                    return tuple(c["rgb"])
                except Exception:
                    return None
                
            if "fondo" in colores:
                v = to_rgb(colores["fondo"])
                if v: COLOR_FONDO = v
            if "ventana" in colores:
                v = to_rgb(colores["ventana"])
                if v:
                    # usar para celdas vacías / fondo de tarjetas
                    CELDA_VACIA = v
                    LINEA = tuple(max(0, int(c * 0.9)) for c in v)  # linea un poco más oscura
            if "btn_primario" in colores:
                v = to_rgb(colores["btn_primario"])
                if v:
                    COLOR_ROOK = v
                    CELDA_OCUPADA = tuple(max(0, int(c * 0.85)) for c in v)
            if "btn_secundario" in colores:
                v = to_rgb(colores["btn_secundario"])
                if v:
                    COLOR_AVATAR = v
            if "texto" in colores:
                v = to_rgb(colores["texto"])
                if v:
                    COLOR_BALA = v

        except Exception as e:
            self.aplicar_colores_por_defecto()

    def aplicar_colores_por_defecto(self):
        global COLOR_FONDO, CELDA_VACIA, CELDA_OCUPADA, LINEA, COLOR_ROOK, COLOR_AVATAR, COLOR_BALA
        
        COLOR_FONDO = (18, 18, 18)
        CELDA_VACIA = "Gray"
        CELDA_OCUPADA = "Blue"
        LINEA = (60, 60, 60)
        COLOR_ROOK = (100, 200, 255)
        COLOR_AVATAR = (255, 100, 100)
        COLOR_BALA = (255, 255, 100)


    def cargar_imagenes(self):
        def cargar_imagen(ruta, tamaño):
            try:
                imagen = pygame.image.load(ruta)
                imagen = imagen.convert_alpha()
                return pygame.transform.scale(imagen, (tamaño, tamaño))
            except:
                return None

        self.imagenes_rooks = []
        rooks_info = self.juego.obtener_rooks_info()
        for i, rook_info in enumerate(rooks_info):
            self.imagenes_rooks.append({
                "imagen": cargar_imagen(f"Imagenes/rook{i+1}.png", TAMAÑO_CELDA - 4),
                "imagen_preview": cargar_imagen(f"Imagenes/rook{i+1}.png", 40)
            })



    def cargar_imagenes_avatares(self):
        def cargar_imagen(ruta, tamaño):
            try:
                imagen = pygame.image.load(ruta)
                imagen = imagen.convert_alpha()
                return pygame.transform.scale(imagen, (tamaño, tamaño))
            except:
                print(f"No se pudo cargar la imagen: {ruta}")
                return None

        nombres_avatares = ["arquero", "canibal", "guerrero", "leñador"]

        self.imagenes_avatares = []

        for nombre in nombres_avatares:
            frames = []
            for i in range(1, 5): 
                ruta = f"Imagenes/{nombre}{i}.png"
                frames.append(cargar_imagen(ruta, TAMAÑO_CELDA - 4))
            self.imagenes_avatares.append({
                "nombre": nombre.capitalize(),
                "frames": frames
            })



    def dibujar_matriz(self):
        self.campo_matriz.blit(self.fondo_matriz, (0, 0))
        
        for f in range(FILAS):
            for c in range(COLUMNAS):
                x = c * TAMAÑO_CELDA
                y = f * TAMAÑO_CELDA
                
                valor_celda = self.juego.matriz[f][c]
                if valor_celda == OCUPADA:
                    pygame.draw.rect(self.campo_matriz, CELDA_OCUPADA, (x, y, TAMAÑO_CELDA, TAMAÑO_CELDA))

        for c in range(COLUMNAS + 1):
            x = c * TAMAÑO_CELDA
            pygame.draw.line(self.campo_matriz, LINEA, (x, 0), (x, ALTO), 1)

        for f in range(FILAS + 1):
            y = f * TAMAÑO_CELDA
            pygame.draw.line(self.campo_matriz, LINEA, (0, y), (ANCHO, y), 1)

                # === DIBUJAR CURSOR DEL JOYSTICK ===
        if 0 <= self.cursor_fila < FILAS and 0 <= self.cursor_col < COLUMNAS:
            x_cursor = self.cursor_col * TAMAÑO_CELDA
            y_cursor = self.cursor_fila * TAMAÑO_CELDA
            # Rectángulo amarillo para marcar la celda seleccionada
            pygame.draw.rect(
                self.campo_matriz,
                (255, 255, 0),
                (x_cursor + 2, y_cursor + 2, TAMAÑO_CELDA - 4, TAMAÑO_CELDA - 4),
                width=3
            )


    def _leer_estado_control(self):
        ultimo_estado = None

        while True:
            try:
                data, addr = self.sock_control.recvfrom(1024)
            except BlockingIOError:
                # No hay más paquetes pendientes
                break

            try:
                texto = data.decode().strip()
                # Ej: "JOY:ARRIBA,C:1,B1:0,B2:0,B3:0,B4:0,BS:0,BP:0"
                partes = texto.split(",")
                estado = {}
                for p in partes:
                    if ":" in p:
                        k, v = p.split(":", 1)
                        estado[k] = v
                # Nos aseguramos de que tenga al menos JOY
                if "JOY" in estado:
                    ultimo_estado = estado
            except Exception as e:
                print("Error al parsear control:", e)
                continue

        return ultimo_estado

        

    def _mover_cursor(self, df, dc):
        """Mueve el cursor en la matriz respetando los límites."""
        nueva_f = self.cursor_fila + df
        nueva_c = self.cursor_col + dc

        if 0 <= nueva_f < FILAS:
            self.cursor_fila = nueva_f
        if 0 <= nueva_c < COLUMNAS:
            self.cursor_col = nueva_c

    def _procesar_direccion(self, dir_joy, dt):
        """
        Aplica la dirección del joystick al cursor.
        Corrige el mapeo raro del hardware y limita la velocidad de movimiento.
        """
        # Corregir mapeo físico -> lógico
        if dir_joy == "IZQUIERDA":
            dir_logica = "ARRIBA"     # Físico arriba
        elif dir_joy == "DERECHA":
            dir_logica = "ABAJO"      # Físico abajo
        elif dir_joy == "ARRIBA":
            dir_logica = "DERECHA"    # Físico derecha
        elif dir_joy == "ABAJO":
            dir_logica = "IZQUIERDA"  # Físico izquierda
        else:
            dir_logica = "CENTRO"

        # Si está en el centro no movemos nada
        if dir_logica == "CENTRO":
            self.ultima_dir = None
            return

        # Para no moverse demasiado rápido: solo cada 0.15s si mantiene la dirección
        ahora = time.time()
        if self.ultima_dir == dir_logica and (ahora - self.ultimo_mov_dir) < 0.15:
            return

        self.ultima_dir = dir_logica
        self.ultimo_mov_dir = ahora

        if dir_logica == "ARRIBA":
            self._mover_cursor(-1, 0)
        elif dir_logica == "ABAJO":
            self._mover_cursor(+1, 0)
        elif dir_logica == "IZQUIERDA":
            self._mover_cursor(0, -1)
        elif dir_logica == "DERECHA":
            self._mover_cursor(0, +1)

    def _procesar_botones(self, estado):

        # Inicializar estados base y prev la primera vez
        if self.control_base is None:
            self.control_base = estado.copy()
            self.control_prev = estado.copy()
            return

        # Para cada botón, vemos si cambió respecto a control_prev
        def cambio_boton(clave):
            return estado.get(clave) != self.control_prev.get(clave)

        # Helper: botón "presionado" = distinto a estado de reposo
        def esta_presionado(clave):
            return estado.get(clave) != self.control_base.get(clave)

        # === Botones de rooks (1-4) ===
        # B1 – arena, B2 – agua, B3 – piedra, B4 – fuego
        if cambio_boton("B1") and esta_presionado("B1"):
            self._colocar_rook_desde_control(tipo_index=0)  # arena
        if cambio_boton("B2") and esta_presionado("B2"):
            self._colocar_rook_desde_control(tipo_index=1)  # agua
        if cambio_boton("B3") and esta_presionado("B3"):
            self._colocar_rook_desde_control(tipo_index=2)  # piedra
        if cambio_boton("B4") and esta_presionado("B4"):
            self._colocar_rook_desde_control(tipo_index=3)  # fuego

        # === Click del joystick: disparo manual de todas las rooks ===
        if cambio_boton("C") and esta_presionado("C"):
            # Un disparo manual por click
            self.juego.disparar_rooks_manual()

        # === SELECT: recoger monedas en todo el tablero ===
        if cambio_boton("BS") and esta_presionado("BS"):
            self.juego.recoger_monedas()

        # === PAUSA: pausar / reanudar ===
        if cambio_boton("BP") and esta_presionado("BP"):
            if not self.juego_pausado:
                self.pausar_juego()
            else:
                self.reanudar_juego()

        # Actualizar estado anterior
        self.control_prev = estado.copy()

    def _colocar_rook_desde_control(self, tipo_index):
        # Solo bloqueo si el juego está en pausa o ya terminó
        if self.juego_pausado or self.juego.game_over or self.juego.victoria:
            return

        fila = self.cursor_fila
        col = self.cursor_col

        # tipo_index: 0=arena, 1=agua, 2=piedra, 3=fuego
        success, message = self.juego.colocar_rook(fila, col, tipo_index)

        if success:
            info = self.juego.obtener_rooks_info()[tipo_index]
            print(f"Rook colocada ({info['nombre']}) en ({fila}, {col})")
        else:
            print("No se pudo colocar la rook:", message)






    def dibujar_rook(self, rook):
        x = int(rook.x_columna * TAMAÑO_CELDA)
        y = int(rook.y_fila * TAMAÑO_CELDA)
        
        rook_index = rook.tipo_rook - 2 
        if rook_index < len(self.imagenes_rooks) and self.imagenes_rooks[rook_index]["imagen"]:
            self.campo_matriz.blit(self.imagenes_rooks[rook_index]["imagen"], (x + 2, y + 2))
        else:
            pygame.draw.circle(self.campo_matriz, COLOR_ROOK, 
                             (x + TAMAÑO_CELDA // 2, y + TAMAÑO_CELDA // 2), 20)
        
        # Barra de vida
        self.dibujar_barra_vida(x, y, rook.vida, rook.vida_maxima)

    def dibujar_avatar(self, avatar):
        x = int(avatar.x_columna * TAMAÑO_CELDA)
        y = int(avatar.y_fila * TAMAÑO_CELDA)


        avatar_index = getattr(avatar, "tipo_avatar", 0)


        if isinstance(avatar_index, str):
            import unicodedata
            def _norm(s):
                s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
                return s.lower()
            key = _norm(avatar_index)
            name_to_idx = {
                "flechero": 0, "arquero": 0,
                "canibal": 1, "caníbal": 1,
                "guerrero": 2, "escudero": 2,
                "lenador": 3, "leñador": 3,
            }
            avatar_index = name_to_idx.get(key, 0)

        if not (0 <= int(avatar_index) < len(self.imagenes_avatares)):
            avatar_index = 0

        frames = self.imagenes_avatares[int(avatar_index)]["frames"]

        # Animación
        if getattr(avatar, "moviendose", False): 
            frame_index = getattr(avatar, "frame_actual", 0)
        else:
            frame_index = 0  

        frame = frames[frame_index] if frames[frame_index] else None


        if frame:
            self.campo_matriz.blit(frame, (x + 2, y + 2))
        else:
            pygame.draw.rect(
                self.campo_matriz, COLOR_AVATAR,
                (x + 10, y + 10, TAMAÑO_CELDA - 20, TAMAÑO_CELDA - 20),
                border_radius=10
            )

        self.dibujar_barra_vida(x + 10, y + 5, avatar.vida, avatar.vida_maxima, TAMAÑO_CELDA - 20)



    def dibujar_balas(self, balas):
        for bala in balas:
            if bala.bala_activa:
                x = int(bala.x_columna * TAMAÑO_CELDA + TAMAÑO_CELDA // 2)
                y = int(bala.y_fila * TAMAÑO_CELDA + TAMAÑO_CELDA // 2)
                pygame.draw.circle(self.campo_matriz, COLOR_BALA, (x, y), 6)

    def dibujar_barra_vida(self, x, y, vida_actual, vida_maxima, ancho=TAMAÑO_CELDA - 10):
        barra_alto = 5
        porcentaje_vida = vida_actual / vida_maxima
        
        pygame.draw.rect(self.campo_matriz, (100, 0, 0), (x, y, ancho, barra_alto))
        pygame.draw.rect(self.campo_matriz, (0, 255, 0), (x, y, int(ancho * porcentaje_vida), barra_alto))


    def dibujar_rooks_recursivo(self, indice=0):
        if indice >= len(self.juego.rooks_activos):
            return
        
        rook = self.juego.rooks_activos[indice]
        if rook.personaje_vivo:
            self.dibujar_rook(rook)
            self.dibujar_balas(rook.balas)
        
        self.dibujar_rooks_recursivo(indice + 1)

    # En la función dibujar_avatares_recursivo, asegúrate de pasar el juego:
    def dibujar_avatares_recursivo(self, indice=0):
        if indice >= len(self.juego.avatares_activos):
            return
        
        avatar = self.juego.avatares_activos[indice]
        if avatar.personaje_vivo:
            self.dibujar_avatar(avatar)
            # El avatar ya disparó en la lógica del juego, solo dibujamos las balas
            self.dibujar_balas(avatar.balas)
        
        self.dibujar_avatares_recursivo(indice + 1)

    def dibujar_tienda(self):
        self.campo_tienda.fill("Red")
        
        # Título
        titulo_tienda = self.fuente_texto.render("TIENDA - ROOKS", False, "White")
        self.campo_tienda.blit(titulo_tienda, (ANCHO // 2 - titulo_tienda.get_width() // 2, 20))

        # Panel de monedas
        fondo_monedas = pygame.Rect(20, 50, ANCHO - 40, 60)
        pygame.draw.rect(self.campo_tienda, (40, 40, 40), fondo_monedas)
        pygame.draw.rect(self.campo_tienda, (200, 200, 200), fondo_monedas, 3)
        
        texto_monedas = self.fuente_texto.render(f"MONEDAS: ${self.juego.monedas_jugador}", False, (255, 215, 0))
        self.campo_tienda.blit(texto_monedas, (ANCHO // 2 - texto_monedas.get_width() // 2, 65))

        # Instrucción
        texto_leyenda = self.fuente_texto.render("COLOCA TUS ROOKS", False, "White")
        self.campo_tienda.blit(texto_leyenda, (ANCHO // 2 - texto_leyenda.get_width() // 2, 140))

        # Items de la tienda
        espacio_x = 20
        inicio_y = 180
        ancho_cuadro_item = ANCHO - (espacio_x * 2)
        alto_cuadro_item = 110
        espaciado = 25

        for i in range(4):
            y = inicio_y + i * (alto_cuadro_item + espaciado)
            rect = pygame.Rect(espacio_x, y, ancho_cuadro_item, alto_cuadro_item)
            
            rook_info = self.juego.obtener_rooks_info()[i]
            puede_comprar = self.juego.monedas_jugador >= rook_info["precio"]
            
            # Fondo del item
            if self.item_seleccionado == i:
                pygame.draw.rect(self.campo_tienda, (80, 80, 150), rect)
                pygame.draw.rect(self.campo_tienda, (255, 255, 0), rect, 4)
            else:
                color_fondo = (25, 25, 25) if not puede_comprar else (50, 50, 50)
                color_borde = (80, 80, 80) if not puede_comprar else (180, 180, 180)
                pygame.draw.rect(self.campo_tienda, color_fondo, rect)
                pygame.draw.rect(self.campo_tienda, color_borde, rect, 3)

            # Imagen preview
            tamaño_preview = 70
            preview_x = espacio_x + 15
            preview_y = y + (alto_cuadro_item // 2) - (tamaño_preview // 2)
            
            if i < len(self.imagenes_rooks) and self.imagenes_rooks[i]["imagen_preview"]:
                imagen = self.imagenes_rooks[i]["imagen_preview"]
                if not puede_comprar:
                    imagen = imagen.copy()
                    imagen.set_alpha(100)
                self.campo_tienda.blit(imagen, (preview_x, preview_y))

            # Precio (derecha)
            color_precio = (255, 215, 0) if puede_comprar else (150, 150, 150)
            texto_precio = self.fuente_texto.render(f"${rook_info['precio']}", False, color_precio)
            px = rect.right - texto_precio.get_width() - 15
            py = y + 20
            self.campo_tienda.blit(texto_precio, (px, py))

            # Nombre del rook
            color_nombre = "White" if puede_comprar else (120, 120, 120)
            texto_nombre = self.fuente_texto.render(rook_info['nombre'], False, color_nombre)
            nombre_x = preview_x + tamaño_preview + 20
            nombre_y = y + 20
            self.campo_tienda.blit(texto_nombre, (nombre_x, nombre_y))

            # ESTADÍSTICAS (
            if puede_comprar:
                fuente_pequeña = pygame.font.Font("Fuentes/super_sliced.otf", 16)
                
                # Vida
                texto_vida = fuente_pequeña.render(f"Vida: {rook_info['vida']}", False, (100, 255, 100))
                vida_x = nombre_x
                vida_y = nombre_y + texto_nombre.get_height() + 8
                self.campo_tienda.blit(texto_vida, (vida_x, vida_y))
                
                # Daño
                texto_daño = fuente_pequeña.render(f"Daño: {rook_info['daño']}", False, (255, 100, 100))
                daño_x = vida_x + texto_vida.get_width() + 15
                daño_y = vida_y
                self.campo_tienda.blit(texto_daño, (daño_x, daño_y))
    
    #Funcion para que se vea el puntaje
    def dibujar_puntaje(self):
        puntaje_actual = self.juego.obtener_puntaje_actual()
        puntaje_total = self.puntaje_acumulado + puntaje_actual
        
        # Puntaje del nivel actual (debe empezar en 0)
        texto_puntaje_nivel = f"Puntaje Nivel: {puntaje_actual}"
        superficie_puntaje_nivel = self.fuente_texto.render(texto_puntaje_nivel, False, (255, 215, 0))
        self.pantalla.blit(superficie_puntaje_nivel, (50, 180))
        
        # Puntaje acumulado total (solo si hay niveles anteriores)
        if self.puntaje_acumulado > 0:
            texto_puntaje_total = f"Puntaje Total: {puntaje_total}"
            superficie_puntaje_total = self.fuente_texto.render(texto_puntaje_total, False, (200, 200, 255))
            self.pantalla.blit(superficie_puntaje_total, (50, 210))
        
        # Estadísticas adicionales
        fuente_pequena = pygame.font.Font("Fuentes/super_sliced.otf", 16)
        
        stats_text = f"Avatars eliminados: {self.juego.total_avatars_matados}"
        stats_surface = fuente_pequena.render(stats_text, False, (200, 200, 200))
        self.pantalla.blit(stats_surface, (50, 240))

    def dibujar_ui(self):
        # Título
        titulo_juego = self.fuente_texto.render("Avatar vs rooks", False, "White")
        self.pantalla.blit(titulo_juego, (50, 50))
        
        # Información de dificultad y nivel
        nivel_texto = self.fuente_texto.render(f"Nivel: {self.dificultad_actual.upper()}", False, "White")
        self.pantalla.blit(nivel_texto, (50, 85))
        
        # Contador de tiempo
        self.dibujar_contador_tiempo()
        self.dibujar_puntaje()
        
        # Notificaciones
        if self.juego.ultima_notificacion and time.time() - self.juego.tiempo_notificacion < 2.0:
            self.mostrar_notificacion(self.juego.ultima_notificacion)

    def dibujar_contador_tiempo(self):
        if not self.ronda_iniciada:
            # Mostrar "PREPARACIÓN" en lugar del tiempo
            texto_tiempo = "PREPARACIÓN"
            color = (255, 255, 100)  # Amarillo para preparación
        elif self.juego_pausado:
            # Mostrar "PAUSADO" cuando el juego está pausado
            texto_tiempo = "PAUSADO"
            color = (255, 150, 50)  # Naranja para pausa
        else:
            mins, secs = divmod(self.juego.tiempo_restante, 60)
            texto_tiempo = f"Tiempo: {mins:02d}:{secs:02d}"
            
            # Cambiar color cuando queda poco tiempo (código existente)
            if self.juego.tiempo_restante > 30:
                color = (255, 255, 255)
            elif self.juego.tiempo_restante > 10:
                color = (255, 200, 0)
            else:
                color = (255, 50, 50)
        
        superficie_tiempo = self.fuente_texto.render(texto_tiempo, False, color)
        self.pantalla.blit(superficie_tiempo, (50, 120))
        
        # Mostrar mensaje especial cuando el tiempo está por acabarse (solo si la ronda inició y no está pausada)
        if (self.ronda_iniciada and not self.juego_pausado and 
            self.juego.tiempo_restante <= 10 and self.juego.tiempo_restante > 0):
            fuente_alerta = pygame.font.Font("Fuentes/super_sliced.otf", 16)
            texto_alerta = f"¡{self.juego.tiempo_restante} segundos restantes!"
            alerta_surface = fuente_alerta.render(texto_alerta, False, (255, 100, 100))
            self.pantalla.blit(alerta_surface, (50, 150))

    def mostrar_notificacion(self, texto):
        fuente_notificacion = pygame.font.Font("Fuentes/super_sliced.otf", 24)
        texto_surface = fuente_notificacion.render(texto, False, (255, 215, 0))
        
        x = (self.ANCHO_PANTALLA - texto_surface.get_width()) // 2
        y = 200
        
        fondo_rect = pygame.Rect(x - 10, y - 5, texto_surface.get_width() + 20, texto_surface.get_height() + 10)
        pygame.draw.rect(self.pantalla, (0, 0, 0, 180), fondo_rect)
        pygame.draw.rect(self.pantalla, (255, 215, 0), fondo_rect, 2)
        
        self.pantalla.blit(texto_surface, (x, y))

    def dibujar_mensaje_fin_juego(self):

        #SALON DE LA FAMA
        # Registrar puntaje una sola vez cuando termina el juego
        if not self.puntaje_registrado:
            self.info_resultado = IntegradorJuego.registrar_partida(
                self.salon_fama,
                self.usuario_actual,
                self.juego
            )
            self.puntaje_registrado = True
            

        overlay = pygame.Surface((self.pantalla.get_width(), self.pantalla.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))
        
        fuente_grande = pygame.font.Font("Fuentes/super_sliced.otf", 60)
        fuente_mediana = pygame.font.Font("Fuentes/super_sliced.otf", 30)
        fuente_pequeña = pygame.font.Font("Fuentes/super_sliced.otf", 25)

        puntaje_final = self.juego.obtener_puntaje_actual()
        detalles = self.juego.obtener_detalles_puntaje()
        
        if self.juego.game_over:
            texto = fuente_grande.render("GAME OVER", False, (255, 50, 50))
            texto2 = fuente_pequeña.render("Los avatares llegaron a la base", False, (255, 255, 255))
        else:  # victoria
            texto = fuente_grande.render("¡VICTORIA!", False, (50, 255, 50))
            texto2 = fuente_pequeña.render("Sobreviviste el tiempo con tus rooks", False, (255, 255, 255))

        texto_puntaje = fuente_mediana.render(f"Puntaje Final: {puntaje_final}", False, (255, 215, 0))
        texto_avatars = fuente_pequeña.render(
            f"Avatars eliminados: {detalles['avatars_matados']}", 
            False, (200, 200, 200))
        
        texto_rect = texto.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 - 50))
        texto2_rect = texto2.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 + 20))
        puntaje_rect = texto_puntaje.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 + 60))
        avatars_rect = texto_avatars.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 + 90))
        
        texto3 = fuente_pequeña.render("Presiona R para reiniciar", False, (200, 200, 200))
        texto3_rect = texto3.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 + 140))

        # Mostrar información del salón de la fama
        if self.info_resultado:
            texto_salon = fuente_pequeña.render(
                "Presiona F para ver el Salón de la Fama", 
                False, (200, 200, 200)
            )
            salon_rect = texto_salon.get_rect(
                center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 + 170)
            )
            self.pantalla.blit(texto_salon, salon_rect)
            
            # Si es récord o top 10, mostrar mensaje especial
            if self.info_resultado['es_record']:
                texto_especial = fuente_mediana.render(
                    "¡NUEVO RÉCORD!", False, (255, 215, 0)
                )
            elif self.info_resultado['es_top']:
                texto_especial = fuente_mediana.render(
                    f"¡TOP 10 - Posición #{self.info_resultado['posicion']}!", 
                    False, (100, 200, 255)
                )
            else:
                texto_especial = fuente_pequeña.render(
                    f"Posición: #{self.info_resultado['posicion']}", 
                    False, (150, 150, 150)
                )
            
            especial_rect = texto_especial.get_rect(
                center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 + 200)
            )
            self.pantalla.blit(texto_especial, especial_rect)
            
        self.pantalla.blit(texto, texto_rect)
        self.pantalla.blit(texto2, texto2_rect)
        self.pantalla.blit(texto_puntaje, puntaje_rect)
        self.pantalla.blit(texto_avatars, avatars_rect)
        self.pantalla.blit(texto3, texto3_rect)

    def obtener_item_clickeado(self, mouse_x, mouse_y):
        tienda_x = self.ANCHO_PANTALLA - ANCHO
        local_x = mouse_x - tienda_x
        local_y = mouse_y
        
        if local_x < 0 or local_x > ANCHO or local_y < 0 or local_y > ALTO * 2:
            return None
        
        espacio_x = 20
        inicio_y = 180
        ancho_cuadro_item = ANCHO - (espacio_x * 2)
        alto_cuadro_item = 110
        espaciado = 25
        
        for i in range(4):
            y = inicio_y + i * (alto_cuadro_item + espaciado)
            if (espacio_x <= local_x <= espacio_x + ancho_cuadro_item and 
                y <= local_y <= y + alto_cuadro_item):
                return i
        
        return None
    
    def mostrar_animacion_fin(self, tipo="derrota"):
        self.juego.juego_iniciado = False 
        
        if tipo == "victoria":
            # Calcular puntaje total acumulado
            puntaje_final_total = self.puntaje_acumulado + self.juego.obtener_puntaje_actual()
            
            # Verificar si es el nivel difícil (último nivel)
            if self.dificultad_actual == "dificil":
                # REGISTRAR EN SALÓN DE LA FAMA con puntaje acumulado
                if not self.puntaje_registrado:
                    # Crear un juego temporal con el puntaje acumulado total para el registro
                    juego_temp = Juego(dificultad="dificil", usuario=self.usuario_actual)
                    juego_temp.total_avatars_matados = self.juego.total_avatars_matados
                    juego_temp.puntos_acumulados_avatars = self.juego.puntos_acumulados_avatars
                    
                    self.info_resultado = IntegradorJuego.registrar_partida(
                        self.salon_fama,
                        self.usuario_actual,
                        juego_temp,
                        puntaje_manual=puntaje_final_total  # Pasar puntaje acumulado
                    )
                    self.puntaje_registrado = True
                
                # Verificar si llegó al salón de la fama
                if self.puntaje_registrado and self.info_resultado and self.info_resultado['es_top']:
                    # Usar animación de salón de la fama
                    ventana_fama = VentanaSalonFama(self.pantalla, paleta=self._paleta_usuario(), username=self.usuario_actual)
                    accion = ventana_fama.run()  # ✅ ASIGNAR accion AQUÍ
                else:
                    # Usar animación final del juego sin salón de la fama
                    accion = VentanaFinalJuego(self.pantalla).run()  # ✅ ASIGNAR accion AQUÍ
                
                # ✅ AHORA accion SIEMPRE ESTÁ DEFINIDA
                if accion == "reiniciar":
                    # Reiniciar desde el nivel difícil con puntaje en 0
                    self.puntaje_acumulado = 0
                    self.reiniciar_nivel_actual()
                    return "reiniciar"
                elif accion == "menu":
                    return "menu"
                else:  # salir
                    return "salir"
            else:
                # Nivel no difícil - progresión normal
                accion = self.mostrar_ventana_victoria()
                
                if accion == "continuar":
                    if self.avanzar_nivel():
                        self.reiniciar_nivel_actual()
                        return "continuar"
                    else:
                        return "victoria_final"
                elif accion == "menu":
                    return "menu"
                else:  # salir
                    return "salir"
            
        else:
            # PARA DERROTA
            accion = VentanaGameOver(self.pantalla, paleta=self._paleta_usuario(), username=self.usuario_actual).run()

            if accion == "reiniciar":
                # Reiniciar nivel actual manteniendo el puntaje acumulado
                self.reiniciar_nivel_actual()
                return "reiniciar"

            elif accion == "menu":
                return "menu"

            elif accion == "salir":
                pygame.quit()
                sys.exit()

    def _paleta_usuario(self):
        try:
            from perfiles import obtener_paleta_personalizada
            return obtener_paleta_personalizada(self.usuario_actual)
        except Exception:
            return None

    def mostrar_ventana_victoria(self):
        ventana_win = VentanaWin(self.pantalla, paleta=self._paleta_usuario(), username=self.usuario_actual)
        return ventana_win.run_modificado()


    def ejecutar(self):
        # Posiciones
        matriz_x = (self.ANCHO_PANTALLA - ANCHO) // 2
        matriz_y = (self.ALTO_PANTALLA - ALTO) // 2
        tienda_x = self.ANCHO_PANTALLA - ANCHO

        # Iniciar juego en modo preparación
        self.juego.iniciar_juego(preparacion=True)

        while True:
            dt = self.reloj.tick(60) / 1000.0  # Delta time en segundos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.MOUSEMOTION:
                    # Actualizar estado hover de todos los botones
                    self.actualizar_estado_boton(event.pos)
                    self.actualizar_estado_botones_pausa(event.pos)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and (self.juego.game_over or self.juego.victoria):
                        self.reiniciar_nivel_actual()
                        # Reiniciar también el estado de los botones
                        self.ronda_iniciada = False
                        self.juego_pausado = False
                        self.boton_iniciar_ronda["activo"] = True
                        self.boton_pausa["visible"] = True
                        self.boton_reanudar["visible"] = False

                    elif event.key == pygame.K_f:
                        self.mostrar_salon = not self.mostrar_salon
                    elif event.key == pygame.K_ESCAPE:
                        if self.mostrar_salon:
                            self.mostrar_salon = False
                        else:
                            pygame.quit()
                            exit()
                    # Atajo de teclado para iniciar ronda (Barra Espaciadora)
                    elif event.key == pygame.K_SPACE and not self.ronda_iniciada and self.boton_iniciar_ronda["activo"]:
                        self.ronda_iniciada = True
                        self.boton_iniciar_ronda["activo"] = False
                        self.juego.iniciar_ronda()
                    
                    # Atajo de teclado para pausar/reanudar (Tecla P)
                    elif event.key == pygame.K_p and self.ronda_iniciada:
                        if not self.juego_pausado:
                            self.pausar_juego()
                        else:
                            self.reanudar_juego()
                    
                    # ATAJO SECRETO PARA RECOGER MONEDAS (Barra Espaciadora cuando el juego está activo)
                    elif event.key == pygame.K_SPACE and self.ronda_iniciada and not self.juego_pausado:
                        monedas_recogidas = self.juego.recoger_monedas()
                        if monedas_recogidas > 0:
                            print(f"Monedas recogidas secretamente: {monedas_recogidas}")

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Verificar click en botón iniciar ronda
                    if self.verificar_click_boton_iniciar((mouse_x, mouse_y)):
                        continue

                    # Verificar click en botones de pausa/reanudar
                    if self.verificar_click_botones_pausa((mouse_x, mouse_y)):
                        continue

                    # Seleccionar item de tienda
                    item_clickeado = self.obtener_item_clickeado(mouse_x, mouse_y)
                    if item_clickeado is not None:
                        rook_info = self.juego.obtener_rooks_info()[item_clickeado]
                        if self.juego.monedas_jugador >= rook_info["precio"]:
                            self.item_seleccionado = item_clickeado

                    # Colocar o remover rook en matriz
                    local_x = mouse_x - matriz_x
                    local_y = mouse_y - matriz_y
                    
                    if 0 <= local_x < ANCHO and 0 <= local_y < ALTO:
                        fila = local_y // TAMAÑO_CELDA
                        columna = local_x // TAMAÑO_CELDA

                        if event.button == 1 and self.item_seleccionado is not None:
                            success, message = self.juego.colocar_rook(fila, columna, self.item_seleccionado)
                            if success:
                                print(f"Rook colocado en ({fila}, {columna})")
                            else:
                                print(message)
                        
                        elif event.button == 3:
                            if self.juego.remover_rook(fila, columna):
                                print(f"Rook removido de ({fila}, {columna})")

            estado = self._leer_estado_control()
            if estado:
                # Procesar dirección del joystick
                self._procesar_direccion(estado.get("JOY", "CENTRO"), dt)

                # Procesar botones (rooks, disparo, select, pausa)
                self._procesar_botones(estado)


            # Actualizar lógica del juego SOLO si la ronda está iniciada y NO está pausada
            if self.ronda_iniciada and not self.juego_pausado:
                self.juego.actualizar()

                if getattr(self.juego, "rook_herida", False):
                    try:
                        self.sock_motor.sendto(b"HIT", (PICO_IP, PICO_PORT_MOTOR))
                        # opcional: print para depurar
                        print("Enviando HIT a Pico para vibrar motor")
                    except Exception as e:
                        print("Error enviando HIT a Pico:", e)
                    # resetear el flag
                    self.juego.rook_herida = False

            # Dibujar (siempre se dibuja, incluso cuando está pausado)
            self.pantalla.fill(COLOR_FONDO)

            # Dibujar matriz
            self.dibujar_matriz()
            
            # Dibujar personajes recursivamente
            self.dibujar_rooks_recursivo()
            self.dibujar_avatares_recursivo()
            
            # DIBUJAR LA MATRIZ PRIMERO
            self.pantalla.blit(self.campo_matriz, (matriz_x, matriz_y))
            
            # LUEGO DIBUJAR LAS MONEDAS DIRECTAMENTE EN LA PANTALLA PRINCIPAL
            self.dibujar_monedas()

            # Dibujar tienda
            self.dibujar_tienda()
            self.pantalla.blit(self.campo_tienda, (tienda_x, 0))

            # Dibujar UI
            self.dibujar_ui()
            
            # Dibujar botón de iniciar ronda
            self.dibujar_boton_iniciar()
            
            # Dibujar botones de pausa/reanudar
            self.dibujar_botones_pausa()

            # Mostrar mensaje de preparación si la ronda no ha iniciado
            if not self.ronda_iniciada:
                self.mostrar_mensaje_preparacion()

            # Mostrar mensaje de pausa si el juego está pausado
            if self.juego_pausado:
                self.mostrar_mensaje_pausa()

            # Verificar fin del juego y mostrar animaciones
            if self.juego.victoria:
                accion = self.mostrar_animacion_fin("victoria")
                
                if accion == "continuar":
                    continue  # Continuar con el siguiente nivel
                elif accion == "menu":
                    from dificultad import main as main_dificultad
                    pygame.display.quit()
                    try:
                        from Clases_auxiliares.credenciales import cargar_preferencias
                        prefs = cargar_preferencias()
                        lang_actual = prefs.get("idioma", "es")
                    except:
                        lang_actual = "es"
                    
                    main_dificultad(self.usuario_actual, lang_actual)
                    return

                elif accion == "victoria_final":
                    # Mostrar victoria final con la ventana win normal
                    ventana_final = VentanaWin(self.pantalla, paleta=self._paleta_usuario(), username=self.usuario_actual)
                    ventana_final.run()
                    pygame.quit()
                    return

            elif self.juego.game_over:
                accion = self.mostrar_animacion_fin("derrota")
                
                if accion == "reiniciar":
                    self.reiniciar_nivel_actual()
                    # Reiniciar estado del botón al reiniciar nivel
                    self.ronda_iniciada = False
                    self.juego_pausado = False
                    self.boton_iniciar_ronda["activo"] = True
                    self.boton_pausa["visible"] = True
                    self.boton_reanudar["visible"] = False
                elif accion == "menu":
                    from dificultad import main as main_dificultad
                    pygame.display.quit()
                    try:
                        from Clases_auxiliares.credenciales import cargar_preferencias
                        prefs = cargar_preferencias()
                        lang_actual = prefs.get("idioma", "es")
                    except:
                        lang_actual = "es"
                    
                    main_dificultad(self.usuario_actual, lang_actual)
                    return
                elif accion == "salir":
                    pygame.quit()
                    exit()

            if self.mostrar_salon:
                self.interfaz_salon.dibujar_salon_completo(
                    self.ANCHO_PANTALLA,
                    self.ALTO_PANTALLA,
                    self.usuario_actual
                )

            pygame.display.update()
            self.reloj.tick(60)  # Limitar a 60 FPS
    
    def mostrar_mensaje_preparacion(self):
        """Muestra mensaje indicando que está en fase de preparación"""
        fuente_grande = pygame.font.Font("Fuentes/super_sliced.otf", 36)
        fuente_mediana = pygame.font.Font("Fuentes/super_sliced.otf", 24)
        
        # Fondo semitransparente
        overlay = pygame.Surface((self.ANCHO_PANTALLA, 200))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, self.ALTO_PANTALLA // 2 - 100))
        
        # Texto principal
        texto_preparacion = fuente_grande.render("FASE DE PREPARACIÓN", True, (255, 255, 100))
        texto_rect = texto_preparacion.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 - 30))
        self.pantalla.blit(texto_preparacion, texto_rect)
        
        # Instrucciones
        instrucciones = fuente_mediana.render("Coloca tus Rooks y presiona INICIAR RONDA cuando estés listo", True, (255, 255, 255))
        inst_rect = instrucciones.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 + 20))
        self.pantalla.blit(instrucciones, inst_rect)
        
        # Atajo de teclado
        atajo = fuente_mediana.render("(También puedes usar la Barra Espaciadora)", True, (200, 200, 200))
        atajo_rect = atajo.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 + 60))
        self.pantalla.blit(atajo, atajo_rect)
    
    def verificar_archivos_imagenes(self):
        """Verifica que los archivos de imágenes existan"""
        import os
        archivos_necesarios = ["25.png", "25y50.png", "100.png"]
        for archivo in archivos_necesarios:
            ruta = os.path.join("Imagenes", archivo)
            if os.path.exists(ruta):
                print(f"✓ {ruta} existe")
            else:
                print(f"✗ {ruta} NO existe")

if __name__ == "__main__":
   
    interfaz = Interfaz()
    interfaz.ejecutar()