import json
import os

def ruta_perfil_usuario(username):
    return f"perfiles/{username}_perfil.json"

def ruta_tema_json(username):
    return f"perfiles/{username}_tema.json"

def personalizacion_ya_hecha(username):
    ruta = ruta_perfil_usuario(username)
    return os.path.exists(ruta)

def marcar_personalizacion(username, tema_dict, musica_uri=None):
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

def cargar_personalizacion(username):
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