import pygame
import random
import sys
import math
import colorsys  # 🆕 for HSV → RGB

# --- Settings ---
FPS = 11
FONT_SIZE = 41

# Colors
BLACK = (0, 0, 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Matrix Rain - Pygame")
    clock = pygame.time.Clock()

    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.SysFont("noteworthy", FONT_SIZE, bold=True, italic=True)

    columns = WIDTH // FONT_SIZE
    drops = [random.randint(-HEIGHT // FONT_SIZE, 0) for _ in range(columns)]
    chars = [chr(i) for i in range(33, 127)]

    trail_surf = pygame.Surface((WIDTH, HEIGHT))
    trail_surf.set_alpha(30)
    trail_surf.fill(BLACK)

    color_phase = 0.0

    running = True
    start_time = pygame.time.get_ticks()  # ms since pygame.init()

    while running:
        # --- events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # --- One color per minute (rainbow stepping) ---
        now_ms = pygame.time.get_ticks()
        elapsed_ms = now_ms - start_time

        # How many full minutes have passed?
        minute_index = elapsed_ms // 60000  # 60000 ms = 1 minute

        # Map that minute index to a hue on the color wheel.
        # Example: 60 distinct colors around the spectrum.
        steps = 60
        hue = (minute_index % steps) / steps  # value between 0 and 1

        r_f, g_f, b_f = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        current_color = (int(r_f * 255), int(g_f * 255), int(b_f * 255))



        # --- trail fade ---
        screen.blit(trail_surf, (0, 0))

        # --- rain ---
        for i in range(columns):
            char = random.choice(chars)
            text_surface = font.render(char, True, current_color)

            x = i * FONT_SIZE
            y = drops[i] * FONT_SIZE

            screen.blit(text_surface, (x, y))

            drops[i] += 1
            if y > HEIGHT:
                drops[i] = random.randint(-HEIGHT // FONT_SIZE, 0)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
