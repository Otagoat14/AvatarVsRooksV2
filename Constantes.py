FILAS = 9
COLUMNAS = 5
TAMAÑO_CELDA = 80

#Practiacamente para sacar el tamanno del mapa en pixeles
ANCHO = COLUMNAS * TAMAÑO_CELDA
ALTO = FILAS * TAMAÑO_CELDA

#Matriz con None para que podamos personlizarla
matriz = [[None for c in range(COLUMNAS)] for f in range(FILAS)]
print(matriz)