__author__ = 'Kathryn Reeve'
import serial
import pygame
import os

screensize = [800, 600]
cursor_pos = [screensize[0] / 2, screensize[1] / 2]
cursor_size = 10
shake_alpha = (255 / 100) * 5
shake_amount = 1


def pixel(surface, color, pos):
    surface.fill(color, (pos, (cursor_size, cursor_size)))


def toggle_fullscreen():
    global screen
    newscreen = pygame.display.get_surface()
    tmp = newscreen.convert()
    caption = pygame.display.get_caption()
    # Duoas 16-04-2007
    cursor = pygame.mouse.get_cursor()

    w, h = newscreen.get_width(), newscreen.get_height()
    flags = newscreen.get_flags()
    bits = newscreen.get_bitsize()

    pygame.display.quit()
    pygame.display.init()

    screen = pygame.display.set_mode((w, h), flags ^ pygame.FULLSCREEN, bits)
    screen.blit(tmp, (0, 0))
    pygame.display.set_caption(*caption)


    # HACK: work-a-round for a SDL bug??
    pygame.key.set_mods(0)

    # Duoas 16-04-2007
    pygame.mouse.set_cursor(*cursor)

    return screen


def run_game_loop_keyboard():
    global cursor_pos, cursor_size, shake_alpha, shake_amount
    pygame.display.flip()
    while True:
        for event in pygame.event.get():
            if (event.type is pygame.KEYDOWN and event.key == pygame.K_RETURN
                    and (event.mod&(pygame.KMOD_LALT|pygame.KMOD_RALT)) != 0):
                toggle_fullscreen()
                pygame.display.flip()
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]:
                return

        pressed = pygame.key.get_pressed()
        render_pixel = False
        render_shake = False

        if 1 in (pressed[pygame.K_DOWN], pressed[pygame.K_d]):
            cursor_pos[1] += cursor_size
            render_pixel = True
            if cursor_pos[1] >= screensize[1] - cursor_size:
                cursor_pos[1] = screensize[1] - cursor_size

        if 1 in (pressed[pygame.K_UP], pressed[pygame.K_u]):
            cursor_pos[1] -= cursor_size
            render_pixel = True
            if cursor_pos[1] < 0:
                cursor_pos[1] = 0

        if 1 in (pressed[pygame.K_LEFT], pressed[pygame.K_l]):
            cursor_pos[0] -= cursor_size
            render_pixel = True
            if cursor_pos[0] < 0:
                cursor_pos[0] = 0

        if 1 in (pressed[pygame.K_RIGHT], pressed[pygame.K_r]):
            cursor_pos[0] += cursor_size
            render_pixel = True
            if cursor_pos[0] >= screensize[0] - cursor_size:
                cursor_pos[0] = screensize[0] - cursor_size

        if 1 == pressed[pygame.K_s]:
            shake_surface = pygame.Surface((screensize[0], screensize[1]))
            shake_surface.fill((255, 255, 255))
            shake_surface.set_alpha(shake_alpha * shake_amount)
            shake_amount += 1
            if (shake_amount == 11):
                shake_amount = 1
            screen.blit(shake_surface, (0, 0))
            render_shake = True

        if render_pixel:
            pixel(screen, (0, 0, 0), (cursor_pos[0], cursor_pos[1]))

        if render_pixel or render_shake:
            pygame.display.flip()
            pygame.time.wait(50)


def run_game_loop_serial():
    port = "COM5"
    ser = serial.Serial(port, 115200)
    pass


def main():
    global font, screen
    pygame.init()
    pygame.font.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    screen = pygame.display.set_mode(screensize)
    pygame.display.set_caption('Project a Sketch')
    pygame.event.set_allowed(pygame.KEYDOWN)
    screen.fill((255, 255, 255))

    if os.environ.get("PAS_SERIAL", 0) == 1:
        run_game_loop_serial()
    else:
        run_game_loop_keyboard()


if __name__ == "__main__":
    main()