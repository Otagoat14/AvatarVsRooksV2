import pygame
import pygame_gui
import colorsys
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from perfiles import marcar_personalizacion, ruta_tema_json
from Traductor import dic_idiomas

BG = (20, 22, 26)
TEXT_TITLE = (245, 245, 245)

def clamp(x, a=0, b=255):
    try:
        return max(a, min(b, int(x)))
    except Exception:
        return a

def rgb_to_hex(rgb):
    r,g,b = rgb
    return "#{:02X}{:02X}{:02X}".format(clamp(r), clamp(g), clamp(b))

def hex_to_rgb(hexstr):
    s = hexstr.strip().lstrip("#")
    if len(s) == 3: s = "".join([c*2 for c in s])
    if len(s) != 6: raise ValueError("HEX inválido")
    return tuple(int(s[i:i+2], 16) for i in (0,2,4))

def aplicar_intensidad(rgb, intensidad_idx):
    """Ajusta brillo según intensidad: 0=baja, 1=media, 2=alta"""
    r,g,b = rgb
    if intensidad_idx == 0:  # clara
        factor = 1.2
    elif intensidad_idx == 2:  # oscura
        factor = 0.7
    else:
        factor = 1.0
    return tuple(clamp(v * factor) for v in (r,g,b))

def ruta_datos_cancion(username: str):
    from perfiles import ruta_tema_json
    ruta_tema = ruta_tema_json(username)
    base_dir = os.path.dirname(ruta_tema)
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "datos_cancion.json")

# -------------------------
# GENERACIÓN AUTOMÁTICA DE PALETA
# -------------------------
def generar_paleta(base_rgb):
    r,g,b = base_rgb
    def mezclar(c, factor):
        return tuple(clamp(v * factor + (255 * (1 - factor))) for v in c)

    fondo = mezclar(base_rgb, 0.1)
    ventana = mezclar(base_rgb, 0.25)
    texto = (245,245,245) if sum(base_rgb)/3 < 150 else (20,20,20)
    btn_primario = base_rgb
    btn_secundario = mezclar(base_rgb, 0.7)
    return {
        "fondo": {"rgb": fondo},
        "texto": {"rgb": texto},
        "ventana": {"rgb": ventana},
        "btn_primario": {"rgb": btn_primario},
        "btn_secundario": {"rgb": btn_secundario}
    }

# -------------------------
# MAPA DE COLOR HSV
# -------------------------
def generar_hs_surface(w, h):
    surf = pygame.Surface((w, h))
    px = pygame.PixelArray(surf)
    for x in range(w):
        hue = x / (w-1)
        for y in range(h):
            sat = 1 - (y / (h-1))
            r,g,b = colorsys.hsv_to_rgb(hue, sat, 1.0)
            px[x, y] = (clamp(r*255), clamp(g*255), clamp(b*255))
    del px
    return surf.convert()

# -------------------------
# SPOTIFY CLIENT
# -------------------------
class SpotifyClient:
    def __init__(self, lang="es"):
        self.lang = lang
        self.sp = None
        self.last_track = None
        self.conectado = False
        self._inicializar_spotify()

    def _inicializar_spotify(self):
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id="37141bd00fde487fb1dbf3b8d2fdf6f4",
                client_secret="87a87eb30ee5418f9f07c0c1800e0905",
                redirect_uri="http://127.0.0.1:8888/callback",
                scope="user-modify-playback-state user-read-playback-state"
            ))
            self.sp.search(q='test', type='track', limit=1)
            print("✅ Spotify conectado correctamente")
            self.conectado = True
        except Exception as e:
            print(f"❌ Spotify no disponible: {e}")
            print("🔶 Funcionando en modo demo")
            self.conectado = False

    def t(self, key):
        return dic_idiomas.get(self.lang, dic_idiomas["es"]).get(key, key)

    def buscar_cancion(self, q):
        if not self.conectado:
            demo = {
                "bad bunny": ("Bad Bunny - Demo", "Artista Demo", "spotify:track:demo1"),
                "queen": ("Queen - Bohemian Rhapsody", "Queen", "spotify:track:demo2"),
                "shakira": ("Shakira - Demo", "Shakira", "spotify:track:demo3"),
                "taylor swift": ("Taylor Swift - Demo", "Taylor Swift", "spotify:track:demo4")
            }
            for key, val in demo.items():
                if key in q.lower():
                    self.last_track = val
                    return val, None
            self.last_track = (f"{q} (Demo)", "Artista Demo", "spotify:track:demo123")
            return self.last_track, None
        try:
            r = self.sp.search(q=q, type="track", limit=1)
            items = r.get("tracks", {}).get("items", [])
            if not items:
                return None, self.t("No se encontraron resultados")
            t = items[0]
            nombre = t["name"]
            artista = ", ".join(a["name"] for a in t["artists"])
            uri = t["uri"]
            self.last_track = (nombre, artista, uri)
            return self.last_track, None
        except Exception as e:
            print("Spotify error:", e)
            self.conectado = False
            return self.buscar_cancion(q)

    def buscar_dispositivo(self):
        if not self.conectado:
            return self.t("Modo demo - La música se reproducirá en el juego")
        if not self.last_track:
            return self.t("No hay pista seleccionada")
        try:
            devices = self.sp.devices().get("devices", [])
            if not devices:
                return self.t("No hay dispositivos activos - Modo demo activado")
            dev = devices[0]["id"]
            self.sp.transfer_playback(dev, force_play=True)
            self.sp.start_playback(device_id=dev, uris=[self.last_track[2]])
            return f"✅ {self.t('Reproduciendo')} {self.last_track[0]} — {self.last_track[1]}"
        except Exception as e:
            self.conectado = False
            return f"❌ {self.t('Modo demo activado')}"

    def obtener_features(self, uri):
        if not self.conectado:
            return 120, 70
        try:
            f = self.sp.audio_features([uri])[0] or {}
            tempo = int(round(f.get("tempo", 120)))
            tr = self.sp.track(uri)
            pop = int(tr.get("popularity", 50))
            return tempo, pop
        except:
            return 120, 70

# -------------------------
# MAIN
# -------------------------
def main(username: str, lang="es"):
    pygame.init()
    info = pygame.display.Info()
    WIN_W, WIN_H = info.current_w, info.current_h
    screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.FULLSCREEN)
    pygame.display.set_caption("🎨 Personaliza tu tema")
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager((WIN_W, WIN_H))

    t = lambda k: dic_idiomas.get(lang, dic_idiomas["es"]).get(k, k)
    spotify = SpotifyClient(lang)

    center_x = WIN_W // 2
    top_y = 100

    # --- Selector de color visual ---
    map_w, map_h = 360, 240
    hs_rect = pygame.Rect(center_x - map_w//2, top_y + 40, map_w, map_h)
    hs_surf = generar_hs_surface(map_w, map_h)
    selected_color = (68,136,255)
    intensidad_idx = 1

    pygame_gui.elements.UILabel(pygame.Rect(center_x - 100, top_y - 40, 200, 30), t("Color base (HEX):"), manager)
    ent_hex = pygame_gui.elements.UITextEntryLine(pygame.Rect(center_x - 80, top_y - 5, 160, 30), manager)
    ent_hex.set_text("#4488FF")

    # --- Dropdown de intensidad ---
    pygame_gui.elements.UILabel(pygame.Rect(center_x - 150, top_y + 300, 100, 30), t("Intensidad:"), manager)
    opciones_int = ["Baja (clara)", "Media (normal)", "Alta (oscuro)"]
    dd_int = pygame_gui.elements.UIDropDownMenu(opciones_int, opciones_int[1],
                                                pygame.Rect(center_x - 20, top_y + 300, 180, 30), manager)

    # Spotify UI
    sp_y = top_y + 360
    pygame_gui.elements.UILabel(pygame.Rect(center_x - 200, sp_y, 400, 100), "Spotify — " + t("Canción") + ":", manager)
    ent_buscar = pygame_gui.elements.UITextEntryLine(pygame.Rect(center_x - 200, sp_y + 80, 200, 30), manager)
    btn_buscar = pygame_gui.elements.UIButton(pygame.Rect(center_x + 10, sp_y + 80, 100, 30), t("Buscar"), manager)
    btn_repro  = pygame_gui.elements.UIButton(pygame.Rect(center_x + 120, sp_y + 80, 120, 30), t("Reproducir"), manager)
    lbl_sp = pygame_gui.elements.UILabel(pygame.Rect(center_x - 200, sp_y + 70, 400, 24), "", manager)

    btn_aplicar = pygame_gui.elements.UIButton(pygame.Rect(center_x - 170, WIN_H - 80, 160, 40), t("Aplicar"), manager)
    btn_cancel  = pygame_gui.elements.UIButton(pygame.Rect(center_x + 10, WIN_H - 80, 160, 40), t("Cancelar"), manager)

    dragging = False
    running = True
    next_action = None  # Nueva variable para saber a dónde ir después
    while running:
        dt = clock.tick(60)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                next_action = "login"
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                next_action = "login"
                running = False


            # --- CLIC Y DRAG SOBRE MAPA DE COLOR ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hs_rect.collidepoint(event.pos):
                    dragging = True
                    # actualizar color en clic
                    x = max(0, min(map_w - 1, event.pos[0] - hs_rect.left))
                    y = max(0, min(map_h - 1, event.pos[1] - hs_rect.top))
                    hue = x / (map_w - 1)
                    sat = 1 - (y / (map_h - 1))
                    r,g,b = colorsys.hsv_to_rgb(hue, sat, 1.0)
                    selected_color = (clamp(r*255), clamp(g*255), clamp(b*255))
                    adjusted = aplicar_intensidad(selected_color, intensidad_idx)
                    ent_hex.set_text(rgb_to_hex(adjusted))
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                if hs_rect.collidepoint(event.pos):
                    x = max(0, min(map_w - 1, event.pos[0] - hs_rect.left))
                    y = max(0, min(map_h - 1, event.pos[1] - hs_rect.top))
                    hue = x / (map_w - 1)
                    sat = 1 - (y / (map_h - 1))
                    r,g,b = colorsys.hsv_to_rgb(hue, sat, 1.0)
                    selected_color = (clamp(r*255), clamp(g*255), clamp(b*255))
                    adjusted = aplicar_intensidad(selected_color, intensidad_idx)
                    ent_hex.set_text(rgb_to_hex(adjusted))

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED and event.ui_element == dd_int:
                    intensidad_idx = opciones_int.index(event.text)
                    adjusted = aplicar_intensidad(selected_color, intensidad_idx)
                    ent_hex.set_text(rgb_to_hex(adjusted))

                elif event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == btn_buscar:
                        q = ent_buscar.get_text().strip()
                        if not q:
                            lbl_sp.set_text(t("Escribe algo para buscar"))
                        else:
                            track, error = spotify.buscar_cancion(q)
                            if error:
                                lbl_sp.set_text(f"❌ {error}")
                            elif track:
                                lbl_sp.set_text(f"✅ {t('Seleccionado')}: {track[0]} — {track[1]}")
                    elif event.ui_element == btn_repro:
                        lbl_sp.set_text(spotify.buscar_dispositivo())
                    elif event.ui_element == btn_aplicar:
                        try:
                            selected_color = hex_to_rgb(ent_hex.get_text())
                        except:
                            pass
                        adjusted = aplicar_intensidad(selected_color, intensidad_idx)
                        paleta = generar_paleta(adjusted)
                        musica_uri = spotify.last_track[2] if spotify.last_track else None
                        ruta = ruta_tema_json(username)
                        os.makedirs(os.path.dirname(ruta), exist_ok=True)
                        data = {
                            "colores": {k: {"hex": rgb_to_hex(v["rgb"]), "rgb": list(v["rgb"])} for k,v in paleta.items()},
                            "musica": musica_uri
                        }
                        with open(ruta, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        marcar_personalizacion(username, paleta, musica_uri)
                        if musica_uri:
                            tempo, pop = spotify.obtener_features(musica_uri)
                            with open(ruta_datos_cancion(username), "w", encoding="utf-8") as f:
                                json.dump({"uri": musica_uri, "tempo": tempo, "popularidad": pop}, f, ensure_ascii=False, indent=2)

                        # ✅ Ir directamente a la ventana de dificultad
                        next_action = "dificultad"
                        running = False

                    elif event.ui_element == btn_cancel:
                        next_action = "login"
                        running = False

            manager.process_events(event)
        manager.update(dt)

        screen.fill(BG)
        title = pygame.font.SysFont("segoeui", 28).render(t("Personaliza tu tema"), True, TEXT_TITLE)
        screen.blit(title, (center_x - title.get_width()//2, 15))
        screen.blit(hs_surf, hs_rect)

        # Cuadro de color — bajado visualmente
        adjusted = aplicar_intensidad(selected_color, intensidad_idx)
        pygame.draw.rect(screen, adjusted, pygame.Rect(center_x - 40, top_y + 340, 80, 30))

        manager.draw_ui(screen)
        pygame.display.flip()
    pygame.quit()

    # 🔁 Abrir la ventana correspondiente según la acción
    if next_action == "dificultad":
        import dificultad
        dificultad.main(username, lang)
    elif next_action == "login":
        try:
            from form_login import PantallaLogin
            PantallaLogin(lang).run()
        except Exception:
            pass


if __name__ == "__main__":
    main("usuario_demo", lang="es")
