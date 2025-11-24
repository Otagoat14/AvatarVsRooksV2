import pygame
import os
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from perfiles import cargar_perfil, obtener_colores, obtener_musica_usuario
from Clases_auxiliares.musica import MUSICA
from Clases_auxiliares.integracion_spotify import reproducir_uri
from Traductor import dic_idiomas

class PantallaDificultad:
    def __init__(self, username: str, lang: str = "es"):
        self.username = username
        self.lang = lang
        self.tema = self._cargar_tema_usuario()
        
        # Función de traducción
        def t(key):
            return dic_idiomas.get(self.lang, dic_idiomas["es"]).get(key, key)
        self.t = t
        
        # Inicializar Pygame
        pygame.init()
        self.info = pygame.display.Info()
        self.WIN_W = self.info.current_w
        self.WIN_H = self.info.current_h

        try:
            from perfiles import obtener_paleta_personalizada
            paleta = obtener_paleta_personalizada(self.username)
            self.FONDO_PANTALLA = paleta["FONDO_PANTALLA"]
            self.CARD_BG = paleta["CARD_BG"]
            self.COLOR_BOTONES = paleta["COLOR_BOTONES"]
            self.COLOR_TEXT_TITU = paleta["COLOR_TEXT_TITU"]
            self.COLOR_TEXT_CUER = paleta["COLOR_TEXT_CUER"]
        except Exception as e:
            print(f"No se aplicó personalización en dificultad: {e}")
        
        self.screen = pygame.display.set_mode((self.WIN_W, self.WIN_H), pygame.FULLSCREEN)
        pygame.display.set_caption(t("Selección de Dificultad"))
        self.clock = pygame.time.Clock()
        
        # Aplicar tema personalizado
        self._aplicar_tema()
        
        # Configurar música
        self._configurar_musica()
        
        # Cargar fuentes
        self._cargar_fuentes()
        
        # Crear botones
        self._crear_botones()
        
        # Estado
        self.dificultad_seleccionada = None
        self.mostrar_salon_fama = False
        self.running = True
        
    def _cargar_tema_usuario(self):
        try:
            from perfiles import obtener_colores
            return obtener_colores(self.username)
        except Exception as e:
            print(f"Error cargando tema: {e}")
            return {
                "fondo": {"rgb": [20, 22, 26]},
                "texto": {"rgb": [245, 245, 245]},
                "ventana": {"rgb": [34, 38, 44]},
                "btn_primario": {"rgb": [180, 68, 68]},
                "btn_secundario": {"rgb": [68, 68, 76]}
            }

    def _aplicar_tema(self):
        self.col_fondo = tuple(self.tema["fondo"]["rgb"])
        self.col_texto = tuple(self.tema["texto"]["rgb"])
        self.col_ventana = tuple(self.tema["ventana"]["rgb"])
        self.col_btn_primario = tuple(self.tema["btn_primario"]["rgb"])
        self.col_btn_secundario = tuple(self.tema["btn_secundario"]["rgb"])
        
        # Colores para estados de botones
        self.col_btn_hover = self._ajustar_color(self.col_btn_primario, 1.2)
        self.col_btn_active = self._ajustar_color(self.col_btn_primario, 0.8)
    
    def _configurar_musica(self):
        try:
            # Detener lo que estuviera sonando antes
            MUSICA.detener()
        except Exception:
            pass

        try:
            # 1) Intentar reproducir la canción personalizada del usuario (Spotify)
            uri = obtener_musica_usuario(self.username)
            if uri:
                ok = reproducir_uri(uri)
                if ok:
                    # Ya está sonando en Spotify, no cargamos música local
                    return

            # 2) Si no hay música personalizada o falló Spotify,
            #    usar la música por defecto local
            if MUSICA.cargar_musica("./musica/menu_ambiental.mp3"):
                MUSICA.reproducir(loops=-1)

        except Exception as e:
            print(f"Error configurando música: {e}")
            # Fallback a música por defecto
            try:
                if MUSICA.cargar_musica("./musica/menu_ambiental.mp3"):
                    MUSICA.reproducir(loops=-1)
            except:
                pass

    
    def _cargar_fuentes(self):
        try:
            # Intentar cargar fuentes personalizadas
            self.fuente_titulo = pygame.font.Font("Fuentes/super_sliced.otf", 48)
            self.fuente_boton = pygame.font.Font("Fuentes/super_sliced.otf", 32)
            self.fuente_desc = pygame.font.Font("Fuentes/super_sliced.otf", 16)
            self.fuente_salon = pygame.font.Font("Fuentes/super_sliced.otf", 24)
        except:
            # Fallback a fuentes del sistema
            self.fuente_titulo = pygame.font.SysFont("segoeui", 48, bold=True)
            self.fuente_boton = pygame.font.SysFont("segoeui", 32, bold=True)
            self.fuente_desc = pygame.font.SysFont("segoeui", 16)
            self.fuente_salon = pygame.font.SysFont("segoeui", 24)
    
    def _crear_botones(self):
        center_x = self.WIN_W // 2
        center_y = self.WIN_H // 2
        
        btn_width, btn_height = 400, 100
        espaciado = 140
        
        # Botones de dificultad
        self.botones = {
            "facil": {
                "rect": pygame.Rect(center_x - btn_width//2, center_y - 120, btn_width, btn_height),
                "texto": "🎮 " + self.t("FÁCIL"),
                "descripcion": self.t("Perfecto para principiantes"),
                "hover": False
            },
            "medio": {
                "rect": pygame.Rect(center_x - btn_width//2, center_y + 30, btn_width, btn_height),
                "texto": "⚔️ " + self.t("MEDIO"),
                "descripcion": self.t("Desafío equilibrado"),
                "hover": False
            },
            "dificil": {
                "rect": pygame.Rect(center_x - btn_width//2, center_y + 180, btn_width, btn_height),
                "texto": "🔥 " + self.t("DIFÍCIL"),
                "descripcion": self.t("Para expertos en busca de reto"),
                "hover": False
            }
        }
        
        # Botón de Salón de la Fama 
        salon_btn_width, salon_btn_height = 220, 50  # Aumentado el ancho
        self.boton_salon = {
            "rect": pygame.Rect(self.WIN_W - salon_btn_width - 30, 30, salon_btn_width, salon_btn_height),
            "texto": "🏆 " + self.t("RANKING"),  
            "hover": False
        }
        
        # Botón para volver del salón de la fama
        self.boton_volver = {
            "rect": pygame.Rect(30, 30, 120, 50),
            "texto": "← " + self.t("VOLVER"),  # Texto en mayúsculas para consistencia
            "hover": False
        }
    
    def _ajustar_color(self, color, factor):
        r, g, b = color
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        return (r, g, b)
    
    def _obtener_color_texto_contraste(self, color_fondo):
        r, g, b = color_fondo
        luminancia = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        return (20, 20, 20) if luminancia > 0.6 else (245, 245, 245)
    
    def _dibujar_boton(self, boton_info, color_btn=None):
        rect = boton_info["rect"]
        texto = boton_info["texto"]
        
        # Determinar color según estado
        if not color_btn:
            if boton_info["hover"]:
                color_btn = self.col_btn_hover
            else:
                color_btn = self.col_btn_primario
        
        # Dibujar botón
        pygame.draw.rect(self.screen, color_btn, rect, border_radius=12)
        pygame.draw.rect(self.screen, self._ajustar_color(color_btn, 0.8), rect, width=3, border_radius=12)
        
        # Dibujar texto del botón - CENTRADO CORRECTAMENTE
        color_texto_btn = self._obtener_color_texto_contraste(color_btn)
        
        # SELECCIONAR FUENTE Y AJUSTAR TEXTO SEGÚN EL BOTÓN
        if rect.width <= 240:  # Botones pequeños como Salón de la Fama y Volver
            # Para botones pequeños, usar fuente más pequeña desde el inicio
            try:
                fuente = pygame.font.Font("Fuentes/super_sliced.otf", 20)  # Fuente más pequeña
            except:
                fuente = pygame.font.SysFont("segoeui", 20, bold=True)
            
            # Renderizar el texto
            texto_surface = fuente.render(texto, True, color_texto_btn)
            
            # Si aún es muy grande, reducir más el tamaño
            if texto_surface.get_width() > rect.width - 20:
                try:
                    fuente = pygame.font.Font("Fuentes/super_sliced.otf", 16)
                except:
                    fuente = pygame.font.SysFont("segoeui", 16, bold=True)
                texto_surface = fuente.render(texto, True, color_texto_btn)
        else:
            # Para botones grandes de dificultad
            try:
                fuente = pygame.font.Font("Fuentes/super_sliced.otf", 32)
            except:
                fuente = pygame.font.SysFont("segoeui", 32, bold=True)
            texto_surface = fuente.render(texto, True, color_texto_btn)
        
        # CENTRAR el texto en el botón - ESTA ES LA PARTE CLAVE
        texto_rect = texto_surface.get_rect(center=rect.center)
        self.screen.blit(texto_surface, texto_rect)
        
        # Dibujar descripción si existe (solo para botones de dificultad)
        if "descripcion" in boton_info:
            try:
                fuente_desc = pygame.font.Font("Fuentes/super_sliced.otf", 16)
            except:
                fuente_desc = pygame.font.SysFont("segoeui", 16)
            color_desc = self._ajustar_color(self.col_texto, 0.7)
            desc_surface = fuente_desc.render(boton_info["descripcion"], True, color_desc)
            desc_rect = desc_surface.get_rect(center=(rect.centerx, rect.bottom + 30))
            self.screen.blit(desc_surface, desc_rect)
    
    def _dibujar_salon_fama(self):
        # Fondo semitransparente
        overlay = pygame.Surface((self.WIN_W, self.WIN_H))
        overlay.set_alpha(230)
        overlay.fill(self.col_fondo)
        self.screen.blit(overlay, (0, 0))
        
        # Título
        titulo = self.fuente_titulo.render("SALÓN DE LA FAMA", True, self.col_texto)
        titulo_rect = titulo.get_rect(center=(self.WIN_W // 2, 80))
        self.screen.blit(titulo, titulo_rect)

        try:
            from Salon_fama import SalonFama
            salon = SalonFama()

            # TOP 10 POR NIVEL
            top_facil   = salon.obtener_top(10, dificultad="facil")
            top_medio   = salon.obtener_top(10, dificultad="medio")
            top_dificil = salon.obtener_top(10, dificultad="dificil")

            if not (top_facil or top_medio or top_dificil):
                mensaje = self.fuente_salon.render(
                    "No hay puntajes registrados aún", True, self.col_texto
                )
                mensaje_rect = mensaje.get_rect(center=(self.WIN_W // 2, self.WIN_H // 2))
                self.screen.blit(mensaje, mensaje_rect)
            else:
                # Posiciones X de cada columna
                x_facil   = self.WIN_W // 4
                x_medio   = self.WIN_W // 2
                x_dificil = 3 * self.WIN_W // 4
                y_top = 150

                def dibujar_columna(x_centro, titulo_modo, lista):
                    panel_ancho = 320
                    panel_alto  = 460
                    panel_rect = pygame.Rect(0, 0, panel_ancho, panel_alto)
                    panel_rect.centerx = x_centro
                    panel_rect.top = y_top

                    # Panel
                    pygame.draw.rect(self.screen, self.col_ventana, panel_rect, border_radius=15)
                    pygame.draw.rect(
                        self.screen,
                        self._ajustar_color(self.col_ventana, 1.1),
                        panel_rect,
                        width=3,
                        border_radius=15,
                    )

                    # Título del modo (FÁCIL / MEDIO / DIFÍCIL)
                    titulo_surf = self.fuente_salon.render(titulo_modo, True, self.col_texto)
                    titulo_rect = titulo_surf.get_rect(
                        center=(panel_rect.centerx, panel_rect.y + 30)
                    )
                    self.screen.blit(titulo_surf, titulo_rect)

                    # Encabezados
                    encabezados_y = panel_rect.y + 70
                    pos_x     = panel_rect.x + 30
                    nombre_x  = panel_rect.x + 80
                    puntaje_x = panel_rect.x + panel_ancho - 80

                    jugador_text = self.fuente_desc.render("JUGADOR", True, self.col_texto)
                    puntaje_text = self.fuente_desc.render("PUNTOS", True, self.col_texto)

                    self.screen.blit(jugador_text, (nombre_x, encabezados_y))
                    self.screen.blit(
                        puntaje_text,
                        (puntaje_x - puntaje_text.get_width() // 2, encabezados_y),
                    )

                    # Línea separadora
                    pygame.draw.line(
                        self.screen,
                        self.col_texto,
                        (panel_rect.x + 20, encabezados_y + 25),
                        (panel_rect.x + panel_ancho - 20, encabezados_y + 25),
                        2,
                    )

                    # Filas
                    for i, registro in enumerate(lista[:10]):
                        y = panel_rect.y + 110 + i * 32

                        # Color según posición
                        if i == 0:
                            color = (255, 215, 0)     # Oro
                        elif i == 1:
                            color = (192, 192, 192)   # Plata
                        elif i == 2:
                            color = (205, 127, 50)    # Bronce
                        else:
                            color = self.col_texto

                        pos_text = self.fuente_desc.render(f"{i+1}.", True, color)
                        self.screen.blit(pos_text, (pos_x, y))

                        nombre = registro.get("nombre", "")
                        if len(nombre) > 12:
                            nombre = nombre[:9] + "..."
                        nombre_surf = self.fuente_desc.render(nombre, True, color)
                        self.screen.blit(nombre_surf, (nombre_x, y))

                        puntaje = str(registro.get("puntaje", 0))
                        puntaje_surf = self.fuente_desc.render(puntaje, True, color)
                        self.screen.blit(
                            puntaje_surf,
                            (puntaje_x - puntaje_surf.get_width() // 2, y),
                        )

                # Dibujar las tres columnas
                dibujar_columna(x_facil,   "FÁCIL",   top_facil)
                dibujar_columna(x_medio,   "MEDIO",   top_medio)
                dibujar_columna(x_dificil, "DIFÍCIL", top_dificil)

        except Exception as e:
            print(f"Error cargando salón de la fama: {e}")
            error_text = self.fuente_salon.render(
                "Error al cargar el salón de la fama", True, (255, 50, 50)
            )
            error_rect = error_text.get_rect(center=(self.WIN_W // 2, self.WIN_H // 2))
            self.screen.blit(error_text, error_rect)

        # Botón Volver
        self._dibujar_boton(self.boton_volver)

    def _procesar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.dificultad_seleccionada = "salir"
            
            elif event.type == pygame.MOUSEMOTION:
                # Actualizar estado hover de los botones
                mouse_pos = pygame.mouse.get_pos()
                
                if self.mostrar_salon_fama:
                    self.boton_volver["hover"] = self.boton_volver["rect"].collidepoint(mouse_pos)
                else:
                    for dificultad, boton in self.botones.items():
                        boton["hover"] = boton["rect"].collidepoint(mouse_pos)
                    self.boton_salon["hover"] = self.boton_salon["rect"].collidepoint(mouse_pos)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.mostrar_salon_fama:
                        if self.boton_volver["rect"].collidepoint(mouse_pos):
                            self.mostrar_salon_fama = False
                    else:
                        # Verificar botón Salón de la Fama
                        if self.boton_salon["rect"].collidepoint(mouse_pos):
                            self.mostrar_salon_fama = True
                        
                        # Verificar botones de dificultad
                        for dificultad, boton in self.botones.items():
                            if boton["rect"].collidepoint(mouse_pos):
                                self.dificultad_seleccionada = dificultad
                                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.mostrar_salon_fama:
                        self.mostrar_salon_fama = False
                    else:
                        self.running = False
                        self.dificultad_seleccionada = "salir"
                elif not self.mostrar_salon_fama:
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        self.dificultad_seleccionada = "facil"
                        self.running = False
                    elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        self.dificultad_seleccionada = "medio"
                        self.running = False
                    elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        self.dificultad_seleccionada = "dificil"
                        self.running = False
    
    def _dibujar_interfaz_principal(self):
        # Fondo
        self.screen.fill(self.col_fondo)
        
        # Panel central
        panel_rect = pygame.Rect(self.WIN_W//2 - 450, self.WIN_H//2 - 350, 900, 700)
        pygame.draw.rect(self.screen, self.col_ventana, panel_rect, border_radius=25)
        pygame.draw.rect(self.screen, self._ajustar_color(self.col_ventana, 1.1), 
                       panel_rect, width=4, border_radius=25)
        
        # Título
        titulo_surface = self.fuente_titulo.render(self.t("SELECCIONA LA DIFICULTAD"), True, self.col_texto)
        titulo_rect = titulo_surface.get_rect(center=(self.WIN_W//2, self.WIN_H//2 - 250))
        self.screen.blit(titulo_surface, titulo_rect)
        
        # Dibujar botones de dificultad
        for dificultad, boton in self.botones.items():
            self._dibujar_boton(boton)
        
        # Dibujar botón Salón de la Fama
        self._dibujar_boton(self.boton_salon, self.col_btn_secundario)
        
        # Instrucciones
        instrucciones = self.t("Presiona ESC para salir • 1=Fácil • 2=Medio • 3=Difícil")
        inst_surface = self.fuente_desc.render(instrucciones, True, self._ajustar_color(self.col_texto, 0.6))
        inst_rect = inst_surface.get_rect(center=(self.WIN_W//2, self.WIN_H - 40))
        self.screen.blit(inst_surface, inst_rect)
    
    def run(self):
        while self.running and not self.dificultad_seleccionada:
            self._procesar_eventos()
            
            if self.mostrar_salon_fama:
                self._dibujar_salon_fama()
            else:
                self._dibujar_interfaz_principal()
                
            pygame.display.flip()
            self.clock.tick(60)
        
        return self.dificultad_seleccionada

def main(username: str, lang: str = "es"):
    corriendo = True
    dificultad = None

    while corriendo:
        # 1) Mostrar pantalla de dificultad
        pantalla = PantallaDificultad(username, lang)
        dificultad = pantalla.run()

        # Si el usuario sale desde la pantalla de dificultad
        if not dificultad or dificultad == "salir":
            corriendo = False
            break

        # 2) Aplicar tema desde perfiles (como ya lo tenías)
        def _aplicar_tema_desde_perfiles():
            """
            Lee el tema del usuario y pisa los colores globales de esta ventana.
            Ajusta aquí los nombres de tus variables de color locales.
            """
            global COLOR_FONDO, COLOR_TEXTO, BTN_BG, BTN_HOVER, SUBTEXTO
            col = obtener_colores(username)
            if not col:
                return
            mapeo = {
                "fondo": "COLOR_FONDO",
                "ventana": "SUBTEXTO",
                "btn_primario": "BTN_BG",
                "btn_secundario": "BTN_HOVER",
                "texto": "COLOR_TEXTO",
            }
            for k, var in mapeo.items():
                if k in col and "rgb" in col[k]:
                    rgb = tuple(col[k]["rgb"])
                    globals()[var] = rgb

        _aplicar_tema_desde_perfiles()

        # 3) Iniciar el juego
        try:
            # Detener música del menú
            MUSICA.detener()

            from Interfaz_Juego import Interfaz
            juego = Interfaz(dificultad=dificultad,
                             puntaje_acumulado=0,
                             usuario=username)
            resultado = juego.ejecutar()

            # Si desde el juego se pidió volver al menú,
            # simplemente continúa el while y se vuelve a crear PantallaDificultad.
            if resultado == "menu":
                continue

            # Si en algún momento quieres manejar otras salidas especiales,
            # podrías hacerlo aquí (por ahora, no hace falta).

        except Exception as e:
            print(f"Error al iniciar el juego: {e}")

            try:
                import tkinter as tk
                from tkinter import messagebox

                def t(key):
                    return dic_idiomas.get(lang, dic_idiomas["es"]).get(key, key)

                root = tk.Tk()
                root.withdraw()
                messagebox.showerror(
                    t("Error"),
                    f"{t('No se pudo iniciar el juego')}: {str(e)}"
                )
                root.destroy()
            except:
                pass

    return dificultad


if __name__ == "__main__":
    # Para testing
    if len(sys.argv) > 1:
        username = sys.argv[1]
        lang = sys.argv[2] if len(sys.argv) > 2 else "es"
        main(username, lang)
    else:
        main("usuario_test")