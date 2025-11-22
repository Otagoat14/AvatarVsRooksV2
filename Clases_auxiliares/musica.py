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


#EFECTOS DE SONIDO

# Clases_auxiliares/sonidos.py
import pygame

# Rutas de los archivos de sonido
RUTA_PONER_ROOK = "musica/poner_rook.mp3"
RUTA_TORRE_DERRUMBADA = "musica/torre_derrumbada.mp3"
RUTA_DISPARO_ROOKS = "musica/disparo_rooks.mp3"
RUTA_DISPARO_AVATARS = "musica/disparo_avatars.mp3"
RUTA_AVATAR_DERRUMBADO = "musica/avatar_derrumbado.mp3"
RUTA_SELECCIONAR_CAMPO = "musica/seleccionar_campo.mp3"


# Variables globales para los sonidos (se cargan perezosamente)
_sonido_poner_rook = None
_sonido_torre_derrumbada = None
_sonido_disparo_rooks = None
_sonido_disparo_avatars = None
_sonido_avatar_derrumbado = None
_sonido_seleccionar_campo = None


def _cargar_sonidos_si_no():
    """Carga los sonidos solo la primera vez que se usan."""
    global _sonido_poner_rook, _sonido_torre_derrumbada
    global _sonido_disparo_rooks, _sonido_disparo_avatars, _sonido_avatar_derrumbado
    global _sonido_seleccionar_campo

    try:
        if _sonido_poner_rook is None:
            _sonido_poner_rook = pygame.mixer.Sound(RUTA_PONER_ROOK)
        if _sonido_torre_derrumbada is None:
            _sonido_torre_derrumbada = pygame.mixer.Sound(RUTA_TORRE_DERRUMBADA)
        if _sonido_disparo_rooks is None:
            _sonido_disparo_rooks = pygame.mixer.Sound(RUTA_DISPARO_ROOKS)
        if _sonido_disparo_avatars is None:
            _sonido_disparo_avatars = pygame.mixer.Sound(RUTA_DISPARO_AVATARS)
        if _sonido_avatar_derrumbado is None:
            _sonido_avatar_derrumbado = pygame.mixer.Sound(RUTA_AVATAR_DERRUMBADO)
        if _sonido_seleccionar_campo is None:                
            _sonido_seleccionar_campo = pygame.mixer.Sound(RUTA_SELECCIONAR_CAMPO)

    except Exception as e:
        print("[SONIDOS] Error cargando sonidos:", e)


def reproducir_poner_rook():
    _cargar_sonidos_si_no()
    if _sonido_poner_rook:
        _sonido_poner_rook.play()


def reproducir_torre_derrumbada():
    _cargar_sonidos_si_no()
    if _sonido_torre_derrumbada:
        _sonido_torre_derrumbada.play()


def reproducir_disparo_rooks():
    _cargar_sonidos_si_no()
    if _sonido_disparo_rooks:
        _sonido_disparo_rooks.play()


def reproducir_disparo_avatars():
    _cargar_sonidos_si_no()
    if _sonido_disparo_avatars:
        _sonido_disparo_avatars.play()


def reproducir_avatar_derrumbado():
    _cargar_sonidos_si_no()
    if _sonido_avatar_derrumbado:
        _sonido_avatar_derrumbado.play()

def reproducir_seleccionar_campo():
    _cargar_sonidos_si_no()
    if _sonido_seleccionar_campo:
        _sonido_seleccionar_campo.play()

