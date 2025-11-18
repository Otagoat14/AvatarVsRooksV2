from machine import ADC, Pin
import time

class Boton:
    def __init__(self, pin_seleccionado):
        self.pin_boton = Pin(pin_seleccionado, Pin.IN)
        
    def esta_presionado(self):
        return self.pin_boton.value() == 0


class Joystick:
    def __init__(self, joystick_x, joystick_y, click):
        self.x = ADC(joystick_x)
        self.y = ADC(joystick_y)
        self.click = Pin(click, Pin.IN, Pin.PULL_UP)
        self.center = 32768
        self.dead_zone = 5000
        
    def getX(self):
        return self.x.read_u16()
    
    def getY(self):
        return self.y.read_u16()
    
    def get_click(self):
        return self.click.value() == 0
    
    def get_direction(self):
        x_val = self.getX()
        y_val = self.getY()
        dx = x_val - self.center
        dy = y_val - self.center

        if abs(dx) < self.dead_zone and abs(dy) < self.dead_zone:
            return "CENTRO"
        elif abs(dx) > abs(dy):
            return "DERECHA" if dx > 0 else "IZQUIERDA"
        else:
            return "ARRIBA" if dy > 0 else "ABAJO"


PIN_JOY_X = 27   
PIN_JOY_Y = 26   
PIN_JOY_CLICK = 22 

PIN_BOTON1 = 17
PIN_BOTON2 = 11
PIN_BOTON3 = 12
PIN_BOTON4 = 13

PIN_BOTON_SELECT = 14
PIN_BOTON_PAUSE = 15



#Creando las instancias
stick = Joystick(PIN_JOY_X, PIN_JOY_Y, PIN_JOY_CLICK)

boton1 = Boton(PIN_BOTON1)
boton2 = Boton(PIN_BOTON2)
boton3 = Boton(PIN_BOTON3)
boton4 = Boton(PIN_BOTON4)

boton_select = Boton(PIN_BOTON_SELECT)
boton_pause = Boton(PIN_BOTON_PAUSE)


while True:
    # Joystick
    dir = stick.get_direction()  
    click = stick.get_click()      

    # Botones de rooks
    b1 = boton1.esta_presionado()
    b2 = boton2.esta_presionado()
    b3 = boton3.esta_presionado()
    b4 = boton4.esta_presionado()

    # Botones extra
    b_select = boton_select.esta_presionado()
    b_pause = boton_pause.esta_presionado()

   
    print(
        f"JOY:{dir},"
        f"C:{int(click)},"
        f"B1:{int(b1)},"
        f"B2:{int(b2)},"
        f"B3:{int(b3)},"
        f"B4:{int(b4)},"
        f"BS:{int(b_select)},"
        f"BP:{int(b_pause)}"
    )

    time.sleep(0.05)  

