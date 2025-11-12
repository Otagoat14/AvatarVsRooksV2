import pygame
import os
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from perfiles import cargar_perfil
from perfiles import obtener_colores
from Clases_auxiliares.musica import MUSICA
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
            MUSICA.detener()
            
            # Verificar si el usuario tiene música personalizada
            perfil = cargar_perfil(self.username)
            if perfil and perfil.get('musica'):
                # TODO: Integrar reproducción de Spotify aquí
                if MUSICA.cargar_musica("./musica/menu_ambiental.mp3"):
                    MUSICA.reproducir(loops=-1)
            else:
                # Música por defecto
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
        except:
            # Fallback a fuentes del sistema
            self.fuente_titulo = pygame.font.SysFont("segoeui", 48, bold=True)
            self.fuente_boton = pygame.font.SysFont("segoeui", 32, bold=True)
            self.fuente_desc = pygame.font.SysFont("segoeui", 16)
    
    def _crear_botones(self):
        center_x = self.WIN_W // 2
        center_y = self.WIN_H // 2
        
        btn_width, btn_height = 400, 100
        espaciado = 140  # Aumentado de 120 a 140 para más separación
        
        # Botones con más espacio entre ellos
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
    
    def _dibujar_boton(self, boton_info, dificultad):
        rect = boton_info["rect"]
        texto = boton_info["texto"]
        descripcion = boton_info["descripcion"]
        
        # Determinar color según estado
        if boton_info["hover"]:
            color_btn = self.col_btn_hover
        else:
            color_btn = self.col_btn_primario
        
        # Dibujar botón
        pygame.draw.rect(self.screen, color_btn, rect, border_radius=15)
        pygame.draw.rect(self.screen, self._ajustar_color(color_btn, 0.8), rect, width=3, border_radius=15)
        
        # Dibujar texto del botón
        color_texto_btn = self._obtener_color_texto_contraste(color_btn)
        texto_surface = self.fuente_boton.render(texto, True, color_texto_btn)
        texto_rect = texto_surface.get_rect(center=rect.center)
        self.screen.blit(texto_surface, texto_rect)
        
        # Dibujar descripción - AUMENTAR ESPACIO entre botón y descripción
        color_desc = self._ajustar_color(self.col_texto, 0.7)
        desc_surface = self.fuente_desc.render(descripcion, True, color_desc)
        desc_rect = desc_surface.get_rect(center=(rect.centerx, rect.bottom + 30))  # Aumentado de 20 a 30
        self.screen.blit(desc_surface, desc_rect)
    
    def _procesar_eventos(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.dificultad_seleccionada = "salir"
            
            elif event.type == pygame.MOUSEMOTION:
                # Actualizar estado hover de los botones
                mouse_pos = pygame.mouse.get_pos()
                for dificultad, boton in self.botones.items():
                    boton["hover"] = boton["rect"].collidepoint(mouse_pos)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    mouse_pos = pygame.mouse.get_pos()
                    for dificultad, boton in self.botones.items():
                        if boton["rect"].collidepoint(mouse_pos):
                            self.dificultad_seleccionada = dificultad
                            self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    self.dificultad_seleccionada = "salir"
                elif event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    self.dificultad_seleccionada = "facil"
                    self.running = False
                elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    self.dificultad_seleccionada = "medio"
                    self.running = False
                elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                    self.dificultad_seleccionada = "dificil"
                    self.running = False
    def _dibujar_interfaz(self):
        # Fondo
        self.screen.fill(self.col_fondo)
        
        # Panel central - AUMENTAR ALTURA para acomodar mejor los botones
        panel_rect = pygame.Rect(self.WIN_W//2 - 450, self.WIN_H//2 - 350, 900, 700)  # Aumentada altura de 600 a 700
        pygame.draw.rect(self.screen, self.col_ventana, panel_rect, border_radius=25)
        pygame.draw.rect(self.screen, self._ajustar_color(self.col_ventana, 1.1), 
                       panel_rect, width=4, border_radius=25)
        
        # Título - Ajustar posición para centrar mejor
        titulo_surface = self.fuente_titulo.render(self.t("SELECCIONA LA DIFICULTAD"), True, self.col_texto)
        titulo_rect = titulo_surface.get_rect(center=(self.WIN_W//2, self.WIN_H//2 - 250))  # Ajustada posición
        self.screen.blit(titulo_surface, titulo_rect)
        
        # Dibujar botones
        for dificultad, boton in self.botones.items():
            self._dibujar_boton(boton, dificultad)
        
        # Instrucciones
        instrucciones = self.t("Presiona ESC para salir • 1=Fácil • 2=Medio • 3=Difícil")
        inst_surface = self.fuente_desc.render(instrucciones, True, self._ajustar_color(self.col_texto, 0.6))
        inst_rect = inst_surface.get_rect(center=(self.WIN_W//2, self.WIN_H - 40))
        self.screen.blit(inst_surface, inst_rect)
    
    def run(self):
        while self.running and not self.dificultad_seleccionada:
            self._procesar_eventos()
            self._dibujar_interfaz()
            pygame.display.flip()
            self.clock.tick(60)
        
        return self.dificultad_seleccionada

def main(username: str, lang: str = "es"):
    pantalla = PantallaDificultad(username, lang)
    dificultad = pantalla.run()
    
    def _aplicar_tema_desde_perfiles():
        """
        Lee el tema del usuario y pisa los colores globales de esta ventana.
        Ajusta aquí los nombres de tus variables de color locales.
        """
        global COLOR_FONDO, COLOR_TEXTO, BTN_BG, BTN_HOVER, SUBTEXTO  # o las que uses en dificultad.py
        col = obtener_colores(username)
        if not col:
            return
        # Mapa clave->variable_local
        mapeo = {
            "fondo": "COLOR_FONDO",
            "ventana": "SUBTEXTO",        # si tienes un color para panel/fondo de tarjetas
            "btn_primario": "BTN_BG",
            "btn_secundario": "BTN_HOVER",
            "texto": "COLOR_TEXTO",
        }
        for k, var in mapeo.items():
            if k in col and "rgb" in col[k]:
                rgb = tuple(col[k]["rgb"])
                globals()[var] = rgb

    # === LLÁMALA ANTES DE DIBUJAR NADA ===
    _aplicar_tema_desde_perfiles()



    if dificultad and dificultad != "salir":
        # Iniciar el juego después de seleccionar dificultad
        try:
            # Detener música del menú
            MUSICA.detener()
            
            # Importar y ejecutar el juego
            from Interfaz_Juego import Interfaz
            juego = Interfaz(dificultad=dificultad, puntaje_acumulado=0, usuario=username)
            juego.ejecutar()

            
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
    
    # Cerrar pygame solo después de que termine el juego
    pygame.quit()
    return dificultad

if __name__ == "__main__":
    # Para testing
    if len(sys.argv) > 1:
        username = sys.argv[1]
        lang = sys.argv[2] if len(sys.argv) > 2 else "es"
        main(username, lang)
    else:
        main("usuario_test")