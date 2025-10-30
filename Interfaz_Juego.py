import pygame
import time
from sys import exit
from Logica_juego import Juego, FILAS, COLUMNAS, VACIO, OCUPADA
from Personajes import TAMAÑO_CELDA
from gameOverAnimado import VentanaGameOver
from salon_fama import VentanaSalonFama
from win import VentanaWin
import sys


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

class Interfaz:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.ANCHO_PANTALLA = info.current_w
        self.ALTO_PANTALLA = info.current_h
        
        self.pantalla = pygame.display.set_mode((self.ANCHO_PANTALLA, self.ALTO_PANTALLA), pygame.FULLSCREEN)
        pygame.display.set_caption("Avatar vs Rooks")
        self.reloj = pygame.time.Clock()
        self.fuente_texto = pygame.font.Font("Fuentes/super_sliced.otf", 20)
        
        self.campo_matriz = pygame.Surface((ANCHO, ALTO))
        self.campo_tienda = pygame.Surface((ANCHO, ALTO * 2))
        
        self.juego = Juego()
        self.item_seleccionado = None
        
        # Cargar imágenes
        self.cargar_imagenes()
        self.cargar_imagenes_avatares()
        # fondo de la matriz
        self.fondo_matriz = pygame.image.load("Imagenes/fondo.png").convert_alpha()
        self.fondo_matriz = pygame.transform.scale(self.fondo_matriz, (ANCHO, ALTO))


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

        # Diccionario con los nombres base de los avatares
        nombres_avatares = ["arquero", "canibal", "guerrero", "leñador"]

        self.imagenes_avatares = []

        for nombre in nombres_avatares:
            frames = []
            for i in range(1, 5):  # 4 frames por avatar
                ruta = f"Imagenes/{nombre}{i}.png"
                frames.append(cargar_imagen(ruta, TAMAÑO_CELDA - 4))
            self.imagenes_avatares.append({
                "nombre": nombre.capitalize(),
                "frames": frames
            })
            print("\n=== DEBUG: contenido de self.imagenes_avatares ===")
            for idx, data in enumerate(self.imagenes_avatares):
                print(idx, type(data), data)


    def dibujar_matriz(self):
        self.campo_matriz.blit(self.fondo_matriz, (0, 0))
        
        for f in range(FILAS):
            for c in range(COLUMNAS):
                x = c * TAMAÑO_CELDA
                y = f * TAMAÑO_CELDA
                
                valor_celda = self.juego.matriz[f][c]
                if valor_celda == OCUPADA:
                    pygame.draw.rect(self.campo_matriz, CELDA_OCUPADA, (x, y, TAMAÑO_CELDA, TAMAÑO_CELDA))


        # Líneas de la grid
        for c in range(COLUMNAS + 1):
            x = c * TAMAÑO_CELDA
            pygame.draw.line(self.campo_matriz, LINEA, (x, 0), (x, ALTO), 1)

        for f in range(FILAS + 1):
            y = f * TAMAÑO_CELDA
            pygame.draw.line(self.campo_matriz, LINEA, (0, y), (ANCHO, y), 1)

    def dibujar_rook(self, rook):
        x = int(rook.x_columna * TAMAÑO_CELDA)
        y = int(rook.y_fila * TAMAÑO_CELDA)
        
        rook_index = rook.tipo_rook - 2  # Convertir tipo a índice
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

        # --- Normalización robusta del tipo de avatar ----
        avatar_index = getattr(avatar, "tipo_avatar", 0)

        # Si viene como texto (e.g. "Flechero", "Caníbal", "Leñador"), mapearlo a índice 0-3
        if isinstance(avatar_index, str):
            # normalizar (minúsculas y sin tildes/ñ)
            import unicodedata
            def _norm(s):
                s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
                return s.lower()
            key = _norm(avatar_index)
            # cubrir nombres lógicos y nombres de sprites
            name_to_idx = {
                "flechero": 0, "arquero": 0,
                "canibal": 1, "caníbal": 1,
                "guerrero": 2, "escudero": 2,
                "lenador": 3, "leñador": 3,
            }
            avatar_index = name_to_idx.get(key, 0)

        # Asegurar rango válido por si llega un número fuera de 0-3
        if not (0 <= int(avatar_index) < len(self.imagenes_avatares)):
            avatar_index = 0
        # --------------------------------------------------

        frames = self.imagenes_avatares[int(avatar_index)]["frames"]

        # Animación
        if getattr(avatar, "moviendose", False):  # atributo booleano
            frame_index = getattr(avatar, "frame_actual", 0)
        else:
            frame_index = 0  # frame estático (primer frame del sprite)

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

    def dibujar_avatares_recursivo(self, indice=0):
        if indice >= len(self.juego.avatares_activos):
            return
        
        avatar = self.juego.avatares_activos[indice]
        if avatar.personaje_vivo:
            self.dibujar_avatar(avatar)
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

            # ESTADÍSTICAS (esto es lo que faltaba)
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
                

    def dibujar_ui(self):
        # Título
        titulo_juego = self.fuente_texto.render("Avatar vs rooks", False, "White")
        self.pantalla.blit(titulo_juego, (50, 50))
        
        # Contador de tiempo
        self.dibujar_contador_tiempo()
        
        # Notificaciones
        if self.juego.ultima_notificacion and time.time() - self.juego.tiempo_notificacion < 2.0:
            self.mostrar_notificacion(self.juego.ultima_notificacion)

    def dibujar_contador_tiempo(self):
        mins, secs = divmod(self.juego.tiempo_restante, 60)
        texto_tiempo = f"Tiempo: {mins:02d}:{secs:02d}"
        
        # Cambiar color cuando queda poco tiempo
        if self.juego.tiempo_restante > 30:
            color = (255, 255, 255)
        elif self.juego.tiempo_restante > 10:
            color = (255, 200, 0)  # Amarillo
        else:
            color = (255, 50, 50)  # Rojo
        
        superficie_tiempo = self.fuente_texto.render(texto_tiempo, False, color)
        self.pantalla.blit(superficie_tiempo, (50, 120))
        
        # Mostrar mensaje especial cuando el tiempo está por acabarse
        if self.juego.tiempo_restante <= 10 and self.juego.tiempo_restante > 0:
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
        overlay = pygame.Surface((self.pantalla.get_width(), self.pantalla.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        self.pantalla.blit(overlay, (0, 0))
        
        fuente_grande = pygame.font.Font("Fuentes/super_sliced.otf", 60)
        fuente_pequeña = pygame.font.Font("Fuentes/super_sliced.otf", 25)
        
        if self.juego.game_over:
            texto = fuente_grande.render("GAME OVER", False, (255, 50, 50))
            texto2 = fuente_pequeña.render("Los avatares llegaron a la base", False, (255, 255, 255))
        else:  # victoria
            texto = fuente_grande.render("¡VICTORIA!", False, (50, 255, 50))
            texto2 = fuente_pequeña.render("Sobreviviste el tiempo con tus rooks", False, (255, 255, 255))
        
        texto_rect = texto.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 - 50))
        texto2_rect = texto2.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 + 20))
        
        texto3 = fuente_pequeña.render("Presiona R para reiniciar", False, (200, 200, 200))
        texto3_rect = texto3.get_rect(center=(self.ANCHO_PANTALLA // 2, self.ALTO_PANTALLA // 2 + 80))
        
        self.pantalla.blit(texto, texto_rect)
        self.pantalla.blit(texto2, texto2_rect)
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
    
    # En el método mostrar_animacion_fin, cambiar las llamadas:
    def mostrar_animacion_fin(self, tipo="derrota"):
        """Muestra la animación de victoria o derrota y maneja la acción del usuario"""
        self.juego.juego_iniciado = False  # Pausar el juego
        
        if tipo == "victoria":
            print("🎉 Mostrando animación de victoria...")
            accion = VentanaSalonFama(self.pantalla).run()  # Pasar self.pantalla
        else:
            print("💀 Mostrando animación de game over...")
            accion = VentanaGameOver(self.pantalla).run()  # Pasar self.pantalla

        # Manejar la acción del usuario
        if accion == "reiniciar":
            print("🔁 Reiniciando juego...")
            self.juego.reiniciar_juego()
        elif accion == "menu":
            print("🏠 Volviendo al menú principal...")
            pygame.quit()
            sys.exit()
        elif accion == "salir":
            print("👋 Saliendo del juego...")
            pygame.quit()
            sys.exit()
        elif accion == "ver":
            print("📊 Mostrando estadísticas...")
            # Por ahora, también cerramos el juego
            pygame.quit()
            sys.exit()




    def ejecutar(self):
        # Posiciones
        matriz_x = (self.ANCHO_PANTALLA - ANCHO) // 2
        matriz_y = (self.ALTO_PANTALLA - ALTO) // 2
        tienda_x = self.ANCHO_PANTALLA - ANCHO

        # Iniciar juego automáticamente
        self.juego.iniciar_juego()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and (self.juego.game_over or self.juego.victoria):
                        self.juego.reiniciar_juego()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

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

            # Actualizar lógica del juego
            self.juego.actualizar()

            # Dibujar
            self.pantalla.fill(COLOR_FONDO)

            # Dibujar matriz
            self.dibujar_matriz()
            
            # Dibujar personajes recursivamente
            self.dibujar_rooks_recursivo()
            self.dibujar_avatares_recursivo()
            
            self.pantalla.blit(self.campo_matriz, (matriz_x, matriz_y))

            # Dibujar tienda
            self.dibujar_tienda()
            self.pantalla.blit(self.campo_tienda, (tienda_x, 0))

            # Dibujar UI
            self.dibujar_ui()

            # Verificar fin del juego y mostrar animaciones
            if self.juego.victoria:
                self.mostrar_animacion_fin("victoria")

            elif self.juego.game_over:
                self.mostrar_animacion_fin("derrota")

            pygame.display.update()
            self.reloj.tick(60)

if __name__ == "__main__":
    interfaz = Interfaz()
    interfaz.ejecutar()