import pygame
from sys import exit

#------CONSTANTES--------
FILAS = 9
COLUMNAS = 5
TAMAÑO_CELDA = 40

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

ORIGEN_X = ANCHO // 2
ORIGEN_Y = ALTO  // 2

#Matriz con None para que podamos personlizarla
matriz = [[VACIO for c in range(COLUMNAS)] for f in range(FILAS)]
print(matriz)

#------------------------------


pygame.init()
#lo de la pantalla se puede cambiar para que quede de forma estetica
pantalla = pygame.display.set_mode((ANCHO * 2, ALTO * 2))
pygame.display.set_caption("Avatar vs Rooks")
reloj = pygame.time.Clock()
fuente_texto = pygame.font.Font("Fuentes/super_sliced.otf", 20)
#Agregar el logo del juego

campo_matriz = pygame.Surface((ANCHO, ALTO))
campo_matriz.fill("Red")

#para hacer que se vea mas estetico se puede hcaer con las imagenes y los surfaces
#fondo_pantalla = pygame.image.load("imagenes/fondo_pantalla.png")

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
                local_x = mouse_x - ORIGEN_X
                local_y = mouse_y - ORIGEN_Y

                # Click dentro del rectángulo de la grilla (en coords locales)
                if 0 <= local_x < ANCHO and 0 <= local_y < ALTO:
                    fila = local_y // TAMAÑO_CELDA
                    columna = local_x // TAMAÑO_CELDA

                    if validar_celda(fila, columna):
                        if event.button == 1:   # izquierdo: poner en OCUPADA
                            matriz[fila][columna] = OCUPADA
                        elif event.button == 3: # derecho: vaciar
                            matriz[fila][columna] = VACIO
                        

                

    #TODO el tema del dibujado de la matriz lo veremos luego porque en todo caso iria con imagenes
    #Por el momento es para probar ya luego veremnos si lo utilizamos para otra cosa

        pantalla.fill((18, 18, 18))
        dibujar_matriz(campo_matriz)
        pantalla.blit(campo_matriz,(ANCHO//2, ALTO//2))
        pantalla.blit(titulo_juego, (0, 0) )

        pygame.display.update()
        #Frames por segundo
        reloj.tick(60)


