import pygame
import sys
import math
import random

# ===== Colores =====
PALETA = {
    "charcoal": (30, 33, 36),
    "ruby": (155, 17, 30),
    "snow": (255, 250, 250),
    "taupe": (210, 200, 190),
    "vermilion": (227, 66, 52)
}

FONDO_PANTALLA = PALETA["charcoal"]
CARD_BG = PALETA["ruby"]
CARD_BORDER = PALETA["snow"]
COLOR_TEXT_TITU = PALETA["snow"]
COLOR_TEXT_CUER = PALETA["taupe"]
COLOR_BOTONES = PALETA["vermilion"]
HOVER = (50, 55, 60)

VENT_ANCHO, VENT_ALTO = 800, 500


class VentanaSalonFama:
    def __init__(self, main_surface):
        pygame.init()
        pygame.mixer.init()
        
        # === Guardar referencia a la ventana principal ===
        self.main_surface = main_surface
        self.original_caption = pygame.display.get_caption()
        
        # === Crear superficie para la ventana modal ===
        self.modal_surface = pygame.Surface((VENT_ANCHO, VENT_ALTO), pygame.SRCALPHA)

        # === Sonidos ===
        try:
            self.sonido_victoria = pygame.mixer.Sound("aplausos.wav")
            self.sonido_click = pygame.mixer.Sound("click.wav")
            self.sonido_victoria.set_volume(1.0)
            self.sonido_click.set_volume(1.0)
            self.sonido_victoria.play()
        except:
            print("⚠️ No se pudieron cargar los sonidos del Salón de la Fama")

        # 🏆 Imagen del trofeo 
        try:
            self.img_trofeo = pygame.image.load("trofeo.png").convert_alpha()
            self.img_trofeo = pygame.transform.scale(self.img_trofeo, (64, 64))
        except:
            print("⚠️ No se pudo cargar la imagen del trofeo")
            self.img_trofeo = None

        # === Fuentes ===
        self.font_titulo = pygame.font.SysFont("Segoe UI", 64, True)
        self.font_texto = pygame.font.SysFont("Segoe UI", 32)
        self.font_boton = pygame.font.SysFont("Segoe UI", 24, True)

        # === Estado general ===
        self.clock = pygame.time.Clock()
        self.opacity = 0
        self.panel_y = -300
        self.target_y = 65
        self.time = 0
        self.running = True
        self.accion_usuario = None

        # === Botones ===
        self.btn_w, self.btn_h = 260, 55
        self.btn_reiniciar = pygame.Rect(VENT_ANCHO // 2 - self.btn_w - 20, 350, self.btn_w, self.btn_h)
        self.btn_menu = pygame.Rect(VENT_ANCHO // 2 + 20, 350, self.btn_w, self.btn_h)
        self.btn_ver = pygame.Rect(VENT_ANCHO // 2 - 75, 250, 150, 45)

        # === Confetti y partículas ===
        self.confetti = [
            [
                random.randint(50, VENT_ANCHO - 50),
                self.panel_y + 140,
                random.uniform(-3.5, 3.5),
                random.uniform(-9, -3),
                random.choice([(255,80,80),(80,255,80),(80,180,255),
                               (255,255,80),(255,160,240),(255,120,180)])
            ]
            for _ in range(140)
        ]
        self.particulas = [self.Particula() for _ in range(70)]
        self.confetti_lifetime = 200
        
        # === Posición de la ventana modal (centrada) ===
        screen_width, screen_height = self.main_surface.get_size()
        self.modal_x = (screen_width - VENT_ANCHO) // 2
        self.modal_y = (screen_height - VENT_ALTO) // 2

    # ===== Clase Partículas =====
    class Particula:
        def __init__(self):
            self.x = random.randint(0, VENT_ANCHO)
            self.y = random.randint(0, VENT_ALTO)
            self.vel = random.uniform(0.3, 1)
            self.size = random.randint(2, 5)
            self.alpha = random.randint(120, 200)
            self.color = (255, 255, 255)

        def update(self):
            self.y -= self.vel
            if self.y < -10:
                self.y = VENT_ALTO + 10
                self.x = random.randint(0, VENT_ANCHO)

        def draw(self, scr):
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            surf.fill((*self.color, self.alpha))
            scr.blit(surf, (self.x, self.y))

    # ===== Ventana modal superpuesta =====
    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.accion_usuario = "salir"
                    self.running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    self.accion_usuario = "salir"
                    self.running = False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    # Ajustar coordenadas del mouse a la ventana modal
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    modal_mouse_x = mouse_x - self.modal_x
                    modal_mouse_y = mouse_y - self.modal_y
                    
                    if self.btn_reiniciar.collidepoint(modal_mouse_x, modal_mouse_y):
                        try:
                            self.sonido_click.play()
                        except:
                            pass
                        pygame.time.delay(300)
                        self.accion_usuario = "reiniciar"
                        self.running = False
                    elif self.btn_menu.collidepoint(modal_mouse_x, modal_mouse_y):
                        try:
                            self.sonido_click.play()
                        except:
                            pass
                        pygame.time.delay(300)
                        self.accion_usuario = "menu"
                        self.running = False
                    elif self.btn_ver.collidepoint(modal_mouse_x, modal_mouse_y):
                        try:
                            self.sonido_click.play()
                        except:
                            pass
                        pygame.time.delay(300)
                        self.accion_usuario = "ver"
                        self.running = False

            # === Dibujar en la superficie modal ===
            self.modal_surface.fill((0, 0, 0, 0))  # Limpiar con transparencia

            # ✨ Fondo partículas
            for p in self.particulas:
                p.update()
                p.draw(self.modal_surface)

            # Fade
            if self.opacity < 200:
                self.opacity += 4
            fade = pygame.Surface((VENT_ANCHO, VENT_ALTO), pygame.SRCALPHA)
            fade.fill((0, 0, 0, self.opacity))
            self.modal_surface.blit(fade, (0, 0))

            # Panel principal descendente
            if self.panel_y < self.target_y:
                self.panel_y += (self.target_y - self.panel_y) * 0.18

            card_rect = pygame.Rect(50, self.panel_y, VENT_ANCHO - 100, VENT_ALTO - 150)
            pygame.draw.rect(self.modal_surface, CARD_BG, card_rect, border_radius=14)
            pygame.draw.rect(self.modal_surface, CARD_BORDER, card_rect, 4, border_radius=14)

            # 🏆 Trofeos flotando
            if self.img_trofeo:
                offset_y = math.sin(self.time * 3) * 5
                self.modal_surface.blit(self.img_trofeo, (card_rect.x - 10, card_rect.y - 10 + offset_y))
                self.modal_surface.blit(self.img_trofeo, (card_rect.right - 54, card_rect.bottom - 54 - offset_y))

            # Título animado
            self.time += 0.08
            scale = 1 + math.sin(self.time * 7) * 0.10
            titulo_surf = self.font_titulo.render("¡YOU WIN!", True, COLOR_TEXT_TITU)
            titulo_surf = pygame.transform.scale(
                titulo_surf,
                (int(titulo_surf.get_width() * scale), int(titulo_surf.get_height() * scale))
            )
            self.modal_surface.blit(titulo_surf, (card_rect.centerx - titulo_surf.get_width()//2, self.panel_y + 35))

            # Subtítulo
            subt_surf = self.font_texto.render("¡¡¡Has entrado al SALÓN DE LA FAMA!!!", True, COLOR_TEXT_CUER)
            subt_x = card_rect.centerx - subt_surf.get_width()//2
            subt_y = self.panel_y + 145
            self.modal_surface.blit(subt_surf, (subt_x, subt_y))

            # Botón "Ver"
            self._dibujar_boton_ver(subt_y + 60)

            # Confetti
            if self.confetti_lifetime > 0:
                self.confetti_lifetime -= 1
            self._dibujar_confetti()

            # Botones inferiores
            self._dibujar_botones()

            # === Dibujar la modal sobre el juego principal ===
            self.main_surface.blit(self.modal_surface, (self.modal_x, self.modal_y))
            pygame.display.flip()
            
            self.clock.tick(60)

        # === Restaurar el título original ===
        pygame.display.set_caption(self.original_caption[0])
        
        return self.accion_usuario

    # ===== Funciones auxiliares =====
    def _dibujar_confetti(self):
        for cf in self.confetti:
            cf[0] += cf[2]
            cf[1] += cf[3]
            cf[3] += 0.38
            alpha = max(120, min(255, self.confetti_lifetime * 2))
            pygame.draw.rect(self.modal_surface, (*cf[4], alpha), (cf[0], cf[1], 8, 13))

    def _dibujar_boton_ver(self, y_pos):
        self.btn_ver.y = y_pos
        # Ajustar coordenadas del mouse a la ventana modal
        mouse_x, mouse_y = pygame.mouse.get_pos()
        modal_mouse_x = mouse_x - self.modal_x
        modal_mouse_y = mouse_y - self.modal_y
        
        hover = self.btn_ver.collidepoint(modal_mouse_x, modal_mouse_y)
        color = HOVER if hover else COLOR_BOTONES

        pygame.draw.rect(self.modal_surface, color, self.btn_ver, border_radius=12)
        label = self.font_boton.render("Ver", True, COLOR_TEXT_TITU)
        self.modal_surface.blit(label, (
            self.btn_ver.centerx - label.get_width() // 2,
            self.btn_ver.centery - label.get_height() // 2
        ))

    def _dibujar_botones(self):
        # Ajustar coordenadas del mouse a la ventana modal
        mouse_x, mouse_y = pygame.mouse.get_pos()
        modal_mouse_x = mouse_x - self.modal_x
        modal_mouse_y = mouse_y - self.modal_y
        
        botones = [(self.btn_reiniciar, "Reiniciar"), (self.btn_menu, "Menú Principal")]

        for rect, txt in botones:
            hover = rect.collidepoint(modal_mouse_x, modal_mouse_y)
            base_color = HOVER if hover else COLOR_BOTONES
            alpha = int(max(140, min(255, 200 + math.sin(self.time * 8) * 60))) if rect == self.btn_reiniciar else 255
            r, g, b = base_color

            btn_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, (r, g, b, alpha), btn_surf.get_rect(), border_radius=12)

            scale_btn = 1.10 if hover else 1
            btn_scaled = pygame.transform.scale(btn_surf, (int(rect.w * scale_btn), int(rect.h * scale_btn)))
            self.modal_surface.blit(btn_scaled, (
                rect.centerx - btn_scaled.get_width() // 2,
                rect.centery - btn_scaled.get_height() // 2
            ))

            label = self.font_boton.render(txt, True, COLOR_TEXT_TITU)
            self.modal_surface.blit(label, (
                rect.centerx - label.get_width() // 2,
                rect.centery - label.get_height() // 2
            ))


# === Prueba directa ===
if __name__ == "__main__":
    pygame.init()
    pantalla_principal = pygame.display.set_mode((1000, 700))
    pantalla_principal.fill((20, 30, 40))
    pygame.display.flip()

    accion = VentanaSalonFama(pantalla_principal).run()
    print(f"El usuario eligió: {accion}")