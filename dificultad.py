import pygame
import os
import sys

# Agregar el directorio actual al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from perfiles import cargar_perfil
from Clases_auxiliares.musica import MUSICA
from traductor_pygame import t, configurar_idioma
from Traductor import dic_idiomas

class PantallaDificultad:
    def __init__(self, username: str, lang: str = "es"):
        self.username = username
        self.lang = lang
        self.tema = self._cargar_tema_usuario()

        configurar_idioma(lang)
        
        # Inicializar Pygame
        pygame.init()
        self.info = pygame.display.Info()
        self.WIN_W = self.info.current_w
        self.WIN_H = self.info.current_h
        
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
            perfil = cargar_perfil(self.username)
            if perfil and perfil.get('tema'):
                return perfil['tema']
        except Exception as e:
            print(f"Error cargando tema: {e}")
        
        # Tema por defecto si no hay personalización
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
        espaciado = 120
        
        # Botones
        self.botones = {
            "facil": {
                "rect": pygame.Rect(center_x - btn_width//2, center_y - 80, btn_width, btn_height),
                "texto": "🎮 " + t("FÁCIL"),
                "descripcion": t("Perfecto para principiantes"),
                "hover": False
            },
            "medio": {
                "rect": pygame.Rect(center_x - btn_width//2, center_y + 40, btn_width, btn_height),
                "texto": "⚔️ " + t("MEDIO"),
                "descripcion": t("Desafío equilibrado"),
                "hover": False
            },
            "dificil": {
                "rect": pygame.Rect(center_x - btn_width//2, center_y + 160, btn_width, btn_height),
                "texto": "🔥 " + t("DIFÍCIL"),
                "descripcion": t("Para expertos en busca de reto"),
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
        
        # Dibujar descripción
        color_desc = self._ajustar_color(self.col_texto, 0.7)
        desc_surface = self.fuente_desc.render(descripcion, True, color_desc)
        desc_rect = desc_surface.get_rect(center=(rect.centerx, rect.bottom + 20))
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
                elif event.key == pygame.K_1:
                    self.dificultad_seleccionada = "facil"
                    self.running = False
                elif event.key == pygame.K_2:
                    self.dificultad_seleccionada = "medio"
                    self.running = False
                elif event.key == pygame.K_3:
                    self.dificultad_seleccionada = "dificil"
                    self.running = False
    
    def _dibujar_interfaz(self):
        # Fondo
        self.screen.fill(self.col_fondo)
        
        # Panel central
        panel_rect = pygame.Rect(self.WIN_W//2 - 450, self.WIN_H//2 - 300, 900, 600)
        pygame.draw.rect(self.screen, self.col_ventana, panel_rect, border_radius=25)
        pygame.draw.rect(self.screen, self._ajustar_color(self.col_ventana, 1.1), 
                       panel_rect, width=4, border_radius=25)
        
        # Título
        titulo_surface = self.fuente_titulo.render(t("SELECCIONA LA DIFICULTAD"), True, self.col_texto)
        titulo_rect = titulo_surface.get_rect(center=(self.WIN_W//2, self.WIN_H//2 - 200))
        self.screen.blit(titulo_surface, titulo_rect)
        
        # Dibujar botones
        for dificultad, boton in self.botones.items():
            self._dibujar_boton(boton, dificultad)
        
        # Instrucciones
        instrucciones = t("Presiona ESC para salir • 1=Fácil • 2=Medio • 3=Difícil")
        inst_surface = self.fuente_desc.render(instrucciones, True, self._ajustar_color(self.col_texto, 0.6))
        inst_rect = inst_surface.get_rect(center=(self.WIN_W//2, self.WIN_H - 40))
        self.screen.blit(inst_surface, inst_rect)
    
    def run(self):
        while self.running and not self.dificultad_seleccionada:
            self._procesar_eventos()
            self._dibujar_interfaz()
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()
        return self.dificultad_seleccionada

def main(username: str, lang: str = "es"):
    pantalla = PantallaDificultad(username, lang)
    dificultad = pantalla.run()
    
    if dificultad and dificultad != "salir":
        
        # Iniciar el juego después de seleccionar dificultad
        try:
            # Detener música del menú
            MUSICA.detener()
            
            # Importar y ejecutar el juego
            from Interfaz_Juego import Interfaz
            
            # Solo pasar dificultad y lang, NO username
            juego = Interfaz(dificultad=dificultad, lang=lang)
            
            juego.ejecutar()
            
        except Exception as e:


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