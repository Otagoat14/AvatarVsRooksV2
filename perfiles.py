import json
import os

# ==============================
# CONFIGURACIÓN DE RUTAS SEGURAS
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PERFILES_DIR = os.path.join(BASE_DIR, "perfiles")

def ruta_perfil_usuario(username):
    os.makedirs(PERFILES_DIR, exist_ok=True)
    return os.path.join(PERFILES_DIR, f"{username}_perfil.json")

def ruta_tema_json(username):
    os.makedirs(PERFILES_DIR, exist_ok=True)
    return os.path.join(PERFILES_DIR, f"{username}_tema.json")


# ==============================
# FUNCIONES DE PERFIL Y TEMA
# ==============================

def personalizacion_ya_hecha(username):
    ruta_perfil = ruta_perfil_usuario(username)
    ruta_tema = ruta_tema_json(username)
    # ✅ Verifica ambos archivos (perfil o tema)
    return os.path.exists(ruta_perfil) or os.path.exists(ruta_tema)


def marcar_personalizacion(username, tema_dict, musica_uri=None):
    """Guarda o actualiza la personalización completa del usuario."""
    ruta = ruta_perfil_usuario(username)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    
    perfil = {
        "usuario": username,
        "personalizado": True,
        "tema": tema_dict,
        "musica": musica_uri
    }
    
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(perfil, f, indent=2, ensure_ascii=False)

    try:
        ruta_tema = ruta_tema_json(username)
        os.makedirs(os.path.dirname(ruta_tema), exist_ok=True)
        # Estructura compatible con lo que esperan otros módulos
        data = {
            "colores": tema_dict,
            "musica": musica_uri
        }
        with open(ruta_tema, "w", encoding="utf-8") as ft:
            json.dump(data, ft, indent=2, ensure_ascii=False)
    except Exception as _:
        pass

def cargar_personalizacion(username):
    """Carga la personalización del usuario desde el JSON."""
    try:
        ruta = ruta_perfil_usuario(username)
        if os.path.exists(ruta):
            with open(ruta, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error cargando personalización de {username}: {e}")
    return None


def cargar_perfil(username):
    return cargar_personalizacion(username)


def cargar_tema_usuario(username):
    perfil = cargar_personalizacion(username)
    if perfil and 'tema' in perfil:
        return perfil['tema']
    return None


def es_primer_inicio(username):
    """
    Retorna True si el usuario aún no tiene un perfil o tema guardado,
    es decir, si es la primera vez que inicia sesión.
    """
    return not personalizacion_ya_hecha(username)


def obtener_colores(username):
    """
    Devuelve un diccionario RGB con los colores personalizados del usuario.
    Si no tiene personalización, devuelve los colores por defecto.
    """
    try:
        ruta = ruta_tema_json(username)
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
                colores = data.get("colores") or data.get("tema")
                if colores:
                    return colores
        else:
            # Si no hay tema.json, intenta cargar desde el perfil.json
            perfil = cargar_personalizacion(username)
            if perfil and "tema" in perfil:
                return perfil["tema"]

    except Exception as e:
        print(f"[obtener_colores] Error: {e}")
    
    # 🎨 Valores por defecto si no hay personalización
    return {
        "fondo": {"rgb": [30, 33, 36]},
        "btn_primario": {"rgb": [155, 17, 30]},
        "texto": {"rgb": [255, 250, 250]},
        "ventana": {"rgb": [210, 200, 190]},
        "btn_secundario": {"rgb": [227, 66, 52]}
    }


def obtener_paleta_personalizada(username):
    """
    Devuelve una paleta de colores lista para aplicar en cualquier ventana
    (fondo, botón, texto, etc.), basada en el tema guardado del usuario.
    """
    colores = obtener_colores(username)

    def rgb(nombre, defecto):
        return tuple(colores.get(nombre, {}).get("rgb", defecto))

    return {
        "FONDO_PANTALLA": rgb("fondo", (30, 33, 36)),
        "CARD_BG": rgb("ventana", (155, 17, 30)),
        "CARD_BORDER": rgb("texto", (255, 250, 250)),
        "COLOR_TEXT_TITU": rgb("texto", (255, 250, 250)),
        "COLOR_TEXT_CUER": rgb("btn_secundario", (210, 200, 190)),
        "COLOR_BOTONES": rgb("btn_primario", (227, 66, 52))
    }

def obtener_musica_usuario(username):
    """
    Devuelve la URI de Spotify guardada para el usuario (o None si no tiene).
    Primero intenta leerla del <usuario>_tema.json y luego del <usuario>_perfil.json.
    """
    try:
        # 1) Intentar en <usuario>_tema.json
        ruta_tema = ruta_tema_json(username)
        if os.path.exists(ruta_tema):
            with open(ruta_tema, "r", encoding="utf-8") as f:
                data = json.load(f)
            uri = data.get("musica")
            if uri:
                return uri

        # 2) Intentar en <usuario>_perfil.json
        perfil = cargar_personalizacion(username)
        if perfil:
            return perfil.get("musica")

    except Exception as e:
        print(f"[obtener_musica_usuario] Error: {e}")

    return None


