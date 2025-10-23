import pygame
from sys import exit

#------CONSTANTES--------
FILAS = 9
COLUMNAS = 5
TAMAÑO_CELDA = 64

#Practicamente para sacar el tamaño del mapa en pixeles
ANCHO = COLUMNAS * TAMAÑO_CELDA
ALTO = FILAS * TAMAÑO_CELDA

#Colores para probar 
CELDA_OCUPADA = "Blue"
CELDA_VACIA = "Gray"
LINEA = (60, 60, 60)

#CELDAS OCUPADAS O VACIAS
VACIO = 0
OCUPADA = 1

# NUEVOS TIPOS DE ROOKS 
ROOK_TIPO_1 = 2
ROOK_TIPO_2 = 3
ROOK_TIPO_3 = 4
ROOK_TIPO_4 = 5

#Matriz con None para que podamos personalizarla
matriz = [[VACIO for c in range(COLUMNAS)] for f in range(FILAS)]
print(matriz)

#------------------------------

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

# Aquí cargamos las imágenes y las escalamos al tamaño de la celda
def cargar_imagen_rook(ruta, tamaño):
    try:
        imagen = pygame.image.load(ruta)
        # convert_alpha() optimiza la imagen y mantiene la transparencia
        imagen = imagen.convert_alpha()
        # Escalar al tamaño deseado
        imagen = pygame.transform.scale(imagen, (tamaño, tamaño))
        return imagen
    except:
        return None

#Esto se cambiaria con la logica de los avatars
rooks_info = [
    {
        "precio": 10, 
        "color": (100, 200, 255), 
        "tipo": ROOK_TIPO_1, 
        "nombre": "Rook Básico",
        "ruta_imagen": "Imagenes/rook1.jpg"  
    },
    {
        "precio": 20, 
        "color": (100, 255, 100), 
        "tipo": ROOK_TIPO_2, 
        "nombre": "Rook Medio",
        "ruta_imagen": "Imagenes/rook2.jpg"  
    },
    {
        "precio": 30, 
        "color": (255, 100, 100), 
        "tipo": ROOK_TIPO_3, 
        "nombre": "Rook Fuerte",
        "ruta_imagen": "Imagenes/rook3.jpg"  
    },
    {
        "precio": 40, 
        "color": (255, 255, 100), 
        "tipo": ROOK_TIPO_4, 
        "nombre": "Rook Épico",
        "ruta_imagen": "Imagenes/rook4.jpg"  
    }
]


for rook in rooks_info:
    rook["imagen"] = cargar_imagen_rook(rook["ruta_imagen"], TAMAÑO_CELDA - 4)
    rook["imagen_preview"] = cargar_imagen_rook(rook["ruta_imagen"], 40)

#-------FUNCIONES PARA LA LOGICA---------
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


def dibujar_tienda():
    campo_tienda.fill("Red")

    espacio_x = 20
    inicio_y = 360
    ancho_cuadro_item = ANCHO - (espacio_x * 2)
    alto_cuadro_item = 128
    espaciado = 24

    for i in range(4):
        y = inicio_y + i * (alto_cuadro_item + espaciado)
        rect = pygame.Rect(espacio_x, y, ancho_cuadro_item, alto_cuadro_item)
        
        if item_seleccionado == i:
            pygame.draw.rect(campo_tienda, (80, 80, 150), rect)  
            pygame.draw.rect(campo_tienda, (255, 255, 0), rect, 4)  
        else:
            pygame.draw.rect(campo_tienda, (40, 40, 40), rect)
            pygame.draw.rect(campo_tienda, (200, 200, 200), rect, 2)

        tamaño_preview = 40
        preview_x = espacio_x + 10
        preview_y = y + (alto_cuadro_item // 2) - (tamaño_preview // 2)
        
        # Si hay imagen preview, dibujarla
        if rooks_info[i]["imagen_preview"] is not None:
            campo_tienda.blit(rooks_info[i]["imagen_preview"], (preview_x, preview_y))
        else:
            # Si no hay imagen, dibujar el cuadrito de color como antes
            pygame.draw.rect(campo_tienda, rooks_info[i]["color"], 
                            (preview_x, preview_y, tamaño_preview, tamaño_preview))
            pygame.draw.rect(campo_tienda, (200, 200, 200), 
                            (preview_x, preview_y, tamaño_preview, tamaño_preview), 2)


        texto_precio = fuente_texto.render(f"${rooks_info[i]['precio']}", False, "White")
        px = rect.right - texto_precio.get_width() - 8
        py = rect.top + 6
        campo_tienda.blit(texto_precio, (px, py))

        texto_nombre = fuente_texto.render(rooks_info[i]['nombre'], False, "White")
        nombre_x = preview_x + tamaño_preview + 15
        nombre_y = y + (alto_cuadro_item // 2) - (texto_nombre.get_height() // 2)
        campo_tienda.blit(texto_nombre, (nombre_x, nombre_y))


def obtener_item_clickeado(mouse_x, mouse_y):
    # Primero convertimos las coordenadas del mouse a coordenadas locales de campo_tienda
    # campo_tienda está dibujado en la posición: (((ANCHO * 2) + 400) - ANCHO, 0)
    posicion_tienda_x = ((ANCHO * 2) + 400) - ANCHO
    posicion_tienda_y = 0
    
    # Coordenadas locales dentro de campo_tienda
    local_x = mouse_x - posicion_tienda_x
    local_y = mouse_y - posicion_tienda_y
    
    # Si el click no está dentro de campo_tienda, retornamos None
    if local_x < 0 or local_x > ANCHO or local_y < 0 or local_y > ALTO * 2:
        return None
    
    # Ahora verificamos en cuál de los 4 items clickeamos
    espacio_x = 20
    inicio_y = 360
    ancho_cuadro_item = ANCHO - (espacio_x * 2)
    alto_cuadro_item = 128
    espaciado = 24
    
    for i in range(4):
        y = inicio_y + i * (alto_cuadro_item + espaciado)
        
        # Verificamos si el click está dentro de este item
        if (espacio_x <= local_x <= espacio_x + ancho_cuadro_item and 
            y <= local_y <= y + alto_cuadro_item):
            return i  
    
    return None  


def juego():
    global item_seleccionado

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                #Click en la tienda
                item_clickeado = obtener_item_clickeado(mouse_x, mouse_y)
                if item_clickeado is not None:

                    item_seleccionado = item_clickeado
                    print(f"Item seleccionado: {rooks_info[item_clickeado]['nombre']}")
                
                #click en la matriz
                local_x_campo_matriz = mouse_x - 180
                local_y_campo_matriz = mouse_y - ALTO_MAPA_CENTRADO
                
                # Click dentro del rectángulo para la matriz
                if 0 <= local_x_campo_matriz < ANCHO and 0 <= local_y_campo_matriz < ALTO:
                    fila = local_y_campo_matriz // TAMAÑO_CELDA
                    columna = local_x_campo_matriz // TAMAÑO_CELDA

                   
                    if event.button == 1:
                    #Colocar rook
                        if item_seleccionado is not None:
                            matriz[fila][columna] = rooks_info[item_seleccionado]["tipo"]
                        else:
                            matriz[fila][columna] = OCUPADA
                    
                    #para borrar cojn click derecho
                    elif event.button == 3:
                        matriz[fila][columna] = VACIO

        pantalla.fill((18, 18, 18))

        dibujar_matriz(campo_matriz)
        pantalla.blit(campo_matriz, (180, ALTO_MAPA_CENTRADO))
        
        dibujar_tienda()
        pantalla.blit(campo_tienda, (((ANCHO * 2) + 400) - ANCHO, 0))

        pantalla.blit(titulo_juego, (0, 0))

        pygame.display.update()
        reloj.tick(60)


juego()