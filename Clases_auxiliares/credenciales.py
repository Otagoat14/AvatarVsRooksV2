import json
import os
from .config import RUTA_PREFERENCIAS, CARPETA_ARCHIVOS

# Archivos dentro de la carpeta Archivos
ARCHIVO_PREFERENCIAS = RUTA_PREFERENCIAS
ARCHIVO_CREDENCIALES = os.path.join(CARPETA_ARCHIVOS, "credenciales.json")

def cargar_preferencias():
    """Cargar preferencias del usuario incluyendo idioma"""
    try:
        if os.path.exists(ARCHIVO_PREFERENCIAS):
            with open(ARCHIVO_PREFERENCIAS, 'r') as f:
                prefs = json.load(f)
                return prefs
    except Exception:
        pass
    return {"recordar": False, "idioma": "es"}

def guardar_preferencias(recordar: bool, idioma: str = "es"):
    """Guardar preferencias del usuario incluyendo idioma"""
    try:
        prefs = {
            "recordar": recordar,
            "idioma": idioma
        }
        with open(ARCHIVO_PREFERENCIAS, 'w') as f:
            json.dump(prefs, f)
        return True
    except Exception:
        return False

def cargar_credenciales():
    """Cargar credenciales guardadas"""
    try:
        if os.path.exists(ARCHIVO_CREDENCIALES):
            with open(ARCHIVO_CREDENCIALES, 'r') as f:
                creds = json.load(f)
                return creds.get("usuario"), creds.get("contraseña")
    except Exception:
        pass
    return None, None

def guardar_credenciales(usuario: str, contraseña: str, recordar: bool):
    """Guardar credenciales si el usuario lo permite"""
    try:
        if recordar:
            creds = {
                "usuario": usuario,
                "contraseña": contraseña
            }
            with open(ARCHIVO_CREDENCIALES, 'w') as f:
                json.dump(creds, f)
        else:
            # Si no recordar, eliminar archivo si existe
            if os.path.exists(ARCHIVO_CREDENCIALES):
                os.remove(ARCHIVO_CREDENCIALES)
        return True
    except Exception:
        return False