import pygame
from sys import exit

#------CONSTANTES--------
FILAS = 9
COLUMNAS = 5
TAMAÑO_CELDA = 64

#Practiacamente para sacar el tamanno del mapa en pixeles
ANCHO = COLUMNAS * TAMAÑO_CELDA
ALTO = FILAS * TAMAÑO_CELDA

#Colores para probar 
CELDA_OCUPADA = "Blue"
CELDA_VACIA = "Gray"
LINEA = (60, 60, 60)

#CELDAS OCUPADAS O VACIAS
VACIO = 0
OCUPADA = 1


#Matriz con None para que podamos personlizarla
matriz = [[VACIO for c in range(COLUMNAS)] for f in range(FILAS)]
print(matriz)

#------------------------------


pygame.init()
#lo de la pantalla se puede cambiar para que quede de forma estetica
pantalla = pygame.display.set_mode(((ANCHO * 2) + 400, ALTO * 2))
pygame.display.set_caption("Avatar vs Rooks")
reloj = pygame.time.Clock()
fuente_texto = pygame.font.Font("Fuentes/super_sliced.otf", 20)
#Agregar el logo del juego

campo_matriz = pygame.Surface((ANCHO, ALTO))
campo_matriz.fill("Red")


campo_tienda = pygame.Surface((ANCHO, ALTO * 2))
campo_tienda.fill("Red")



ANCHO_MAPA_CENTRADO = (pantalla.get_width() - ANCHO) // 2
ALTO_MAPA_CENTRADO = (pantalla.get_height() - ALTO) // 2

#para hacer que se vea mas estetico se puede hcaer con las imagenes y los surfaces

#asi se annade el texto y luego en el ciclo while true
titulo_juego = fuente_texto.render("Avatar vs rooks", False, "White")


#-------FUNCIONES PARA LA LOGICA---------
def validar_celda(fila, columna):
    return (0 <= fila < FILAS) and (0 <= columna < COLUMNAS)

def dibujar_matriz (pantalla) :
    for f in range(FILAS):
        for c in range(COLUMNAS):
            posicion_x = c * TAMAÑO_CELDA
            posicion_y = f * TAMAÑO_CELDA

            if matriz[f][c] == VACIO :
                color = CELDA_VACIA

            else :
                color = CELDA_OCUPADA

            pygame.draw.rect(campo_matriz, color, (posicion_x, posicion_y, TAMAÑO_CELDA, TAMAÑO_CELDA))

    #Lineas verticales
    for c in range (COLUMNAS + 1) :
        posicion_x = c * TAMAÑO_CELDA
        pygame.draw.line(campo_matriz, LINEA, (posicion_x, 0), (posicion_x, ALTO), 1)

    #Lineas horizontales
    for f in range(FILAS + 1) :
        posicion_y = f * TAMAÑO_CELDA
        pygame.draw.line(campo_matriz, LINEA, (0, posicion_y), (ANCHO, posicion_y), 1 )

def dibujar_tienda():

    campo_tienda.fill("Red")

    espacio_x = 20
    incio_y = 360
    ancho_cuadro_item = ANCHO - (espacio_x * 2)
    alto_cuadro_item = 128
    espaciado = 24

    #ESTO SE CAMBIARIA Y SE MANEJARIA CON LOS DATOS DE LOS ROOKS
    precios = [10, 20, 30, 40]  


    for i in range(4):
        y = incio_y + i * (alto_cuadro_item + espaciado)
        rect = pygame.Rect(espacio_x, y, ancho_cuadro_item, alto_cuadro_item)
        pygame.draw.rect(campo_tienda, (40, 40, 40), rect)          
        pygame.draw.rect(campo_tienda, (200, 200, 200), rect, 2)    

        # precio (esquina superior derecha del item)
        texto_precio = fuente_texto.render(f"${precios[i]}", False, "White")

        #Esto nada mas es para que el precio aparezca arriba a la derecha del cuadrito
        px = rect.right - texto_precio.get_width() - 8
        py = rect.top + 6
        campo_tienda.blit(texto_precio, (px, py))




def juego():

#Ciclo para que la ventana se mantenga abierta
    while True:


        #Obtiene todos los pisibles eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #cierra todo literalmente, se lo vuela todo para que no consuma memoria
                exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                local_x = mouse_x - 180
                local_y = mouse_y - ALTO_MAPA_CENTRADO

                # Click dentro del rectangulo para la matriz
                if 0 <= local_x < ANCHO and 0 <= local_y < ALTO:
                    fila = local_y // TAMAÑO_CELDA
                    columna = local_x // TAMAÑO_CELDA

                    if validar_celda(fila, columna):
                        #Click izquierdo
                        if event.button == 1:   
                            matriz[fila][columna] = OCUPADA
                        #Click derecho
                        elif event.button == 3: 
                            matriz[fila][columna] = VACIO

    #TODO el tema del dibujado de la matriz lo veremos luego porque en todo caso iria con imagenes
    #Por el momento es para probar ya luego veremnos si lo utilizamos para otra cosa

        pantalla.fill((18, 18, 18))

        dibujar_matriz(campo_matriz)
        pantalla.blit(campo_matriz, (180 , ALTO_MAPA_CENTRADO))
        
        dibujar_tienda()
        pantalla.blit(campo_tienda, (((ANCHO * 2) + 400) - ANCHO , 0))

        pantalla.blit(titulo_juego, (0, 0) )

        pygame.display.update()
        #Frames por segundo
        reloj.tick(60)


juego()


