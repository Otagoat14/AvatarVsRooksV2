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


class VentanaWin:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.mixer.set_num_channels(20)

        self.screen = pygame.display.set_mode((VENT_ANCHO, VENT_ALTO))
        pygame.display.set_caption("¡Victoria!")

        # ===== Sonidos =====
        self.sonido_victoria = pygame.mixer.Sound("victory.wav")
        self.sonido_click = pygame.mixer.Sound("click.wav")
        self.sonido_victoria.set_volume(0.9)
        self.sonido_click.set_volume(1.0)

        self.sonido_victoria.play()

        # ===== Fuentes =====
        self.font_titulo = pygame.font.SysFont("Segoe UI", 64, True)
        self.font_texto = pygame.font.SysFont("Segoe UI", 30)
        self.font_boton = pygame.font.SysFont("Segoe UI", 24, True)

        self.clock = pygame.time.Clock()
        self.opacity = 0
        self.panel_y = -300  # Ahora cae desde arriba ✅
        self.target_y = 75
        self.time = 0

        # Botones
        self.btn_w, self.btn_h = 260, 55
        self.btn_reiniciar = pygame.Rect(VENT_ANCHO // 2 - self.btn_w - 20, 350, self.btn_w, self.btn_h)
        self.btn_menu = pygame.Rect(VENT_ANCHO // 2 + 20, 350, self.btn_w, self.btn_h)

        # ===== Partículas celebratorias =====
        self.particulas = [self.Particula() for _ in range(80)]

        self.running = True

    # ===== Clase Partículas =====
    class Particula:
        def __init__(self):
            self.x = random.randint(0, VENT_ANCHO)
            self.y = random.randint(0, VENT_ALTO)
            self.vel = random.uniform(0.3, 1)
            self.size = random.randint(3, 7)
            self.alpha = random.randint(150, 255)
            self.color = random.choice([(255,200,50),(255,255,80),(255,150,80)])

        def update(self):
            self.y -= self.vel
            if self.y < -10:
                self.y = VENT_ALTO + 10
                self.x = random.randint(0, VENT_ANCHO)

        def draw(self, scr):
            surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            surf.fill((*self.color, self.alpha))
            scr.blit(surf, (self.x, self.y))

    def run(self):
        # ===== CONFETTI =====
        confetti = []
        confetti_lifetime = 120  # Tiempo de animación
        confetti_active = True

        for _ in range(60):
            confetti.append([
                random.randint(50, VENT_ANCHO - 50),  # pos x
                self.panel_y + 140,  # pos y aprox donde está el título
                random.uniform(-2, 2),  # vel x
                random.uniform(-5, -2), # vel y (explosión hacia arriba)
                random.choice([(255,80,80),(80,255,80),(80,180,255),(255,255,80)])
            ])

        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.running = False

                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if self.btn_reiniciar.collidepoint(e.pos):
                        self.sonido_click.play()
                        pygame.time.delay(350)
                        self.running = False

                    if self.btn_menu.collidepoint(e.pos):
                        self.sonido_click.play()
                        pygame.time.delay(350)
                        self.running = False

            self.screen.fill(FONDO_PANTALLA)

            # Partículas de fondo
            for p in self.particulas:
                p.update()
                p.draw(self.screen)

            # Fade-in
            if self.opacity < 200:
                self.opacity += 3
            fade = pygame.Surface((VENT_ANCHO, VENT_ALTO), pygame.SRCALPHA)
            fade.fill((0, 0, 0, self.opacity))
            self.screen.blit(fade, (0, 0))

            # Panel cayendo
            if self.panel_y < self.target_y:
                self.panel_y += (self.target_y - self.panel_y) * 0.1

            card_rect = pygame.Rect(50, self.panel_y,
                                    VENT_ANCHO - 100, VENT_ALTO - 150)
            pygame.draw.rect(self.screen, CARD_BG, card_rect, border_radius=14)
            pygame.draw.rect(self.screen, CARD_BORDER, card_rect, 4, border_radius=14)

            # Título animado
            self.time += 0.05
            scale = 1 + math.sin(self.time * 4) * 0.05
            titulo = pygame.transform.scale(
                self.font_titulo.render("¡YOU WIN!", True, COLOR_TEXT_TITU),
                (int(420 * scale), int(80 * scale))
            )
            titulo_x = card_rect.centerx - titulo.get_width()//2
            titulo_y = self.panel_y + 40
            self.screen.blit(titulo, (titulo_x, titulo_y))
            
            # ===== CONFETTI EFFECT =====
            if confetti_active:
                confetti_lifetime -= 1
                if confetti_lifetime <= 0:
                    confetti_active = False

            if confetti_active:
                for cf in confetti:
                    cf[0] += cf[2]
                    cf[1] += cf[3]
                    cf[3] += 0.3  # gravedad
                    alpha = int(max(100, confetti_lifetime * 2))
                    pygame.draw.rect(self.screen,
                                     (*cf[4], alpha),
                                     (cf[0], cf[1], 6, 10))

            # Subtítulo
            subt = self.font_texto.render("¡Felicidades, has ganado el juego!",
                                          True, COLOR_TEXT_CUER)
            self.screen.blit(subt, (card_rect.centerx - subt.get_width()//2,
                                    self.panel_y + 140))

            # Botones
            botones = [(self.btn_reiniciar, "Reiniciar"), (self.btn_menu, "Menú Principal")]

            for idx, (rect, txt) in enumerate(botones):
                mouse = pygame.mouse.get_pos()
                hover = rect.collidepoint(mouse)

                color = HOVER if hover else COLOR_BOTONES
                scale_btn = 1.06 if hover else 1

                # ✨ Parpadeo suave SOLO en el primer botón ("Reiniciar")
                alpha = 255
                if idx == 0:
                    alpha = int(180 + math.sin(self.time * 7) * 75)

                btn_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(btn_surf, (*color, alpha),
                                (0, 0, rect.w, rect.h), border_radius=10)

                btn_scaled = pygame.transform.scale(btn_surf,
                    (int(rect.w * scale_btn), int(rect.h * scale_btn)))

                self.screen.blit(btn_scaled, (
                    rect.centerx - btn_scaled.get_width()//2,
                    rect.centery - btn_scaled.get_height()//2
                ))

                label = self.font_boton.render(txt, True, COLOR_TEXT_TITU)
                self.screen.blit(label, (
                    rect.centerx - label.get_width()//2,
                    rect.centery - label.get_height()//2
                ))


            pygame.display.update()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()



# ===== Ejecutar para probar =====
if __name__ == "__main__":
    VentanaWin().run()
