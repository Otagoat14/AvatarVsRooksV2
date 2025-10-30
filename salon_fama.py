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
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(10)

        # === Guardar la ventana principal actual (del juego)
        self.main_surface = pygame.display.get_surface()

        # === Crear subventana sin cerrar la principal ===
        self.window = pygame.display.set_mode((VENT_ANCHO, VENT_ALTO))
        pygame.display.set_caption("Salón de la Fama")

        # === Sonidos ===
        self.sonido_victoria = pygame.mixer.Sound("aplausos.wav")
        self.sonido_click = pygame.mixer.Sound("click.wav")
        self.sonido_victoria.set_volume(1.0)
        self.sonido_click.set_volume(1.0)
        self.sonido_victoria.play()

        # 🏆 Imagen del trofeo 
        self.img_trofeo = pygame.image.load("trofeo.png").convert_alpha()
        self.img_trofeo = pygame.transform.scale(self.img_trofeo, (64, 64))

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

    # ===== Ventana principal =====
    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False
                elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    self.running = False
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if self.btn_reiniciar.collidepoint(e.pos):
                        self.sonido_click.play()
                        pygame.time.delay(300)
                        self.running = False
                    elif self.btn_menu.collidepoint(e.pos):
                        self.sonido_click.play()
                        pygame.time.delay(300)
                        self.running = False
                    elif self.btn_ver.collidepoint(e.pos):
                        self.sonido_click.play()
                        pygame.time.delay(300)
                        self.running = False

            self.window.fill(FONDO_PANTALLA)

            # ✨ Fondo partículas
            for p in self.particulas:
                p.update()
                p.draw(self.window)

            # Fade
            if self.opacity < 200:
                self.opacity += 4
            fade = pygame.Surface((VENT_ANCHO, VENT_ALTO), pygame.SRCALPHA)
            fade.fill((0, 0, 0, self.opacity))
            self.window.blit(fade, (0, 0))

            # Panel principal descendente
            if self.panel_y < self.target_y:
                self.panel_y += (self.target_y - self.panel_y) * 0.18

            card_rect = pygame.Rect(50, self.panel_y, VENT_ANCHO - 100, VENT_ALTO - 150)
            pygame.draw.rect(self.window, CARD_BG, card_rect, border_radius=14)
            pygame.draw.rect(self.window, CARD_BORDER, card_rect, 4, border_radius=14)

            # 🏆 Trofeos flotando
            offset_y = math.sin(self.time * 3) * 5
            self.window.blit(self.img_trofeo, (card_rect.x - 10, card_rect.y - 10 + offset_y))
            self.window.blit(self.img_trofeo, (card_rect.right - 54, card_rect.bottom - 54 - offset_y))

            # Título animado
            self.time += 0.08
            scale = 1 + math.sin(self.time * 7) * 0.10
            titulo_surf = self.font_titulo.render("¡YOU WIN!", True, COLOR_TEXT_TITU)
            titulo_surf = pygame.transform.scale(
                titulo_surf,
                (int(titulo_surf.get_width() * scale), int(titulo_surf.get_height() * scale))
            )
            self.window.blit(titulo_surf, (card_rect.centerx - titulo_surf.get_width()//2, self.panel_y + 35))

            # Subtítulo
            subt_surf = self.font_texto.render("¡¡¡Has entrado al SALÓN DE LA FAMA!!!", True, COLOR_TEXT_CUER)
            subt_x = card_rect.centerx - subt_surf.get_width()//2
            subt_y = self.panel_y + 145
            self.window.blit(subt_surf, (subt_x, subt_y))

            # Botón "Ver"
            self._dibujar_boton_ver(subt_y + 60)

            # Confetti
            if self.confetti_lifetime > 0:
                self.confetti_lifetime -= 1
            self._dibujar_confetti()

            # Botones inferiores
            self._dibujar_botones()

            pygame.display.flip()
            self.clock.tick(60)

        # === Restaurar la ventana principal cuando se cierra ===
        if self.main_surface:
            ancho, alto = self.main_surface.get_size()
            pygame.display.set_mode((ancho, alto), pygame.FULLSCREEN)
            pygame.display.set_caption("Avatar vs Rooks")

    # ===== Funciones auxiliares =====
    def _dibujar_confetti(self):
        for cf in self.confetti:
            cf[0] += cf[2]
            cf[1] += cf[3]
            cf[3] += 0.38
            alpha = max(120, min(255, self.confetti_lifetime * 2))
            pygame.draw.rect(self.window, (*cf[4], alpha), (cf[0], cf[1], 8, 13))

    def _dibujar_boton_ver(self, y_pos):
        self.btn_ver.y = y_pos
        mouse = pygame.mouse.get_pos()
        hover = self.btn_ver.collidepoint(mouse)
        color = HOVER if hover else COLOR_BOTONES

        pygame.draw.rect(self.window, color, self.btn_ver, border_radius=12)
        label = self.font_boton.render("Ver", True, COLOR_TEXT_TITU)
        self.window.blit(label, (
            self.btn_ver.centerx - label.get_width() // 2,
            self.btn_ver.centery - label.get_height() // 2
        ))

    def _dibujar_botones(self):
        mouse = pygame.mouse.get_pos()
        botones = [(self.btn_reiniciar, "Reiniciar"), (self.btn_menu, "Menú Principal")]

        for rect, txt in botones:
            hover = rect.collidepoint(mouse)
            base_color = HOVER if hover else COLOR_BOTONES
            alpha = int(max(140, min(255, 200 + math.sin(self.time * 8) * 60))) if rect == self.btn_reiniciar else 255
            r, g, b = base_color

            btn_surf = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, (r, g, b, alpha), btn_surf.get_rect(), border_radius=12)

            scale_btn = 1.10 if hover else 1
            btn_scaled = pygame.transform.scale(btn_surf, (int(rect.w * scale_btn), int(rect.h * scale_btn)))
            self.window.blit(btn_scaled, (
                rect.centerx - btn_scaled.get_width() // 2,
                rect.centery - btn_scaled.get_height() // 2
            ))

            label = self.font_boton.render(txt, True, COLOR_TEXT_TITU)
            self.window.blit(label, (
                rect.centerx - label.get_width() // 2,
                rect.centery - label.get_height() // 2
            ))


# === Prueba directa ===
if __name__ == "__main__":
    pygame.init()
    pantalla_principal = pygame.display.set_mode((1000, 700))  # simula juego
    pantalla_principal.fill((20, 30, 40))
    pygame.display.flip()

    VentanaSalonFama().run()
