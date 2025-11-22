import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Puedes mover estos a variables de entorno si quieres
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "37141bd00fde487fb1dbf3b8d2fdf6f4")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "87a87eb30ee5418f9f07c0c1800e0905")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback")

SCOPE = "user-modify-playback-state user-read-playback-state"

_sp = None  # Cliente global reutilizable

def _get_spotify():
    global _sp
    if _sp is None:
        _sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE
        ))
    return _sp

def reproducir_uri(uri: str) -> bool:
    """
    Reproduce la URI dada en el primer dispositivo disponible.
    Devuelve True si parece que se reprodujo, False si no.
    """
    try:
        sp = _get_spotify()
        devices = sp.devices().get("devices", [])
        if not devices:
            print("No hay dispositivos activos de Spotify.")
            return False

        device_id = devices[0]["id"]

        # Intentar tomar control del dispositivo
        try:
            sp.transfer_playback(device_id, force_play=True)
        except Exception:
            pass

        sp.start_playback(device_id=device_id, uris=[uri])
        print(f"Reproduciendo {uri} en Spotify.")
        return True
    except Exception as e:
        print(f"[spotify_helper.reproducir_uri] Error: {e}")
        return False
