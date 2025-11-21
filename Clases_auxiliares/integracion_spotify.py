import spotipy
from spotipy.oauth2 import SpotifyOAuth

def crear_cliente_spotify():
    """Crea cliente Spotify con fallback"""
    try:
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id="37141bd00fde487fb1dbf3b8d2fdf6f4",  # Tu nuevo client_id
            client_secret="87a87eb30ee5418f9f07c0c1800e0905",  # Tu nuevo client_secret
            redirect_uri="http://127.0.0.1:8888/callback",
            scope="user-modify-playback-state user-read-playback-state",
        ))
        # Probar la conexión
        sp.search(q="test", limit=1)
        print("✅ Spotify integrado correctamente")
        return sp, True
    except Exception as e:
        print(f"❌ Spotify no disponible: {e}")
        print("🔶 Juego funcionará sin integración musical")
        return None, False

sp, spotify_disponible = crear_cliente_spotify()

def buscar_y_reproducir(cancion):
    if not spotify_disponible or sp is None:
        print(f"🎵 Modo demo: Canción '{cancion}' seleccionada")
        print("🔊 La música se reproducirá en el juego")
        return True
    
    try:
        resultados = sp.search(q=cancion, type="track", limit=1)
        items = resultados.get("tracks", {}).get("items", [])
        
        if not items:
            print("No encontré esa canción en Spotify.")
            return False
        
        track = items[0]
        track_uri = track.get("uri")
        nombre = track.get("name")
        artista = track.get("artists", [{}])[0].get("name")

        print(f'🎵 Escuchando {nombre} - {artista}')

        try:
            dispositivos = sp.devices()
        except Exception as e:
            print("Error al obtener dispositivos:", e)
            dispositivos = {"devices": []}

        if not dispositivos.get("devices"):
            print("No tiene premium o no hay dispositivos activos")
            return False
        
        device_id = dispositivos["devices"][0].get("id")
        try:
            sp.start_playback(device_id=device_id, uris=[track_uri])
            print("✅ Reproducción iniciada en Spotify")
            return True
        except Exception as e:
            print("No pude iniciar la reproducción:", e)
            return False
            
    except Exception as e:
        print(f"Error con Spotify: {e}")
        return False

# Modificar la parte principal del archivo:
if __name__ == "__main__":
    cancion = input("¿Qué canción quiere? ")
    buscar_y_reproducir(cancion)