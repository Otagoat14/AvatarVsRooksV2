import pygame
from sys import exit

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

#Matriz con None para que podamos personlizarla
matriz = [[None for c in range(COLUMNAS)] for f in range(FILAS)]
print(matriz)


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

#Ciclo para que la ventana se mantenga abierta
while True:

    #Obtiene todos los pisibles eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            #cierra todo literalmente, se lo vuela todo para que no consuma memoria
            exit()

#TODO el tema del dibujado de la matriz lo veremos luego porque en todo caso iria con imagenes
#Por el momento es para probar ya luego veremnos si lo utilizamos para otra cosa

    #Dibujar la matriz
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


    pantalla.blit(campo_matriz,(ANCHO//2, ALTO//2))
    pantalla.blit(titulo_juego, (0, 0) )

    pygame.display.update()
    #Frames por segundo
    reloj.tick(60)


