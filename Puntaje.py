
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
    def __init__(self, usuario = "None"):
        self.usuario = usuario
        self.tempo = 0
        self.popularidad = 0
        self.avatars_matados = 0
        self.puntos_totales_avatars = 0
        self.cargar_datos_cancion()

    def _ruta_datos_cancion_usuario(self):
        # misma lógica de personalizacion_GUI.ruta_datos_cancion
        try:
            from perfiles import ruta_tema_json
            ruta_tema = ruta_tema_json(self.usuario) if self.usuario else None
            if ruta_tema:
                base_dir = os.path.dirname(ruta_tema)
                return os.path.join(base_dir, "datos_cancion.json")
        except Exception:
            pass
        return "datos_cancion.json"  # fallback
    
    def cargar_datos_cancion(self):
        try:
            ruta = self._ruta_datos_cancion_usuario()
            if ruta and os.path.exists(ruta):
                with open(ruta, "r", encoding="utf-8") as f:
                    datos = json.load(f)
                    self.tempo = int(datos.get("tempo", 120))
                    self.popularidad = int(datos.get("popularidad", 50))
                    print(f"Datos cargados - Tempo: {self.tempo}, Popularidad: {self.popularidad}")
            else:
                self.tempo, self.popularidad = 120, 50
                print("Usando valores por defecto para el puntaje (no hay canción seleccionada)")
        except Exception as e:
            print(f"Error cargando datos de canción: {e}")
            self.tempo, self.popularidad = 120, 50
    
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
            "puntaje_final": self.calcular_puntaje(),
            "tempo": self.tempo,
            "popularidad": self.popularidad,
            "avatars_matados": self.avatars_matados,
            "puntos_avatars": self.puntos_totales_avatars
        }

