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


class VentanaGameOver:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(10)

        # === Guardar referencia a la ventana principal (la del juego)
        self.main_surface = pygame.display.get_surface()

        # === Crear una subventana secundaria sin cerrar la principal ===
        self.window = pygame.display.set_mode((VENT_ANCHO, VENT_ALTO))
        pygame.display.set_caption("Game Over")

        # === Sonidos ===
        self.sonido_gameover = pygame.mixer.Sound("gameover.wav")
        self.sonido_click = pygame.mixer.Sound("click.wav")
        self.sonido_gameover.set_volume(0.9)
        self.sonido_click.set_volume(1.0)
        self.sonido_gameover.play()

        # === Fuentes ===
        self.font_titulo = pygame.font.SysFont("Segoe UI", 64, True)
        self.font_texto = pygame.font.SysFont("Segoe UI", 30)
        self.font_boton = pygame.font.SysFont("Segoe UI", 24, True)

        # === Estado general ===
        self.clock = pygame.time.Clock()
        self.opacity = 0
        self.panel_y = -300
        self.target_y = 75
        self.time = 0
        self.running = True

        # === Botones ===
        self.btn_w, self.btn_h = 260, 55
        self.btn_reiniciar = pygame.Rect(VENT_ANCHO // 2 - self.btn_w - 20, 350, self.btn_w, self.btn_h)
        self.btn_menu = pygame.Rect(VENT_ANCHO // 2 + 20, 350, self.btn_w, self.btn_h)

        # === Partículas ===
        self.particulas = [self.Particula() for _ in range(80)]

    # ===== Clase Partículas =====
    class Particula:
        def __init__(self):
            self.x = random.randint(0, VENT_ANCHO)
            self.y = random.randint(0, VENT_ALTO)
            self.vel = random.uniform(0.3, 1)
            self.size = random.randint(3, 7)
            self.alpha = random.randint(150, 255)
            self.color = random.choice([(255, 200, 50), (255, 255, 80), (255, 150, 80)])

        def update(self):
            self.y -= self.vel
            if self.y < -10:
                self.y = VENT_ALTO + 10
                self.x = random.randint(0, VENT_ANCHO)

        def draw(self, scr):
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            surf.fill((*self.color, self.alpha))
            scr.blit(surf, (self.x, self.y))

    # === Ventana principal (bucle local de Game Over) ===
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

            self.window.fill(FONDO_PANTALLA)

            # === Partículas ===
            for p in self.particulas:
                p.update()
                p.draw(self.window)

            # === Fade in ===
            if self.opacity < 200:
                self.opacity += 3
            fade = pygame.Surface((VENT_ANCHO, VENT_ALTO), pygame.SRCALPHA)
            fade.fill((0, 0, 0, self.opacity))
            self.window.blit(fade, (0, 0))

            # === Panel principal ===
            if self.panel_y < self.target_y:
                self.panel_y += (self.target_y - self.panel_y) * 0.1

            card_rect = pygame.Rect(50, self.panel_y, VENT_ANCHO - 100, VENT_ALTO - 150)
            pygame.draw.rect(self.window, CARD_BG, card_rect, border_radius=14)
            pygame.draw.rect(self.window, CARD_BORDER, card_rect, 4, border_radius=14)

            # === Texto principal ===
            self.time += 0.05
            scale = 1 + math.sin(self.time * 4) * 0.05
            titulo = pygame.transform.scale(
                self.font_titulo.render("¡GAME OVER!", True, COLOR_TEXT_TITU),
                (int(420 * scale), int(80 * scale))
            )
            self.window.blit(titulo, (card_rect.centerx - titulo.get_width() // 2, card_rect.y + 40))

            subt = self.font_texto.render("Has perdido. ¡Intenta de nuevo!", True, COLOR_TEXT_CUER)
            self.window.blit(subt, (card_rect.centerx - subt.get_width() // 2, card_rect.y + 150))

            # === Botones ===
            self._dibujar_botones()

            pygame.display.flip()
            self.clock.tick(60)

        # === Restaurar la ventana principal cuando se cierra ===
        if self.main_surface:
            ancho, alto = self.main_surface.get_size()
            pygame.display.set_mode((ancho, alto), pygame.FULLSCREEN)
            pygame.display.set_caption("Avatar vs Rooks")

    # === Método auxiliar para botones ===
    def _dibujar_botones(self):
        mouse = pygame.mouse.get_pos()
        for idx, (rect, texto) in enumerate([(self.btn_reiniciar, "Reiniciar"), (self.btn_menu, "Menú Principal")]):
            hover = rect.collidepoint(mouse)
            color = HOVER if hover else COLOR_BOTONES
            scale_btn = 1.06 if hover else 1

            alpha = int(180 + math.sin(self.time * 7) * 75) if idx == 0 else 255
            btn_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(btn_surf, (*color, alpha), btn_surf.get_rect(), border_radius=10)

            btn_scaled = pygame.transform.scale(
                btn_surf,
                (int(rect.w * scale_btn), int(rect.h * scale_btn))
            )
            self.window.blit(btn_scaled, (
                rect.centerx - btn_scaled.get_width() // 2,
                rect.centery - btn_scaled.get_height() // 2
            ))

            label = self.font_boton.render(texto, True, COLOR_TEXT_TITU)
            self.window.blit(label, (
                rect.centerx - label.get_width() // 2,
                rect.centery - label.get_height() // 2
            ))


# === Prueba directa (no interfiere con el juego) ===
if __name__ == "__main__":
    pygame.init()
    pantalla_principal = pygame.display.set_mode((1000, 700))  # simulación de juego
    pantalla_principal.fill((20, 30, 40))
    pygame.display.flip()

    # abrir ventana secundaria Game Over
    VentanaGameOver().run()
