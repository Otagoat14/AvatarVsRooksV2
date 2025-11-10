import pygame 
import serial
import time

#Puerto al que esta conectado la raspherry pi
#Hay que avaertir el puerto serial antes de ejecutar el codigo
ser = serial.Serial("COM3", 115200, timeout = 0.1)
time.sleep(2)  


pygame.init
ANCHO, ALTO = 600, 400
screen = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Control de Robot con Joystick")

#Cuadro
x, y = ANCHO // 2, ALTO // 2
speed = 5
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    if ser.in_waiting:
        try:

            line = ser.readline().decode().strip()
            if line:
                direction, click = line.split(",")
                click = bool(int(click))

                if direction == "ARRIBA":
                    y -= speed

                elif direction == "ABAJO":
                    y += speed
                
                elif direction == "IZQUIERDA":
                    x -= speed

                elif direction == "DERECHA":
                    x += speed

                if click:
                    print("Click")

        except Exception as e:
            print("ERROR:", e)

    screen.fill((30, 30, 30))
    pygame.draw.rect(screen, (0, 255, 0), (x, y, 50, 50))
    pygame.display.flip()
    clock.tick(60)

    

            
    


pygame.quit()

    
