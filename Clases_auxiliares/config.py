# Clases_auxiliares/config.py
import os

# Ruta base de archivos (relativa a la raíz del proyecto)
CARPETA_ARCHIVOS = "Archivos"

# Rutas específicas
RUTA_CACHE = os.path.join(CARPETA_ARCHIVOS, "cache")
RUTA_TARJETA_KEY = os.path.join(CARPETA_ARCHIVOS, "tarjeta_key")
RUTA_PALABRAS_PROHIBIDAS = os.path.join(CARPETA_ARCHIVOS, "palabras_prohibidas.txt")
RUTA_PREFERENCIAS = os.path.join(CARPETA_ARCHIVOS, "preferencias.json")
RUTA_TARJETAS_ENC = os.path.join(CARPETA_ARCHIVOS, "tarjetas.enc")
RUTA_TEMA = os.path.join(CARPETA_ARCHIVOS, "tema.json")
RUTA_USUARIOS_PKL = os.path.join(CARPETA_ARCHIVOS, "usuarios.pkl")
RUTA_USUARIOS_DIR = os.path.join(CARPETA_ARCHIVOS, "usuarios")

def crear_estructura():
    """Crear la estructura de carpetas si no existe"""
    try:
        # Solo crear si no existen
        if not os.path.exists(RUTA_CACHE):
            os.makedirs(RUTA_CACHE)
            print(f"✅ Carpeta cache creada: {RUTA_CACHE}")
        
        if not os.path.exists(RUTA_USUARIOS_DIR):
            os.makedirs(RUTA_USUARIOS_DIR)
            print(f"✅ Carpeta usuarios creada: {RUTA_USUARIOS_DIR}")
        
        # Verificar que Archivos existe
        if not os.path.exists(CARPETA_ARCHIVOS):
            os.makedirs(CARPETA_ARCHIVOS)
            print(f"✅ Carpeta Archivos creada: {CARPETA_ARCHIVOS}")
            
        print("✅ Estructura de archivos verificada")
        return True
        
    except Exception as e:
        print(f"❌ Error creando estructura: {e}")
        return False

# Crear estructura al importar (pero silenciosamente)
try:
    crear_estructura()
except:
    pass  # Ignorar errores en importación