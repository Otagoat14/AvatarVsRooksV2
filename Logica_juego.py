import pygame 
import time
from sys import exit
from Funciones_auxiliares import (cargar_imagen_rook, 
                                verificar_click_boton,
                                obtener_item_clickeado,
                                iniciar_juego, 
                                agregar_monedas, 
                                rooks_info,
                                tiempo_restante,
                                juego_iniciado,
                                obtener_tiempo_nivel,
                                ANCHO,
                                ALTO,
                                FILAS,
                                COLUMNAS,
                                TAMAÑO_CELDA,
                                matriz,
                                VACIO,
                                CELDA_VACIA,
                                CELDA_OCUPADA,
                                OCUPADA,
                                LINEA,
                                

                                )


monedas_jugador = 350  
nivel_dificultad = "Facil"
juego_iniciado = False
tiempo_restante = 0
tiempo_inicio = 0


pygame.init()
#lo de la pantalla se puede cambiar para que quede de forma estética
pantalla = pygame.display.set_mode(((ANCHO * 2) + 400, ALTO * 2))
pygame.display.set_caption("Avatar vs Rooks")
reloj = pygame.time.Clock()
fuente_texto = pygame.font.Font("Fuentes/super_sliced.otf", 20)

campo_matriz = pygame.Surface((ANCHO, ALTO))
campo_matriz.fill("Red")

campo_tienda = pygame.Surface((ANCHO, ALTO * 2))
campo_tienda.fill("Red")

ANCHO_MAPA_CENTRADO = (pantalla.get_width() - ANCHO) // 2
ALTO_MAPA_CENTRADO = (pantalla.get_height() - ALTO) // 2

titulo_juego = fuente_texto.render("Avatar vs rooks", False, "White")
item_seleccionado = None

#Esto se cambiaria con la logica de los avatars
for rook in rooks_info:
    rook["imagen"] = cargar_imagen_rook(rook["ruta_imagen"], TAMAÑO_CELDA - 4)
    rook["imagen_preview"] = cargar_imagen_rook(rook["ruta_imagen"], 40)

#-------FUNCIONES PARA LA LOGICA---------
def gastar_monedas(cantidad):
    global monedas_jugador
    
    if monedas_jugador >= cantidad:
        monedas_jugador -= cantidad
        return True
    else:
        return False

def actualizar_contador():
    global tiempo_restante, juego_iniciado
    
    if juego_iniciado and tiempo_restante > 0:
        tiempo_actual = time.time()
        tiempo_transcurrido = int(tiempo_actual - tiempo_inicio)
        tiempo_calculado = obtener_tiempo_nivel(nivel_dificultad) - tiempo_transcurrido
        
        if tiempo_calculado != tiempo_restante:
            tiempo_restante = max(0, tiempo_calculado)

        if tiempo_restante == 0:
            print("Tiempo terminado")

    
    return tiempo_restante

#-----------------------------------------------------------------
#---------FUNCIONES DE DIBUJADO------------------------------------

def dibujar_matriz(pantalla):
    for f in range(FILAS):
        for c in range(COLUMNAS):
            posicion_x = c * TAMAÑO_CELDA
            posicion_y = f * TAMAÑO_CELDA

            valor_celda = matriz[f][c]
            
            # Primero dibujamos el fondo de la celda
            if valor_celda == VACIO:
                color = CELDA_VACIA
            elif valor_celda == OCUPADA:
                color = CELDA_OCUPADA
            else:
                # Para las celdas con rooks, usamos un color neutro de fondo
                color = CELDA_VACIA
            
            pygame.draw.rect(pantalla, color, (posicion_x, posicion_y, TAMAÑO_CELDA, TAMAÑO_CELDA))
            
            if valor_celda != VACIO and valor_celda != OCUPADA:
                # buscar qué rook es
                for rook in rooks_info:
                    if rook["tipo"] == valor_celda:
                        # si tiene imagen la dibuja
                        if rook["imagen"] is not None:
                            # centrar la imagen en la celda
                            img_x = posicion_x + 2  
                            img_y = posicion_y + 2
                            pantalla.blit(rook["imagen"], (img_x, img_y))
                        else:
                            # si no se cargó la imagen dibujar el color de respaldo
                            pygame.draw.rect(pantalla, rook["color"], 
                                           (posicion_x + 5, posicion_y + 5, 
                                            TAMAÑO_CELDA - 10, TAMAÑO_CELDA - 10))
                        break

    #Lineas verticales
    for c in range(COLUMNAS + 1):
        posicion_x = c * TAMAÑO_CELDA
        pygame.draw.line(campo_matriz, LINEA, (posicion_x, 0), (posicion_x, ALTO), 1)

    #Lineas horizontales
    for f in range(FILAS + 1):
        posicion_y = f * TAMAÑO_CELDA
        pygame.draw.line(campo_matriz, LINEA, (0, posicion_y), (ANCHO, posicion_y), 1)

# Función para dibujar el contador en pantalla
def dibujar_contador(pantalla, fuente, x, y):
    """Dibuja el contador en formato MM:SS"""
    mins, secs = divmod(tiempo_restante, 60)
    texto_tiempo = f"Tiempo: {mins:02d}:{secs:02d}"
    
    # Color según tiempo restante
    if tiempo_restante > 30:
        color = (255, 255, 255)  # Blanco
    elif tiempo_restante > 10:
        color = (255, 200, 0)    # Amarillo
    else:
        color = (255, 50, 50)    # Rojo
    
    superficie_tiempo = fuente.render(texto_tiempo, False, color)
    pantalla.blit(superficie_tiempo, (x, y))


def dibujar_boton_iniciar(pantalla, fuente, x, y, ancho, alto):
    boton_rect = pygame.Rect(x, y, ancho, alto)
    
    # Color del botón
    if not juego_iniciado:
        color_boton = (50, 200, 50)  
        texto = "INICIAR JUEGO"
    else:
        color_boton = (100, 100, 100)  
        texto = "EN JUEGO"
    
    # Dibujar el botón
    pygame.draw.rect(pantalla, color_boton, boton_rect)
    pygame.draw.rect(pantalla, (255, 255, 255), boton_rect, 3)
    
    # Dibujar el texto centrado
    superficie_texto = fuente.render(texto, False, (255, 255, 255))
    texto_x = x + (ancho - superficie_texto.get_width()) // 2
    texto_y = y + (alto - superficie_texto.get_height()) // 2
    pantalla.blit(superficie_texto, (texto_x, texto_y))
    
    return boton_rect

def dibujar_tienda():
    campo_tienda.fill("Red")

    espacio_x = 20
    inicio_y = 360
    ancho_cuadro_item = ANCHO - (espacio_x * 2)
    alto_cuadro_item = 128
    espaciado = 24

    fondo_monedas = pygame.Rect(20, 50, ANCHO - 40, 70)
    pygame.draw.rect(campo_tienda, (40, 40, 40), fondo_monedas)
    pygame.draw.rect(campo_tienda, (200, 200, 200), fondo_monedas, 3)
    
    # Texto de monedas
    texto_monedas = fuente_texto.render(f"Monedas: ${monedas_jugador}", False, (255, 215, 0))  
    campo_tienda.blit(texto_monedas, (50, 300))
    
    # Leyenda
    texto_leyenda = fuente_texto.render("Coloca tus rooks", False, "White")
    campo_tienda.blit(texto_leyenda, (50, 200))

    #Dibujar las 4 rooks de la tieda
    for i in range(4):
        y = inicio_y + i * (alto_cuadro_item + espaciado)
        rect = pygame.Rect(espacio_x, y, ancho_cuadro_item, alto_cuadro_item)
        
        #ver si puede comprar
        puede_comprar = monedas_jugador >= rooks_info[i]["precio"]
        
        if item_seleccionado == i:
            pygame.draw.rect(campo_tienda, (80, 80, 150), rect)  
            pygame.draw.rect(campo_tienda, (255, 255, 0), rect, 4)  
        else:
            # Si no puede comprar dibujar con color más oscuro, es solo estetico
            if not puede_comprar:
                pygame.draw.rect(campo_tienda, (20, 20, 20), rect)  
                pygame.draw.rect(campo_tienda, (100, 100, 100), rect, 2)  
            else:
                pygame.draw.rect(campo_tienda, (40, 40, 40), rect)
                pygame.draw.rect(campo_tienda, (200, 200, 200), rect, 2)

        tamaño_preview = 40
        preview_x = espacio_x + 10
        preview_y = y + (alto_cuadro_item // 2) - (tamaño_preview // 2)
        
        # Si hay imagen se dibuja si no se hace unos rectangulos de colores
        if rooks_info[i]["imagen_preview"] is not None:
            
            #Dibujar todo mas oscuro en caso de que no se pueda comprar
            if not puede_comprar:
                # Crear una copia de la imagen transparente
                imagen_oscura = rooks_info[i]["imagen_preview"].copy()
                imagen_oscura.set_alpha(100)  
                campo_tienda.blit(imagen_oscura, (preview_x, preview_y))
            else:
                campo_tienda.blit(rooks_info[i]["imagen_preview"], (preview_x, preview_y))
        else:
            # Si no hay imagen, dibujar el cuadrito de color como antes
            color_item = rooks_info[i]["color"] if puede_comprar else (50, 50, 50)
            pygame.draw.rect(campo_tienda, color_item, 
                            (preview_x, preview_y, tamaño_preview, tamaño_preview))
            pygame.draw.rect(campo_tienda, (200, 200, 200), 
                            (preview_x, preview_y, tamaño_preview, tamaño_preview), 2)

        # Precio (cambiar color si no puede comprar)
        color_precio = (255, 215, 0) if puede_comprar else (150, 150, 150)  
        texto_precio = fuente_texto.render(f"${rooks_info[i]['precio']}", False, color_precio)
        px = rect.right - texto_precio.get_width() - 8
        py = rect.top + 6
        campo_tienda.blit(texto_precio, (px, py))

        # Nombre del rook
        color_nombre = "White" if puede_comprar else (100, 100, 100)
        texto_nombre = fuente_texto.render(rooks_info[i]['nombre'], False, color_nombre)
        nombre_x = preview_x + tamaño_preview + 15
        nombre_y = y + (alto_cuadro_item // 2) - (texto_nombre.get_height() // 2)
        campo_tienda.blit(texto_nombre, (nombre_x, nombre_y))

#-------------------------------------
#---------CICLO PRINCIPLA-------------

def juego():
    global item_seleccionado
    global nivel_dificultad


    boton_x = 50
    boton_y = 150
    boton_ancho = 200
    boton_alto = 60

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Verificar clic en botón iniciar
                if event.button == 1:
                    boton_rect = pygame.Rect(boton_x, boton_y, boton_ancho, boton_alto)
                    if verificar_click_boton(boton_rect, mouse_x, mouse_y) and not juego_iniciado:
                        iniciar_juego(nivel_dificultad)
                
                # ========== CLICK EN LA TIENDA ==========
                item_clickeado = obtener_item_clickeado(mouse_x, mouse_y)
                if item_clickeado is not None:
                    # ========== NUEVO: VERIFICAR SI PUEDE COMPRAR ==========
                    precio = rooks_info[item_clickeado]["precio"]
                    if monedas_jugador >= precio:
                        item_seleccionado = item_clickeado
                        print(f"Item seleccionado: {rooks_info[item_clickeado]['nombre']}")
                    else:
                        print(f"¡No tienes suficientes monedas para seleccionar {rooks_info[item_clickeado]['nombre']}!")
                        print(f"Necesitas ${precio}, tienes ${monedas_jugador}")
                
               
                local_x_campo_matriz = mouse_x - 180
                local_y_campo_matriz = mouse_y - ALTO_MAPA_CENTRADO
                
                # Click dentro del rectángulo para la matriz
                if 0 <= local_x_campo_matriz < ANCHO and 0 <= local_y_campo_matriz < ALTO:
                    fila = local_y_campo_matriz // TAMAÑO_CELDA
                    columna = local_x_campo_matriz // TAMAÑO_CELDA

                    # Click izquierdo: colocar rook
                    if event.button == 1:
                        if item_seleccionado is not None:

                            precio = rooks_info[item_seleccionado]["precio"]
                            
                            # Intentar gastar las monedas
                            if gastar_monedas(precio):
                                # Si se pudo gastar, colocar el rook
                                matriz[fila][columna] = rooks_info[item_seleccionado]["tipo"]
                            
                        else:
                            # Si no hay nada seleccionado, ponemos OCUPADA sin costo
                            matriz[fila][columna] = OCUPADA
                    
                    # Click derecho: borrar
                    elif event.button == 3:
                        valor_celda = matriz[fila][columna]
                        
                        # Si hay un rook en esta celda, devolver sus monedas
                        if valor_celda != VACIO and valor_celda != OCUPADA:
                            for rook in rooks_info:
                                if rook["tipo"] == valor_celda:
                                    agregar_monedas(rook["precio"])
                                    print(f"Rook removido. Monedas devueltas: ${rook['precio']}")
                                    break
                        
                        matriz[fila][columna] = VACIO
            if juego_iniciado :
                actualizar_contador()

        pantalla.fill((18, 18, 18))

        dibujar_matriz(campo_matriz)
        pantalla.blit(campo_matriz, (180, ALTO_MAPA_CENTRADO))
        
        dibujar_tienda()
        pantalla.blit(campo_tienda, (((ANCHO * 2) + 400) - ANCHO, 0))

        pantalla.blit(titulo_juego, (0, 0))

        boton_rect = dibujar_boton_iniciar(pantalla, fuente_texto, boton_x, boton_y, boton_ancho, boton_alto)

        if juego_iniciado:
            dibujar_contador(pantalla, fuente_texto, boton_x, boton_y + 80)

        pygame.display.update()
        reloj.tick(60)


juego()