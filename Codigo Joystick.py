from machine import ADC, Pin
import time
import sys

class Joystick:
    def __init__(self, joystick_x, joystick_y, click ):
        self.x = ADC(joystick_x)
        self.y = ADC(joystick_y)
        self.click = Pin(click, Pin.In, Pin_PULL_UP)
        self.center = 32768
        self.dead_zone = 5000

        
        
    def getX(self):
        return self.x.read_u16()
    
    def getY(self):
        return self.y.read_u16()
    
    def get_click(self):
        return not self.click.value()
    
    def get_direction(self):
        x_val = self.getX()
        y_val = self.getY()
        dx = x_val - self.center
        dy = y_val - self.center

        if abs(dx) < self.dead_zone and abs(dy) < self.dead_zone:
            return "CENTRO"
        elif abs(dx) > abs(dy):
            return "DERECHA" if dx > 0 else "IZQUIERDA"
        else :
            return "ARRIBA" if dy > 0 else "ABAJO"
        
        
    
stick = Joystick() #Hay que poner los pines analogicos y el digital ejm (27, 26, 22)

while True :
    dir = stick.get_direction()
    click = stick.get_click()
    print(f"{dir}, {int(click)}")
    
    time.sleep(0.1)
    
