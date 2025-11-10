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
TEXT_BODY = (184, 184, 184)
BORDER = (32, 36, 42)

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

def aplicar_intensidad(rgb, nivel:int):
    r,g,b = rgb
    if nivel == 0:
        t = 0.35
        return (clamp(r + (255-r)*t), clamp(g + (255-g)*t), clamp(b + (255-b)*t))
    if nivel == 2:
        t = 0.35
        return (clamp(r*(1-t)), clamp(g*(1-t)), clamp(b*(1-t)))
    return (clamp(r), clamp(g), clamp(b))

def ruta_datos_cancion(username: str):
    # Guarda los features junto al tema del usuario
    from perfiles import ruta_tema_json
    ruta_tema = ruta_tema_json(username)
    base_dir = os.path.dirname(ruta_tema)
    os.makedirs(base_dir, exist_ok=True)
    return os.path.join(base_dir, "datos_cancion.json")


class EstadoTema:
    def __init__(self):
        self.h, self.s, self.v = 0.0, 0.0, 1.0
        self.intensidad_idx = 1
        self.rol_idx = 0
        # Usar solo las claves, no las etiquetas traducidas
        self.estilos = {
            "fondo": {"h":0.0,"s":0.0,"v":1.0,"int":1,"rgb":(20, 22, 26)},
            "texto": {"h":0.0,"s":0.0,"v":1.0,"int":1,"rgb":(245, 245, 245)},
            "ventana": {"h":0.0,"s":0.0,"v":1.0,"int":1,"rgb":(34, 38, 44)},
            "btn_primario": {"h":0.0,"s":0.0,"v":1.0,"int":1,"rgb":(180, 68, 68)},
            "btn_secundario": {"h":0.0,"s":0.0,"v":1.0,"int":1,"rgb":(68, 68, 76)}
        }

    def color_base_rgb(self):
        r,g,b = colorsys.hsv_to_rgb(self.h, self.s, self.v)
        return (clamp(r*255), clamp(g*255), clamp(b*255))

    def guardar_en_rol(self, final_rgb):
        # Obtener la clave del rol actual
        claves = ["fondo", "texto", "ventana", "btn_primario", "btn_secundario"]
        k = claves[self.rol_idx]
        self.estilos[k].update({"h":self.h,"s":self.s,"v":self.v,"int":self.intensidad_idx,"rgb":final_rgb})

    def cargar_rol_en_picker(self):
        claves = ["fondo", "texto", "ventana", "btn_primario", "btn_secundario"]
        k = claves[self.rol_idx]
        st = self.estilos[k]
        self.h, self.s, self.v = st.get("h",0.0), st.get("s",0.0), st.get("v",1.0)
        self.intensidad_idx = st.get("int",1)

    def aplicar_archivo(self, ruta=None, musica=None):
        if ruta is None:
            from Clases_auxiliares.config import RUTA_TEMA
            ruta = RUTA_TEMA
        
        data = {
            "colores": {
                k: {"hex": rgb_to_hex(v["rgb"]), "rgb": list(v["rgb"]), "intensidad": v.get("int",1)}
                for k, v in self.estilos.items()
            },
            "musica": musica
        }
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Tema guardado en:", ruta)

def generar_hs_surface(w, h):
    surf = pygame.Surface((w, h))
    px = pygame.PixelArray(surf)
    for x in range(w):
        hue = x / (w-1) if w > 1 else 0
        for y in range(h):
            sat = 1 - (y / (h-1) if h > 1 else 0)
            r,g,b = colorsys.hsv_to_rgb(hue, sat, 1.0)
            px[x, y] = (clamp(r*255), clamp(g*255), clamp(b*255))
    del px
    return surf.convert()

def generar_v_surface(w, h, hue, sat):
    surf = pygame.Surface((w, h))
    for y in range(h):
        v = 1 - (y/(h-1) if h > 1 else 0)
        r,g,b = colorsys.hsv_to_rgb(hue, sat, v)
        pygame.draw.line(surf, (clamp(r*255), clamp(g*255), clamp(b*255)), (0, y), (w-1, y))
    return surf.convert()

def _set_dropdown_value(dd, value):
    try:
        dd.set_selected_option(value)
    except Exception:
        try:
            dd.selected_option = value
            dd.rebuild()
        except Exception:
            pass

class SpotifyClient:
    def __init__(self, lang="es"):
        self.lang = lang
        self.sp = None
        self.last_track = None
        self.conectado = False
        self._inicializar_spotify()

    def _inicializar_spotify(self):
        """Intenta inicializar Spotify, si falla, funciona en modo demo"""
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id="37141bd00fde487fb1dbf3b8d2fdf6f4",
                client_secret="87a87eb30ee5418f9f07c0c1800e0905",
                redirect_uri="http://127.0.0.1:8888/callback",
                scope="user-modify-playback-state user-read-playback-state"
            ))
            # Verificar que funciona haciendo una búsqueda de prueba
            test_result = self.sp.search(q='test', type='track', limit=1)
            print("✅ Spotify conectado correctamente")
            self.conectado = True
        except Exception as e:
            print(f"❌ Spotify no disponible: {e}")
            print("🔶 Funcionando en modo demo")
            self.conectado = False

    def t(self, key):
        return dic_idiomas.get(self.lang, dic_idiomas["es"]).get(key, key)

    def buscar_cancion(self, cancion: str):
        """Retorna (track, error) donde track = (nombre, artista, uri) o None"""
        if not self.conectado:
            # Modo demo - simular búsqueda
            canciones_demo = {
                "bad bunny": ("Bad Bunny - Demo", "Artista Demo", "spotify:track:demo1"),
                "queen": ("Queen - Bohemian Rhapsody", "Queen", "spotify:track:demo2"),
                "shakira": ("Shakira - Demo", "Shakira", "spotify:track:demo3"),
                "taylor swift": ("Taylor Swift - Demo", "Taylor Swift", "spotify:track:demo4")
            }
            
            cancion_lower = cancion.lower()
            for key, track in canciones_demo.items():
                if key in cancion_lower:
                    self.last_track = track
                    return track, None  # Retorna track y None (sin error)
            
            # Si no encuentra coincidencia, crear una demo genérica
            self.last_track = (f"{cancion} (Demo)", "Artista Demo", "spotify:track:demo123")
            return self.last_track, None
        
        # Si está conectado, usar Spotify real
        try:
            resultados = self.sp.search(q=cancion, type="track", limit=1)
            items = resultados.get("tracks", {}).get("items", [])
            if not items:
                return None, self.t("No se encontraron resultados")
            
            t = items[0]
            nombre = t["name"]
            artista = ", ".join(a["name"] for a in t["artists"])
            uri = t["uri"]
            self.last_track = (nombre, artista, uri)
            return self.last_track, None
            
        except Exception as e:
            error_msg = f"Error de Spotify: {str(e)}"
            print(f"❌ {error_msg}")
            # Fallback a modo demo
            self.conectado = False
            return self.buscar_cancion(cancion)  # Llamada recursiva en modo demo

    def buscar_dispositivo(self):
        if not self.conectado:
            return self.t("Modo demo - La música se reproducirá en el juego")
        
        if not self.last_track:
            return self.t("No hay pista seleccionada")
        
        try:
            devices = self.sp.devices().get("devices", [])
            if not devices:
                return self.t("No hay dispositivos activos - Modo demo activado")
            
            device_id = devices[0]["id"]
            try:
                self.sp.transfer_playback(device_id, force_play=True)
            except:
                pass
            
            self.sp.start_playback(device_id=device_id, uris=[self.last_track[2]])
            return f"✅ {self.t('Reproduciendo')} {self.last_track[0]} — {self.last_track[1]}"
            
        except Exception as e:
            error_msg = f"{self.t('No se pudo reproducir')}: {str(e)}"
            print(f"❌ {error_msg}")
            # Fallback a modo demo
            self.conectado = False
            return self.t("Modo demo activado - Música en juego")

    def obtener_features(self, uri: str):
        if not self.conectado:
            # Valores por defecto para demo
            return 120, 70  # tempo, popularidad
        
        try:
            feats = self.sp.audio_features([uri])[0] or {}
            tempo = int(round(feats.get("tempo", 120)))
            tr = self.sp.track(uri) or {}
            popularidad = int(tr.get("popularity", 50))
            return tempo, popularidad
        except:
            return 120, 70  # Fallback


def main(username: str, lang: str = "es"):

    import os
    import pygame
    import pygame_gui
    import colorsys
    from perfiles import marcar_personalizacion, ruta_tema_json
    from Traductor import dic_idiomas
    
    print(f"🎯 DEBUG personalización: Idioma recibido = '{lang}'")
    pygame.init()

    # Función de traducción usando el sistema centralizado
    def t(key):
        traduccion = dic_idiomas.get(lang, dic_idiomas["es"]).get(key, key)
        return traduccion

    # Traducir roles dinámicamente DENTRO de la función main
    ROLES_KEYS = [
        ("fondo",         "Fondo de la app"),
        ("texto",         "Texto principal"), 
        ("ventana",       "Tarjetas / Ventanas"),
        ("btn_primario",  "Botón primario"),
        ("btn_secundario","Botón secundario"),
    ]
    INT_ETIQUETAS_KEYS = ["Baja (clara)", "Media (normal)", "Alta (oscuro)"]

    roles_traducidos = [
        (key, t(label_key)) for key, label_key in ROLES_KEYS
    ]
    int_etiquetas_traducidas = [t(key) for key in INT_ETIQUETAS_KEYS]

    print(f"🎯 Roles traducidos: {roles_traducidos}")
    print(f"🎯 Intensidades traducidas: {int_etiquetas_traducidas}")

    # Dimensiones de pantalla (pantalla completa)
    info = pygame.display.Info()
    WIN_W = info.current_w
    WIN_H = info.current_h

    pygame.display.set_caption(t("Personalización"))
    screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager((WIN_W, WIN_H))

    # --- Estado del tema / helpers de UI ---
    state = EstadoTema()

    # Layout básico
    margin = 24
    center_x = WIN_W // 2
    top_y = 90

    # Panel izquierdo: mapa HS (tono/saturación) + barra V (valor)
    map_w, map_h = 360, 240
    bar_w, bar_h = 32, map_h

    hs_rect = pygame.Rect(center_x - map_w - 40, top_y + 30, map_w, map_h)
    v_rect = pygame.Rect(hs_rect.right + 10, hs_rect.top, bar_w, bar_h)

    # Panel derecho: controles, entradas y Spotify
    right_x = center_x + 40
    controls_w = min(520, WIN_W - right_x - margin)

    # Campos de texto HEX y RGB
    ent_hex = pygame_gui.elements.UITextEntryLine(pygame.Rect(right_x, top_y + 80, 160, 30), manager)
    ent_r   = pygame_gui.elements.UITextEntryLine(pygame.Rect(right_x, top_y + 120, 50, 30), manager)
    ent_g   = pygame_gui.elements.UITextEntryLine(pygame.Rect(right_x + 60, top_y + 120, 50, 30), manager)
    ent_b   = pygame_gui.elements.UITextEntryLine(pygame.Rect(right_x + 120, top_y + 120, 50, 30), manager)

    # Labels para las entradas
    pygame_gui.elements.UILabel(pygame.Rect(right_x, top_y + 52, 160, 20), "HEX", manager)
    pygame_gui.elements.UILabel(pygame.Rect(right_x, top_y + 152, 160, 20), "RGB (0-255)", manager)

    # Dropdown de Rol (elemento) e Intensidad (TRADUCIDOS)
    pygame_gui.elements.UILabel(pygame.Rect(right_x, top_y - 28, 90, 24), t("Elemento") + ":", manager)
    dd_roles = pygame_gui.elements.UIDropDownMenu(
        [etq for (_k, etq) in roles_traducidos], roles_traducidos[0][1], pygame.Rect(right_x + 90, top_y - 32, 220, 30), manager
    )

    pygame_gui.elements.UILabel(pygame.Rect(right_x, top_y + 8, 90, 24), t("Intensidad") + ":", manager)
    dd_int = pygame_gui.elements.UIDropDownMenu(
        int_etiquetas_traducidas, int_etiquetas_traducidas[1], pygame.Rect(right_x + 90, top_y + 4, 140, 30), manager
    )

    # Bloque de Spotify (buscar/reproducir) - TRADUCIDO
    sp_y = top_y + 200
    pygame_gui.elements.UILabel(pygame.Rect(right_x, sp_y, 180, 24), "Spotify — " + t("Canción") + ":", manager)
    ent_buscar = pygame_gui.elements.UITextEntryLine(pygame.Rect(right_x, sp_y + 28, controls_w - 250, 30), manager)
    btn_buscar = pygame_gui.elements.UIButton(pygame.Rect(ent_buscar.rect.right + 10, sp_y + 28, 100, 30), t("Buscar"), manager)
    btn_repro  = pygame_gui.elements.UIButton(pygame.Rect(btn_buscar.rect.right + 10, sp_y + 28, 120, 30), t("Conectar/Repro"), manager)
    lbl_sp     = pygame_gui.elements.UILabel(pygame.Rect(right_x, sp_y + 68, controls_w, 24), "", manager)

    # Botones inferiores (TRADUCIDOS)
    btn_aplicar = pygame_gui.elements.UIButton(pygame.Rect(center_x - 170, WIN_H - 80, 160, 40), t("Aplicar"), manager)
    btn_cancel  = pygame_gui.elements.UIButton(pygame.Rect(center_x + 10,  WIN_H - 80, 160, 40), t("Cancelar"), manager)

    # Vista previa (demo) - TRADUCIDA
    demo_root_rect = pygame.Rect(center_x - 360, top_y + 300, 720, 200)
    demo_card_rect = pygame.Rect(demo_root_rect.x + 20, demo_root_rect.y + 20, demo_root_rect.w - 40, 120)
    demo_btn_y     = demo_card_rect.y + demo_card_rect.h - 48
    demo_btn1_rect = pygame.Rect(demo_card_rect.x + 10, demo_btn_y, 120, 34)
    demo_btn2_rect = pygame.Rect(demo_card_rect.x + 10 + 126, demo_btn_y, 120, 34)

    # Superficies de selección de color
    hs_surf = generar_hs_surface(map_w, map_h)
    v_surf  = generar_v_surface(bar_w, bar_h, state.h, state.s)
    dragging_hs = False
    dragging_v  = False

    # Spotify client (con idioma)
    spotify = SpotifyClient(lang)

    # --- Helpers internos ---

    def _update_v_bar():
        nonlocal v_surf
        v_surf = generar_v_surface(bar_w, bar_h, state.h, state.s)

    def _update_entries_from_state():
        base = state.color_base_rgb()
        ent_hex.set_text(rgb_to_hex(base))
        ent_r.set_text(str(base[0])); ent_g.set_text(str(base[1])); ent_b.set_text(str(base[2]))
        _set_dropdown_value(dd_int,  int_etiquetas_traducidas[state.intensidad_idx])
        _set_dropdown_value(dd_roles, roles_traducidos[state.rol_idx][1])

    def _apply_intensity_and_persist():
        base = state.color_base_rgb()
        state.guardar_en_rol(final_rgb=base)

    def _load_role_and_refresh():
        # Cargar HSV base del rol actual en los sliders/campos
        claves = ["fondo", "texto", "ventana", "btn_primario", "btn_secundario"]
        k = claves[state.rol_idx]
        d = state.estilos[k]
        state.h = d.get("h", state.h)
        state.s = d.get("s", state.s)
        state.v = d.get("v", state.v)
        _update_v_bar()
        _update_entries_from_state()

    # Cargar el rol actual al inicio
    _load_role_and_refresh()

    running = True
    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            # Cerrar ventana
            if event.type == pygame.QUIT:
                running = False

            # Presionar botones y UI de pygame_gui
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == btn_aplicar:
                        from perfiles import marcar_personalizacion, ruta_tema_json
                        # 1) Validar canción seleccionada la primera vez
                        primera_vez = not os.path.exists(ruta_tema_json(username))
                        if primera_vez and not spotify.last_track:
                            lbl_sp.set_text(t("Debes elegir una canción antes de aplicar"))
                            continue  # no cerrar

                        # Verificar que last_track tenga el formato correcto
                        if spotify.last_track and len(spotify.last_track) >= 3:
                            musica_uri = spotify.last_track[2]
                        else:
                            musica_uri = None
                            print("⚠️ No hay canción seleccionada válida")
                        ruta = ruta_tema_json(username)
                        os.makedirs(os.path.dirname(ruta), exist_ok=True)
                        state.aplicar_archivo(ruta, musica=musica_uri)

                        # 2) Guardar tema en perfiles
                        tema_dict = {
                            k: {
                                "hex": rgb_to_hex(v["rgb"]),
                                "rgb": list(v["rgb"]),
                                "intensidad": v.get("int", 1)
                            }
                            for k, v in state.estilos.items()
                        }
                        marcar_personalizacion(username, tema_dict, musica_uri)

                        # 3) Guardar features de la canción para el puntaje
                        if musica_uri:
                            tempo, popularidad = spotify.obtener_features(musica_uri)
                            with open(ruta_datos_cancion(username), "w", encoding="utf-8") as f:
                                json.dump({"uri": musica_uri, "tempo": tempo, "popularidad": popularidad}, f, ensure_ascii=False, indent=2)

                        running = False
                        pygame.quit()

                        import dificultad
                        dificultad_seleccionada = dificultad.main(username, lang)

                    elif event.ui_element == btn_cancel:
                        running = False

                    elif event.ui_element == btn_buscar:
                        q = ent_buscar.get_text().strip()
                        if not q:
                            lbl_sp.set_text(t("Escribe algo para buscar"))
                        else:
                            # Ahora buscar_cancion retorna (track, error)
                            track, error = spotify.buscar_cancion(q)
                            if error:
                                lbl_sp.set_text(f"❌ {error}")
                            elif track is None:
                                lbl_sp.set_text(t("No encontré resultados"))
                            else:
                                nombre, artista, _ = track
                                lbl_sp.set_text(f"✅ {t('Seleccionado')}: {nombre} — {artista}")

                    elif event.ui_element == btn_repro:
                        msg = spotify.buscar_dispositivo()
                        lbl_sp.set_text(msg)

                elif event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == dd_roles:
                        etiqueta = event.text
                        for i, (_k, etq) in enumerate(roles_traducidos):
                            if etq == etiqueta:
                                state.rol_idx = i
                                break
                        _load_role_and_refresh()

                    elif event.ui_element == dd_int:
                        state.intensidad_idx = int_etiquetas_traducidas.index(event.text)
                        _apply_intensity_and_persist()
                        _update_entries_from_state()

                elif event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == ent_hex:
                        txt = ent_hex.get_text().strip()
                        try:
                            r, g, b = hex_to_rgb(txt)
                            rr, gg, bb = [c/255 for c in (r, g, b)]
                            h, s, v = colorsys.rgb_to_hsv(rr, gg, bb)
                            state.h, state.s, state.v = h, s, v
                            _update_v_bar()
                            _apply_intensity_and_persist()
                            _update_entries_from_state()
                        except Exception:
                            pass
                    elif event.ui_element in (ent_r, ent_g, ent_b):
                        try:
                            r = clamp(int(ent_r.get_text()))
                            g = clamp(int(ent_g.get_text()))
                            b = clamp(int(ent_b.get_text()))
                            rr, gg, bb = [c/255 for c in (r, g, b)]
                            h, s, v = colorsys.rgb_to_hsv(rr, gg, bb)
                            state.h, state.s, state.v = h, s, v
                            _update_v_bar()
                            _apply_intensity_and_persist()
                            _update_entries_from_state()
                        except Exception:
                            pass

            # Entrada de teclado / ratón (fuera de pygame_gui)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hs_rect.collidepoint(event.pos):
                    dragging_hs = True
                    x = event.pos[0] - hs_rect.left
                    y = event.pos[1] - hs_rect.top
                    state.h = max(0, min(1, x / (map_w - 1)))
                    state.s = max(0, min(1, 1 - (y / (map_h - 1))))
                    _update_v_bar()
                    _apply_intensity_and_persist()
                    _update_entries_from_state()
                elif v_rect.collidepoint(event.pos):
                    dragging_v = True
                    y = event.pos[1] - v_rect.top
                    state.v = max(0, min(1, 1 - (y / (bar_h - 1))))
                    _apply_intensity_and_persist()
                    _update_entries_from_state()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_hs = False
                dragging_v = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging_hs:
                    x = max(0, min(map_w - 1, event.pos[0] - hs_rect.left))
                    y = max(0, min(map_h - 1, event.pos[1] - hs_rect.top))
                    state.h = x / (map_w - 1)
                    state.s = 1 - (y / (map_h - 1))
                    _update_v_bar()
                    _apply_intensity_and_persist()
                    _update_entries_from_state()
                elif dragging_v:
                    y = max(0, min(bar_h - 1, event.pos[1] - v_rect.top))
                    state.v = 1 - (y / (bar_h - 1))
                    _apply_intensity_and_persist()
                    _update_entries_from_state()

            manager.process_events(event)

        # Actualizar UI y dibujar
        manager.update(time_delta)

        # Fondo
        screen.fill(BG)

        # Títulos (TRADUCIDOS)
        title = pygame.font.SysFont("segoeui", 26).render(t("Personaliza tu tema"), True, TEXT_TITLE)
        screen.blit(title, (center_x - title.get_width() // 2, 24))

        # Dibujar mapa HS y barra V
        screen.blit(hs_surf, hs_rect)
        screen.blit(v_surf, v_rect)

        # Cursor/indicadores en HS/V
        base = state.color_base_rgb()
        hs_x = int(state.h * (map_w - 1)) + hs_rect.left
        hs_y = int((1 - state.s) * (map_h - 1)) + hs_rect.top
        pygame.draw.circle(screen, (255, 255, 255), (hs_x, hs_y), 6, 2)

        v_y = int((1 - state.v) * (bar_h - 1)) + v_rect.top
        pygame.draw.rect(screen, (255, 255, 255), (v_rect.left - 2, v_y - 3, bar_w + 4, 6), 2)

        # Demo preview con los estilos actuales (TRADUCIDO)
        col_fondo = state.estilos["fondo"]["rgb"]
        col_vent  = state.estilos["ventana"]["rgb"]
        col_texto = state.estilos["texto"]["rgb"]
        col_btn_p = state.estilos["btn_primario"]["rgb"]
        col_btn_s = state.estilos["btn_secundario"]["rgb"]

        pygame.draw.rect(screen, BORDER, demo_root_rect, 1, border_radius=8)
        pygame.draw.rect(screen, col_fondo, demo_root_rect, border_radius=8)
        pygame.draw.rect(screen, col_vent, demo_card_rect, border_radius=10)

        subtitle = pygame.font.SysFont("segoeui", 14).render(t("Tarjeta de ejemplo"), True, col_texto)
        screen.blit(subtitle, (demo_card_rect.x + 10, demo_card_rect.y + 10))

        pygame.draw.rect(screen, col_btn_p, demo_btn1_rect, border_radius=6)
        pygame.draw.rect(screen, (int(col_btn_p[0]*0.8), int(col_btn_p[1]*0.8), int(col_btn_p[2]*0.8)), demo_btn1_rect, 1, border_radius=6)

        l1 = 0.2126*col_btn_p[0] + 0.7152*col_btn_p[1] + 0.0722*col_btn_p[2]
        txt1_color = (20, 22, 26) if l1 > 140 else (245, 245, 245)
        txt1 = pygame.font.SysFont("segoeui", 14).render(t("Primario"), True, txt1_color)
        screen.blit(txt1, txt1.get_rect(center=demo_btn1_rect.center))

        pygame.draw.rect(screen, col_btn_s, demo_btn2_rect, border_radius=6)
        pygame.draw.rect(screen, (int(col_btn_s[0]*0.8), int(col_btn_s[1]*0.8), int(col_btn_s[2]*0.8)), demo_btn2_rect, 1, border_radius=6)

        l2 = 0.2126*col_btn_s[0] + 0.7152*col_btn_s[1] + 0.0722*col_btn_s[2]
        txt2_color = (20, 22, 26) if l2 > 140 else (245, 245, 245)
        txt2 = pygame.font.SysFont("segoeui", 14).render(t("Secundario"), True, txt2_color)
        screen.blit(txt2, txt2.get_rect(center=demo_btn2_rect.center))

        # Indicador inferior (TRADUCIDO)
        exit_text = pygame.font.SysFont("segoeui", 12).render(t("Presiona ESC para salir | F11 pantalla completa"), True, TEXT_BODY)
        screen.blit(exit_text, (center_x - exit_text.get_width() // 2, WIN_H - 30))

        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()

