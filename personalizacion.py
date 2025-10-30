import pygame
import pygame_gui
import colorsys
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

from perfiles import marcar_personalizacion, ruta_tema_json

BG = (20, 22, 26)
TEXT_TITLE = (245, 245, 245)
TEXT_BODY = (184, 184, 184)
BORDER = (32, 36, 42)

ROLES = [
    ("fondo",           "Fondo de la app"),
    ("texto",           "Texto principal"),
    ("texto_secundario","Texto de botones / secundario"),
    ("ventana",         "Tarjetas / Ventanas"),
    ("btn_primario",    "Botón primario"),
    ("btn_secundario",  "Botón secundario"),
]
INT_ETIQUETAS = ["Baja (clara)", "Media (normal)", "Alta (oscuro)"]
VENTANAS = ["Game Over", "Win"]


def clamp(x, a=0, b=255):
    try:
        return max(a, min(b, int(x)))
    except Exception:
        return a

def clamp01(x):
    return 0.0 if x < 0.0 else (1.0 if x > 1.0 else x)

def rgb_to_hex(rgb):
    r,g,b = rgb
    return "#{:02X}{:02X}{:02X}".format(clamp(r), clamp(g), clamp(b))

def hex_to_rgb(hexstr):
    s = hexstr.strip().lstrip("#")
    if len(s) == 3:
        s = "".join([c*2 for c in s])
    if len(s) != 6:
        raise ValueError("HEX inválido")
    return tuple(int(s[i:i+2], 16) for i in (0,2,4))

def aplicar_intensidad(rgb, nivel:int):
    r,g,b = rgb
    if nivel == 0:  # Baja (aclara)
        t = 0.35
        return (clamp(r + (255-r)*t), clamp(g + (255-g)*t), clamp(b + (255-b)*t))
    if nivel == 2:  # Alta (oscurece)
        t = 0.35
        return (clamp(r*(1-t)), clamp(g*(1-t)), clamp(b*(1-t)))
    return (clamp(r), clamp(g), clamp(b))

def _color_con_intensidad(state, key):
    e = state.estilos[key]
    return aplicar_intensidad(e["rgb"], e.get("int", 1))


class EstadoTema:
    def __init__(self):
        self.h, self.s, self.v = 0.0, 0.0, 1.0
        self.intensidad_idx = 1
        self.rol_idx = 0
        self.estilos = {k: {"h":0.0,"s":0.0,"v":1.0,"int":1,"rgb":(255,255,255)} for k,_ in ROLES}
        # valores por defecto
        self.estilos["fondo"]["rgb"]            = (20, 22, 26)
        self.estilos["texto"]["rgb"]            = (245, 245, 245)
        self.estilos["texto_secundario"]["rgb"] = (210, 210, 210)
        self.estilos["ventana"]["rgb"]          = (34, 38, 44)
        self.estilos["btn_primario"]["rgb"]     = (180, 68, 68)
        self.estilos["btn_secundario"]["rgb"]   = (68, 68, 76)

    def color_base_rgb(self):
        r,g,b = colorsys.hsv_to_rgb(self.h, self.s, self.v)
        return (clamp(r*255), clamp(g*255), clamp(b*255))

    def guardar_en_rol(self, final_rgb):
        k = ROLES[self.rol_idx][0]
        self.estilos[k].update({
            "h": self.h, "s": self.s, "v": self.v,
            "int": self.intensidad_idx,
            "rgb": final_rgb
        })

    def cargar_rol_en_picker(self):
        k = ROLES[self.rol_idx][0]
        st = self.estilos[k]
        self.h, self.s, self.v = st.get("h",0.0), st.get("s",0.0), st.get("v",1.0)
        self.intensidad_idx = st.get("int",1)

    def aplicar_archivo(self, ruta="tema.json", musica=None):
        data = {
            "colores": {
                k: {"hex": rgb_to_hex(v["rgb"]), "rgb": list(v["rgb"]), "intensidad": v.get("int",1)}
                for k, v in self.estilos.items()
            },
            "musica": musica
        }
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Tema guardado:", data)


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


# ---- VISTAS PREVIAS ------------------------------------------------
def draw_preview_gameover(screen, state, rect):
    col_fondo = _color_con_intensidad(state, "fondo")
    col_vent  = _color_con_intensidad(state, "ventana")
    col_texto = _color_con_intensidad(state, "texto")
    col_texto_sec = _color_con_intensidad(state, "texto_secundario")
    col_btn_p = _color_con_intensidad(state, "btn_primario")
    col_btn_s = _color_con_intensidad(state, "btn_secundario")

    pygame.draw.rect(screen, col_fondo, rect, border_radius=8)
    inner = rect.inflate(-100, -60)
    pygame.draw.rect(screen, col_vent, inner, border_radius=12)

    font_titulo = pygame.font.SysFont("segoeui", 36, bold=True)
    titulo = font_titulo.render("¡Game Over!", True, col_texto)
    screen.blit(titulo, (inner.centerx - titulo.get_width()//2, inner.y + 40))

    font_body = pygame.font.SysFont("segoeui", 22)
    msg = font_body.render("Has perdido. Intenta de nuevo.", True, col_texto)
    screen.blit(msg, (inner.centerx - msg.get_width()//2, inner.y + 100))

    btn1 = pygame.Rect(inner.centerx - 160, inner.bottom - 80, 130, 40)
    btn2 = pygame.Rect(inner.centerx + 30, inner.bottom - 80, 180, 40)
    pygame.draw.rect(screen, col_btn_p, btn1, border_radius=8)
    pygame.draw.rect(screen, col_btn_s, btn2, border_radius=8)

    font_btn = pygame.font.SysFont("segoeui", 18)
    screen.blit(font_btn.render("Reintentar", True, col_texto_sec), btn1.move(22, 10))
    screen.blit(font_btn.render("Menú principal", True, col_texto_sec), btn2.move(15, 10))


def draw_preview_win(screen, state, rect):
    col_fondo = _color_con_intensidad(state, "fondo")
    col_vent  = _color_con_intensidad(state, "ventana")
    col_texto = _color_con_intensidad(state, "texto")
    col_texto_sec = _color_con_intensidad(state, "texto_secundario")
    col_btn_p = _color_con_intensidad(state, "btn_primario")

    pygame.draw.rect(screen, col_fondo, rect, border_radius=8)
    inner = rect.inflate(-100, -60)
    pygame.draw.rect(screen, col_vent, inner, border_radius=12)

    font_titulo = pygame.font.SysFont("segoeui", 36, bold=True)
    titulo = font_titulo.render("¡Victoria!", True, col_texto)
    screen.blit(titulo, (inner.centerx - titulo.get_width()//2, inner.y + 50))

    font_body = pygame.font.SysFont("segoeui", 22)
    msg = font_body.render("¡Has ganado el juego!", True, col_texto)
    screen.blit(msg, (inner.centerx - msg.get_width()//2, inner.y + 110))

    btn = pygame.Rect(inner.centerx - 80, inner.bottom - 80, 160, 40)
    pygame.draw.rect(screen, col_btn_p, btn, border_radius=8)

    font_btn = pygame.font.SysFont("segoeui", 18)
    screen.blit(font_btn.render("Continuar", True, col_texto_sec), btn.move(30, 10))


# ---- Spotify (credenciales por entorno) ----------------------------
class SpotifyClient:
    def __init__(self):
        self.sp = None
        self.last_track = None

    def _ensure(self):
        if self.sp is None:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIPY_CLIENT_ID", "37141bd00fde487fb1dbf3b8d2fdf6f4"),
                client_secret=os.getenv("SPOTIPY_CLIENT_SECRET", "87a87eb30ee5418f9f07c0c1800e0905"),
                redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback"),
                scope="user-modify-playback-state user-read-playback-state"
            ))

    def buscar_cancion(self, cancion: str):
        self._ensure()
        resultados = self.sp.search(q=cancion, type="track", limit=1)
        items = resultados.get("tracks", {}).get("items", [])
        if not items:
            return None
        t = items[0]
        nombre = t["name"]
        artista = ", ".join(a["name"] for a in t["artists"])
        uri = t["uri"]
        self.last_track = (nombre, artista, uri)
        return self.last_track

    def buscar_dispositivo(self):
        self._ensure()
        if not self.last_track:
            return "No hay pista seleccionada."
        devices = self.sp.devices().get("devices", [])
        if not devices:
            return "No hay dispositivos activos o no es Premium."
        device_id = devices[0]["id"]
        try:
            self.sp.transfer_playback(device_id, force_play=True)
        except Exception:
            pass
        try:
            self.sp.start_playback(device_id=device_id, uris=[self.last_track[2]])
            return f"Reproduciendo {self.last_track[0]} — {self.last_track[1]}"
        except Exception as e:
            return f"No se pudo reproducir: {e}"

# -------------------------------------------------------------------
def main(username: str):
    pygame.init()
    info = pygame.display.Info()
    WIN_W = max(1024, info.current_w)
    WIN_H = max(700, info.current_h)

    pygame.display.set_caption("Personalización")
    screen_flags = pygame.FULLSCREEN  # puedes cambiar a 0 si prefieres arrancar en ventana
    screen = pygame.display.set_mode((WIN_W, WIN_H), screen_flags)
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager((WIN_W, WIN_H))

    state = EstadoTema()
    margin = 24
    center_x = WIN_W // 2
    top_y = 90

    map_w, map_h = 360, 240
    bar_w, bar_h = 32, map_h
    hs_rect = pygame.Rect(center_x - map_w - 40, top_y + 30, map_w, map_h)
    v_rect  = pygame.Rect(hs_rect.right + 10, hs_rect.top, bar_w, bar_h)

    right_x = center_x + 40
    controls_w = min(520, WIN_W - right_x - margin)

    ent_hex = pygame_gui.elements.UITextEntryLine(pygame.Rect(right_x, top_y + 80, 160, 30), manager)
    ent_r   = pygame_gui.elements.UITextEntryLine(pygame.Rect(right_x, top_y + 120, 50, 30), manager)
    ent_g   = pygame_gui.elements.UITextEntryLine(pygame.Rect(right_x + 60, top_y + 120, 50, 30), manager)
    ent_b   = pygame_gui.elements.UITextEntryLine(pygame.Rect(right_x + 120, top_y + 120, 50, 30), manager)

    pygame_gui.elements.UILabel(pygame.Rect(right_x, top_y + 52, 160, 20), "HEX", manager)
    pygame_gui.elements.UILabel(pygame.Rect(right_x, top_y + 152, 160, 20), "RGB (0-255)", manager)

    pygame_gui.elements.UILabel(pygame.Rect(right_x, top_y - 28, 90, 24), "Elemento:", manager)
    dd_roles = pygame_gui.elements.UIDropDownMenu(
        [etq for (_k, etq) in ROLES], ROLES[0][1], pygame.Rect(right_x + 90, top_y - 32, 220, 30), manager
    )

    pygame_gui.elements.UILabel(pygame.Rect(right_x, top_y + 8, 90, 24), "Intensidad:", manager)
    dd_int = pygame_gui.elements.UIDropDownMenu(
        INT_ETIQUETAS, INT_ETIQUETAS[1], pygame.Rect(right_x + 90, top_y + 4, 140, 30), manager
    )

    pygame_gui.elements.UILabel(pygame.Rect(right_x, top_y + 180, 140, 24), "Vista previa:", manager)
    dd_vista = pygame_gui.elements.UIDropDownMenu(
        VENTANAS, VENTANAS[0], pygame.Rect(right_x + 130, top_y + 176, 160, 30), manager
    )
    vista_actual = VENTANAS[0]

    # Spotify
    sp_y = top_y + 230
    pygame_gui.elements.UILabel(pygame.Rect(right_x, sp_y, 180, 24), "Spotify — Canción:", manager)
    ent_buscar = pygame_gui.elements.UITextEntryLine(pygame.Rect(right_x, sp_y + 28, controls_w - 250, 30), manager)
    btn_buscar = pygame_gui.elements.UIButton(pygame.Rect(ent_buscar.rect.right + 10, sp_y + 28, 100, 30), "Buscar", manager)
    btn_repro  = pygame_gui.elements.UIButton(pygame.Rect(btn_buscar.rect.right + 10, sp_y + 28, 120, 30), "Conectar/Repro", manager)
    lbl_sp     = pygame_gui.elements.UILabel(pygame.Rect(right_x, sp_y + 68, controls_w, 24), "", manager)

    btn_aplicar = pygame_gui.elements.UIButton(pygame.Rect(center_x - 170, WIN_H - 80, 160, 40), "Aplicar", manager)
    btn_cancel  = pygame_gui.elements.UIButton(pygame.Rect(center_x + 10,  WIN_H - 80, 160, 40), "Cancelar", manager)

    hs_surf = generar_hs_surface(map_w, map_h)
    v_surf  = generar_v_surface(bar_w, bar_h, state.h, state.s)
    dragging_hs = False
    dragging_v  = False
    spotify = SpotifyClient()

    def _update_v_bar():
        nonlocal v_surf
        v_surf = generar_v_surface(bar_w, bar_h, state.h, state.s)

    def _update_entries_from_state():
        base = state.color_base_rgb()
        ent_hex.set_text(rgb_to_hex(base))
        ent_r.set_text(str(base[0])); ent_g.set_text(str(base[1])); ent_b.set_text(str(base[2]))
        _set_dropdown_value(dd_int,  INT_ETIQUETAS[state.intensidad_idx])
        _set_dropdown_value(dd_roles, ROLES[state.rol_idx][1])

    def _guardar_color_en_rol_actual():
        base = state.color_base_rgb()
        state.guardar_en_rol(final_rgb=base)

    def _load_role_and_refresh():
        state.cargar_rol_en_picker()
        _update_v_bar()
        _update_entries_from_state()

    def _set_hs_from_pos(mx, my):
        # Convertir posición a H y S
        hx = (mx - hs_rect.left) / (map_w - 1)
        sy = 1 - ((my - hs_rect.top) / (map_h - 1))
        state.h = clamp01(hx)
        state.s = clamp01(sy)
        _update_v_bar()
        _update_entries_from_state()

    def _set_v_from_pos(my):
        v = 1 - ((my - v_rect.top) / (bar_h - 1))
        state.v = clamp01(v)
        _update_entries_from_state()

    def _rgb_entries_to_state():
        try:
            r = int(ent_r.get_text())
            g = int(ent_g.get_text())
            b = int(ent_b.get_text())
            r, g, b = clamp(r), clamp(g), clamp(b)
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            state.h, state.s, state.v = h, s, v
            _update_v_bar()
        except Exception:
            pass  # ignorar entradas inválidas

    def _hex_entry_to_state():
        try:
            r,g,b = hex_to_rgb(ent_hex.get_text())
            h, s, v = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            state.h, state.s, state.v = h, s, v
            _update_v_bar()
            _update_entries_from_state()
        except Exception:
            pass

    _update_entries_from_state()
    _load_role_and_refresh()

    running = True
    fullscreen = True

    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            # ---- Salida / modo pantalla ----
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    pygame.display.quit()
                    pygame.display.init()
                    flags = pygame.FULLSCREEN if fullscreen else 0
                    screen = pygame.display.set_mode((WIN_W, WIN_H), flags)

            # ---- Ratón para HS y V ----
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hs_rect.collidepoint(event.pos):
                    dragging_hs = True
                    _set_hs_from_pos(*event.pos)
                elif v_rect.collidepoint(event.pos):
                    dragging_v = True
                    _set_v_from_pos(event.pos[1])

            if event.type == pygame.MOUSEMOTION:
                if dragging_hs:
                    mx = max(hs_rect.left, min(event.pos[0], hs_rect.right-1))
                    my = max(hs_rect.top,  min(event.pos[1], hs_rect.bottom-1))
                    _set_hs_from_pos(mx, my)
                if dragging_v:
                    my = max(v_rect.top, min(event.pos[1], v_rect.bottom-1))
                    _set_v_from_pos(my)

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging_hs = False
                dragging_v  = False
                # Guardar temporalmente el color actual en el rol seleccionado
                _guardar_color_en_rol_actual()

            # ---- Eventos de UI ----
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
                    if event.ui_element == ent_hex:
                        _hex_entry_to_state()
                    elif event.ui_element in (ent_r, ent_g, ent_b):
                        _rgb_entries_to_state()

                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == btn_aplicar:
                        # Persistir todo a JSON
                        try:
                            ruta = ruta_tema_json(username)
                        except Exception:
                            ruta = "tema.json"
                        try:
                            state.aplicar_archivo(ruta=ruta, musica=None)
                            try:
                                marcar_personalizacion(username, ruta)
                            except Exception:
                                pass
                        except Exception as e:
                            print("Error al guardar tema:", e)
                    elif event.ui_element == btn_cancel:
                        running = False
                    elif event.ui_element == btn_buscar:
                        q = ent_buscar.get_text().strip()
                        if q:
                            t = spotify.buscar_cancion(q)
                            if t:
                                lbl_sp.set_text(f"Seleccionada: {t[0]} — {t[1]}")
                            else:
                                lbl_sp.set_text("No se encontraron resultados.")
                    elif event.ui_element == btn_repro:
                        lbl_sp.set_text(spotify.buscar_dispositivo())

                if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                    if event.ui_element == dd_vista:
                        vista_actual = event.text
                    elif event.ui_element == dd_roles:
                        # Cambiar de rol manteniendo su HSV/Int guardados
                        try:
                            # localizar índice por etiqueta
                            idx = [etq for (_k, etq) in ROLES].index(event.text)
                            state.rol_idx = idx
                        except Exception:
                            state.rol_idx = 0
                        _load_role_and_refresh()
                    elif event.ui_element == dd_int:
                        try:
                            state.intensidad_idx = INT_ETIQUETAS.index(event.text)
                            # Guardar en el rol la nueva intensidad (sin cambiar color)
                            k = ROLES[state.rol_idx][0]
                            state.estilos[k]["int"] = state.intensidad_idx
                        except Exception:
                            pass

            manager.process_events(event)

        manager.update(time_delta)

        # ---- Dibujo -------------------------------------------------
        screen.fill(BG)

        title = pygame.font.SysFont("segoeui", 26).render("Personaliza tu tema", True, TEXT_TITLE)
        screen.blit(title, (center_x - title.get_width() // 2, 24))

        screen.blit(hs_surf, hs_rect)
        screen.blit(v_surf, v_rect)

        # cursor HS
        hs_x = int(state.h * (map_w - 1)) + hs_rect.left
        hs_y = int((1 - state.s) * (map_h - 1)) + hs_rect.top
        pygame.draw.circle(screen, (255, 255, 255), (hs_x, hs_y), 6, 2)

        # cursor V
        v_y = int((1 - state.v) * (bar_h - 1)) + v_rect.top
        pygame.draw.rect(screen, (255, 255, 255), (v_rect.left - 2, v_y - 3, bar_w + 4, 6), 2)

        # Preview
        preview_rect = pygame.Rect(center_x - 360, top_y + 300, 720, 300)
        pygame.draw.rect(screen, BORDER, preview_rect, 1, border_radius=8)

        if vista_actual == "Game Over":
            draw_preview_gameover(screen, state, preview_rect)
        else:
            draw_preview_win(screen, state, preview_rect)

        exit_text = pygame.font.SysFont("segoeui", 12).render(
            "ESC para salir | F11 alterna pantalla completa", True, TEXT_BODY)
        screen.blit(exit_text, (center_x - exit_text.get_width() // 2, WIN_H - 30))

        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    # Por si acaso la pantalla completa te complica salir:
    # cambia el flag a 0 en set_mode o usa ESC.
    main("invitado")
