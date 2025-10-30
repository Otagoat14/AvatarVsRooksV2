# traductor_pygame.py
from Traductor import dic_idiomas

class TraductorPygame:
    def __init__(self, lang="es"):
        self.lang = lang
        self.diccionario = dic_idiomas.get(lang, dic_idiomas["es"])
    
    def t(self, key):
        """Traduce una clave al idioma actual"""
        return self.diccionario.get(key, key)
    
    def cambiar_idioma(self, nuevo_lang):
        """Cambia el idioma en tiempo de ejecución"""
        self.lang = nuevo_lang
        self.diccionario = dic_idiomas.get(nuevo_lang, dic_idiomas["es"])
    
    def obtener_texto(self, key, default=None):
        """Obtiene texto traducido con valor por defecto"""
        return self.diccionario.get(key, default or key)

# Instancia global
traductor_global = TraductorPygame()

def t(key):
    """Función global para facilitar el uso"""
    return traductor_global.t(key)

def configurar_idioma(lang):
    """Configura el idioma globalmente"""
    traductor_global.cambiar_idioma(lang)