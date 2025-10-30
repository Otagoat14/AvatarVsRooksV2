# perfiles.py
import os, json
<<<<<<< HEAD
from Clases_auxiliares.config import CARPETA_ARCHIVOS

BASE_DIR = os.path.join(CARPETA_ARCHIVOS, "usuarios")
=======

BASE_DIR = "users_lbph"
>>>>>>> feature/personalizacion

def _user_dir(username: str) -> str:
    return os.path.join(BASE_DIR, username.strip().lower())

def _profile_path(username: str) -> str:
    return os.path.join(_user_dir(username), "perfil.json")

def cargar_perfil(username: str) -> dict:
    path = _profile_path(username)
    if not os.path.exists(path):
        return {"personalizacion_completada": False, "tema": None, "spotify_uri": None}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar_perfil(username: str, data: dict) -> None:
    os.makedirs(_user_dir(username), exist_ok=True)
    with open(_profile_path(username), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def personalizacion_ya_hecha(username: str) -> bool:
    return bool(cargar_perfil(username).get("personalizacion_completada"))

def marcar_personalizacion(username: str, tema_colores: dict, musica_uri: str | None) -> None:
    data = cargar_perfil(username)
    data["personalizacion_completada"] = True
    data["tema"] = tema_colores
    data["spotify_uri"] = musica_uri
    guardar_perfil(username, data)

def ruta_tema_json(username: str) -> str:
<<<<<<< HEAD
    return os.path.join(_user_dir(username), "tema.json")
=======
    return os.path.join(_user_dir(username), "tema.json")
>>>>>>> feature/personalizacion
