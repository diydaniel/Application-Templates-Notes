import pygame
import random
import sys
import colorsys

# --- Settings ---
FPS = 11
FONT_SIZE = 41
BLACK = (0, 0, 0)

def outline_surf(text_surf):
    o = text_surf.copy()
    o.fill((0, 0, 0, 255), special_flags=pygame.BLEND_RGBA_MULT)
    return o

def draw_text_with_outline(surface, text_surf, x, y):
    for ox, oy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
        surface.blit(outline_surf(text_surf), (x + ox, y + oy))
    surface.blit(text_surf, (x, y))

def hsv_color(h, s=1.0, v=1.0):
    r_f, g_f, b_f = colorsys.hsv_to_rgb(h, s, v)
    return (int(r_f * 255), int(g_f * 255), int(b_f * 255))

def main():
    # Terminal prompt on launch (kept from your request)
    try:
        user_message = input("Please tell me your screen saver message? ").strip()
    except EOFError:
        user_message = ""
    if not user_message:
        user_message = "Hello from CodeJacket.io"

    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Matrix Rain - Pygame")
    pygame.mouse.set_visible(False)  # ✅ hide cursor
    clock = pygame.time.Clock()

    WIDTH, HEIGHT = screen.get_size()
    font = pygame.font.SysFont("noteworthy", FONT_SIZE, bold=True, italic=True)

    columns = WIDTH // FONT_SIZE
    drops = [random.randint(-HEIGHT // FONT_SIZE, 0) for _ in range(columns)]
    chars = [chr(i) for i in range(33, 127)]

    trail_surf = pygame.Surface((WIDTH, HEIGHT))
    trail_surf.set_alpha(30)
    trail_surf.fill(BLACK)

    start_time = pygame.time.get_ticks()

    # --- Screensaver message settings ---
    msg_font = pygame.font.SysFont("noteworthy", max(22, FONT_SIZE), bold=True)
    msg_move_every_ms = 10_000
    msg_next_move_ms = 0
    msg_x, msg_y = 0, 0

    # --- Input box state (spacebar) ---
    input_active = False
    typed = ""
    input_prompt = "New message: "
    input_font = pygame.font.SysFont("noteworthy", 28, bold=True)

    running = True
    while running:
        now_ms = pygame.time.get_ticks()
        elapsed_ms = now_ms - start_time

        # --- One color per minute (rainbow stepping) ---
        minute_index = elapsed_ms // 60000
        steps = 60
        hue = (minute_index % steps) / steps
        current_color = hsv_color(hue, 1.0, 1.0)

        # ✅ Message color = one step BEFORE current hue
        prev_hue = ((minute_index - 1) % steps) / steps
        message_color = hsv_color(prev_hue, 1.0, 1.0)

        # --- events ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Global exits
                if event.key == pygame.K_ESCAPE and not input_active:
                    running = False

                # Space toggles input box
                elif event.key == pygame.K_SPACE and not input_active:
                    input_active = True
                    typed = ""

                # When input box is active, capture typing
                elif input_active:
                    if event.key == pygame.K_ESCAPE:
                        input_active = False  # cancel
                    elif event.key == pygame.K_RETURN:
                        new_msg = typed.strip()
                        if new_msg:
                            user_message = new_msg
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        typed = typed[:-1]
                    else:
                        # Basic text input (ignore weird control keys)
                        if event.unicode and event.unicode.isprintable():
                            typed += event.unicode

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

        # --- move message every 10 seconds (only if not editing) ---
        if not input_active and now_ms >= msg_next_move_ms:
            tmp = msg_font.render(user_message, True, (255, 255, 255))
            mw, mh = tmp.get_size()
            pad = 14
            msg_x = random.randint(pad, max(pad, WIDTH - mw - pad))
            msg_y = random.randint(pad, max(pad, HEIGHT - mh - pad))
            msg_next_move_ms = now_ms + msg_move_every_ms

        # --- draw message badge + message (color = previous hue step) ---
        if user_message and not input_active:
            msg_surf = msg_font.render(user_message, True, message_color)
            mw, mh = msg_surf.get_size()
            badge_pad_x, badge_pad_y = 16, 10
            badge_rect = pygame.Rect(
                msg_x - badge_pad_x,
                msg_y - badge_pad_y,
                mw + badge_pad_x * 2,
                mh + badge_pad_y * 2,
            )
            badge = pygame.Surface((badge_rect.w, badge_rect.h), pygame.SRCALPHA)
            badge.fill((0, 0, 0, 140))
            screen.blit(badge, (badge_rect.x, badge_rect.y))
            draw_text_with_outline(screen, msg_surf, msg_x, msg_y)

        # --- input box overlay ---
        if input_active:
            # Dim overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            # Input box
            box_w = min(900, WIDTH - 120)
            box_h = 90
            box_x = (WIDTH - box_w) // 2
            box_y = (HEIGHT - box_h) // 2

            box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            box.fill((20, 20, 20, 220))
            screen.blit(box, (box_x, box_y))

            # Border
            pygame.draw.rect(screen, (200, 200, 200), (box_x, box_y, box_w, box_h), 2)

            # Render prompt + typed
            display_text = input_prompt + typed
            text_surf = input_font.render(display_text, True, (255, 255, 255))
            screen.blit(text_surf, (box_x + 16, box_y + 26))

            # Help line
            help_surf = pygame.font.SysFont("noteworthy", 18).render(
                "Enter = Save   Esc = Cancel", True, (220, 220, 220)
            )
            screen.blit(help_surf, (box_x + 16, box_y + box_h + 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
