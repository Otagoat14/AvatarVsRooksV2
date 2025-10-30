import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id = "37141bd00fde487fb1dbf3b8d2fdf6f4",
    client_secret = "87a87eb30ee5418f9f07c0c1800e0905",
    redirect_uri = "http://127.0.0.1:8888/callback",
    scope = "user-modify-playback-state user-read-playback-state",
))

cancion = input("¿Qué canción quiere? ")

try:
    resultados = sp.search(q = cancion, type = "track", limit = 1)
except Exception as e:
    print("Error buscando la canción en Spotify:", e)
    raise

items = resultados.get("tracks", {}).get("items", [])
if not items:
    print("No encontré esa canción en Spotify. Verifica el nombre e intenta otra vez.")
else:
    track = items[0]
    track_uri = track.get("uri")
    nombre = track.get("name")
    artista = track.get("artists", [{}])[0].get("name")

    print(f'Escuchando {nombre} - {artista}')

    # Dispositivos disponibles (solo intento playback si encontré la canción)
    try:
        dispositivos = sp.devices()
    except Exception as e:
        print("Error al obtener dispositivos:", e)
        dispositivos = {"devices": []}

    if not dispositivos.get("devices"):
        print("No tiene premium o no hay dispositivos activos")
    else:
        device_id = dispositivos["devices"][0].get("id")
        try:
            sp.start_playback(device_id = device_id, uris=[track_uri])
            print("Reproducción iniciada.")
        except Exception as e:
            print("No pude iniciar la reproducción:", e)

