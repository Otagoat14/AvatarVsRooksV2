
from math import sqrt
import json
import os


#Primer codigo
"""tempo = "FALTA INVESTIGAR"
popularidad = "Falta investigar"
avatars_matados = "Lo que retorne la logica"
puntos_avatar =  0#Avatar.vida


if tempo > 0 and popularidad > 0 :
    media_armonica = 2 / ((1 / tempo) + (1 / popularidad))
else:
    media_armonica = 0
    
  

limite_maximo = (tempo + popularidad + (avatars_matados * puntos_avatar)) * 0.2
factor_intensidad = (avatars_matados / (tempo + 1)) * 0.05
factor_avatar = 1 + sqrt(puntos_avatar / 500)

puntaje_ajustado = (media_armonica + (factor_intensidad * 100)) * factor_avatar

if puntaje_ajustado > limite_maximo :
    puntaje_ajustado = limite_maximo


return puntaje_ajustado """


class CalculadorPuntaje:
    def __init__(self):
        self.tempo = 0
        self.popularidad = 0
        self.avatars_matados = 0
        self.puntos_totales_avatars = 0
        self.cargar_datos_cancion()
    
    def cargar_datos_cancion(self):
        try:
            if os.path.exists("datos_cancion.json"):
                with open("datos_cancion.json", "r") as f:
                    datos = json.load(f)
                    self.tempo = datos.get("tempo", 120)  # Valor por defecto
                    self.popularidad = datos.get("popularidad", 50)
                    print(f"Datos cargados - Tempo: {self.tempo}, Popularidad: {self.popularidad}")
            else:
                # Valores por defecto si no hay canción seleccionada
                self.tempo = 120
                self.popularidad = 50
                print("Usando valores por defecto para el puntaje")
        except Exception as e:
            print(f"Error cargando datos de canción: {e}")
            self.tempo = 120
            self.popularidad = 50
    
    def actualizar_avatars(self, cantidad_muertos, puntos_avatar):
        self.avatars_matados = cantidad_muertos
        self.puntos_totales_avatars = puntos_avatar
    
    def calcular_puntaje(self):
        # Media armónica (evita división por cero)
        if self.tempo > 0 and self.popularidad > 0:
            media_armonica = 2 / ((1 / self.tempo) + (1 / self.popularidad))
        else:
            media_armonica = 0
        
        # Límite máximo del puntaje
        limite_maximo = (self.tempo + self.popularidad + 
                        (self.avatars_matados * self.puntos_totales_avatars)) * 0.2
        
        # Factor de intensidad (qué tan rápido matas avatars)
        factor_intensidad = (self.avatars_matados / (self.tempo + 1)) * 0.05
        
        # Factor avatar (bonificación por puntos de avatar)
        if self.puntos_totales_avatars > 0:
            factor_avatar = 1 + sqrt(self.puntos_totales_avatars / 500)
        else:
            factor_avatar = 1
        
        # Cálculo del puntaje ajustado
        puntaje_ajustado = (media_armonica + (factor_intensidad * 100)) * factor_avatar
        
        # Aplicar límite máximo
        if puntaje_ajustado > limite_maximo:
            puntaje_ajustado = limite_maximo
        
        return int(puntaje_ajustado)
    
    def obtener_detalles(self):
        return {
            'puntaje_final': self.calcular_puntaje(),
            'tempo': self.tempo,
            'popularidad': self.popularidad,
            'avatars_matados': self.avatars_matados,
            'puntos_avatars': self.puntos_totales_avatars
        }

