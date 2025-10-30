# ============================================================
# PASO 1: Crear nuevo archivo: musica_ambiental.py
# ============================================================

import pygame
import os

class MusicaAmbiental:    
    def __init__(self):
        self.inicializado = False
        self.reproduciendo = False
        self.volumen = 0.3  
        self.ruta_musica = None
        self._inicializar_pygame()
    
    def _inicializar_pygame(self):
        try:
            pygame.mixer.init()
            self.inicializado = True
        except Exception as e:
            print(f"Error al inicializar pygame mixer: {e}")
            self.inicializado = False
    
    def cargar_musica(self, ruta_archivo):
        if not self.inicializado:
            return False
        
        if not os.path.exists(ruta_archivo):
            print(f"Archivo de música no encontrado: {ruta_archivo}")
            return False
        
        try:
            pygame.mixer.music.load(ruta_archivo)
            self.ruta_musica = ruta_archivo
            return True
        except Exception as e:
            print(f"Error al cargar música: {e}")
            return False
    
    def reproducir(self, loops=-1):
        if not self.inicializado or self.ruta_musica is None:
            return
        
        try:
            pygame.mixer.music.set_volume(self.volumen)
            pygame.mixer.music.play(loops=loops)
            self.reproduciendo = True
        except Exception as e:
            print(f"Error al reproducir música: {e}")
    
    def detener(self):
        if not self.inicializado:
            return
        
        try:
            pygame.mixer.music.stop()
            self.reproduciendo = False
        except Exception as e:
            print(f"Error al detener música: {e}")
    
    def pausar(self):
        if not self.inicializado:
            return
        
        try:
            pygame.mixer.music.pause()
        except Exception as e:
            print(f"Error al pausar música: {e}")
    
    def reanudar(self):
        if not self.inicializado:
            return
        
        try:
            pygame.mixer.music.unpause()
        except Exception as e:
            print(f"Error al reanudar música: {e}")
    
    def cambiar_volumen(self, volumen):
        if not self.inicializado:
            return
        
        self.volumen = max(0.0, min(1.0, volumen))
        try:
            pygame.mixer.music.set_volume(self.volumen)
        except Exception as e:
            print(f"Error al cambiar volumen: {e}")
    
    def esta_reproduciendo(self):
        if not self.inicializado:
            return False
        
        try:
            return pygame.mixer.music.get_busy()
        except Exception:
            return False


MUSICA = MusicaAmbiental()