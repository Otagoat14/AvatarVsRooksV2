import pygame
from sys import exit

FILAS = 9
COLUMNAS = 5
TAMAÑO_CELDA = 80

#Practiacamente para sacar el tamanno del mapa en pixeles
ANCHO = COLUMNAS * TAMAÑO_CELDA
ALTO = FILAS * TAMAÑO_CELDA

#Matriz con None para que podamos personlizarla
matriz = [[None for c in range(COLUMNAS)] for f in range(FILAS)]
print(matriz)


pygame.init()
#lo de la pantalla se puede cambiar para que quede de forma estetica
pantalla = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Avatar vs Rooks")
reloj = pygame.time.Clock()
#Agregar el logo del juego

#Ciclo para que la ventana se mantenga abierta
while True:

    #Obtiene todos los pisibles eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            #cierra todo literalmente, se lo vuela todo para que no consuma memoria
            exit()

    pygame.display.update()

    #Frames por segundo
    reloj.tick(60)


