__author__ = 'Kathryn Reeve'
import serial
import pygame
import random
import json
import serial

json_data = open('./config.json')
config = json.load(json_data)
json_data.close()

# screensize = [800, 600]
screensize = [config["screen"]["height"], config["screen"]["width"]]
cursor_pos = [screensize[0] / 2, screensize[1] / 2]
cursor_size = 10
shake_alpha = (255 / 100) * 5
shake_amount = 1
start_full_screen = (config["screen"]["fullscreen"])


def pixel(surface, color, pos):
    surface.fill(color, (pos, (cursor_size, cursor_size)))


def toggle_fullscreen():
    global screen
    tmp_screen = pygame.display.get_surface()
    tmp = tmp_screen.convert()
    caption = pygame.display.get_caption()
    # Duoas 16-04-2007
    cursor = pygame.mouse.get_cursor()

    w, h = tmp_screen.get_width(), tmp_screen.get_height()
    flags = tmp_screen.get_flags()
    bits = tmp_screen.get_bitsize()

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


def project_a_sketch(pressed):
    global cursor_pos, cursor_size, shake_alpha, shake_amount
    render_pixel = False
    render_shake = False

    if 1 == pressed[pygame.K_DOWN]:
        cursor_pos[1] += cursor_size
        render_pixel = True
        if cursor_pos[1] >= screensize[1] - cursor_size:
            cursor_pos[1] = screensize[1] - cursor_size

    if 1 == pressed[pygame.K_UP]:
        cursor_pos[1] -= cursor_size
        render_pixel = True
        if cursor_pos[1] < 0:
            cursor_pos[1] = 0

    if 1 == pressed[pygame.K_LEFT]:
        cursor_pos[0] -= cursor_size
        render_pixel = True
        if cursor_pos[0] < 0:
            cursor_pos[0] = 0

    if 1 == pressed[pygame.K_RIGHT]:
        cursor_pos[0] += cursor_size
        render_pixel = True
        if cursor_pos[0] >= screensize[0] - cursor_size:
            cursor_pos[0] = screensize[0] - cursor_size

    if 1 == pressed[pygame.K_s]:
        shake_surface = pygame.Surface((screensize[0], screensize[1]))
        shake_surface.fill((255, 255, 255))
        shake_surface.set_alpha(shake_alpha * shake_amount)
        shake_amount += 1
        if shake_amount == 11:
            shake_amount = 1
        screen.blit(shake_surface, (0, 0))
        render_shake = True

    if render_pixel:
        pixel(screen, (0, 0, 0), (cursor_pos[0], cursor_pos[1]))

    if render_pixel or render_shake:
        pygame.display.flip()


def run_game_loop():
    global use_serial
    pygame.display.flip()
    if config["process"] == "serial":
        ser = serial.Serial(config["serial"]["port"], config["serial"]["baud"], timeout=config["serial"]["timeout"])

    while True:
        for event in pygame.event.get():
            if event.type is pygame.KEYDOWN and (event.key == pygame.K_RETURN and (event.mod & (pygame.KMOD_LALT | pygame.KMOD_RALT)) != 0):
                toggle_fullscreen()
                pygame.display.flip()
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_TAB:
                use_serial = not use_serial

        if config["process"] == "serial":
            # pressed = array thingy
            # build using the standard keys
            serial_line = ser.readline().strip()

            pressed = {
                pygame.K_UP: 0,
                pygame.K_DOWN: 0,
                pygame.K_LEFT: 0,
                pygame.K_RIGHT: 0,
                pygame.K_s: 0
            }

            if not serial_line:
                pass

            elif serial_line == 'u':
                pressed[pygame.K_UP] = 1

            elif serial_line == 'd':
                pressed[pygame.K_DOWN] = 1

            elif serial_line == 'l':
                pressed[pygame.K_LEFT] = 1

            elif serial_line == 'r':
                pressed[pygame.K_RIGHT] = 1

            project_a_sketch(pressed)
            pygame.time.wait(10)

        elif config["process"] == "random":
            pressed = {
                pygame.K_UP: random.randrange(2),
                pygame.K_DOWN: random.randrange(2),
                pygame.K_LEFT: random.randrange(2),
                pygame.K_RIGHT: random.randrange(2),
                pygame.K_s: pygame.key.get_pressed()[pygame.K_s]
            }
            project_a_sketch(pressed)
            pygame.time.wait(10)

        else:
            pressed = pygame.key.get_pressed()
            project_a_sketch(pressed)
            pygame.time.wait(50)


def main():
    global font, screen
    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.font.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 16)

    screenData = pygame.display.Info()
    print

    if start_full_screen == 1:
        screen = pygame.display.set_mode(screensize, pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(screensize)
    pygame.display.set_caption('Project a Sketch')
    pygame.event.set_allowed(pygame.KEYDOWN)
    screen.fill((255, 255, 255))
    run_game_loop()

if __name__ == "__main__":
    main()