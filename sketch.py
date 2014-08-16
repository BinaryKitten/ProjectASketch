__author__ = 'Kathryn Reeve'
import serial
import pygame
import random
import json

json_data = open('./config.json')
config = json.load(json_data)
json_data.close()

shake_alpha = (255 / 100) * config["screen"]["shake_alpha_perc"]
shake_amount = 1
screensize = [0, 0]
cursor_pos = [0, 0]
screen = False
cursor_size = 5
zreads = []
last_z_avg = 0


def pixel(surface, color, pos):
    if config["cursor"]["style"] == "square":
        surface.fill(color, (pos, (config["cursor"]["height"], config["cursor"]["width"])))
    elif config["cursor"]["style"] == "circle":
        pygame.draw.circle(surface, color, pos, config["cursor"]["width"])


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
    global use_serial, last_z_avg, zreads
    pygame.display.flip()
    if config["process"] == "serial":
        ser = serial.Serial(config["serial"]["port"], config["serial"]["baud"])
        ser.close()
        ser.open()
        serial_line = ser.readline().strip()
        print serial_line

    while True:
        for event in pygame.event.get():
            if event.type is pygame.KEYDOWN and (event.key == pygame.K_RETURN and (event.mod & (pygame.KMOD_LALT | pygame.KMOD_RALT)) != 0):
                toggle_fullscreen()
                pygame.display.flip()
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]:
                return

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
            else:
                x,y,z = serial_line.split()
                zpos = int(y.split(":")[1])
                zreads.append(zpos)
                if len(zreads) > config['shake']['reads']:
                    zreads.pop(0)

                if len(zreads) == config['shake']['reads']:
                    avg = sum(zreads) / config['shake']['reads']
                    if last_z_avg == 0:
                        last_z_avg = avg
                    elif avg <= (last_z_avg - config['shake']['threshold']) | avg >= (last_z_avg + config['shake']['threshold']):
                        pressed[pygame.K_s] = 1
                        last_z_avg = avg

            project_a_sketch(pressed)
            pygame.time.wait(10)

        elif config["process"] == "random":
            pressed = {
                pygame.K_UP: (0, 1, 0, 1, 0, 1)[random.randrange(5)],
                pygame.K_DOWN: (1, 0, 0, 1, 0, 1)[random.randrange(5)],
                pygame.K_LEFT: (0, 1, 0, 0, 1, 1)[random.randrange(5)],
                pygame.K_RIGHT: (1, 0, 1, 1, 0, 1)[random.randrange(5)],
                pygame.K_s: pygame.key.get_pressed()[pygame.K_s]
            }
            project_a_sketch(pressed)
            pygame.time.wait(10)

        else:
            pressed = pygame.key.get_pressed()
            project_a_sketch(pressed)
            pygame.time.wait(50)


def calculate_screen():
    global screensize, cursor_pos, screen

    if config["screen"]["fullscreen"] == 1:
        screenData = pygame.display.Info()
        screensize = [screenData.current_w, screenData.current_h]
        screen = pygame.display.set_mode(screensize, pygame.FULLSCREEN)
    else:
        screensize = [config["screen"]["width"], config["screen"]["height"]]
        screen = pygame.display.set_mode(screensize)

    cursor_pos = [screensize[0] / 2, screensize[1] / 2]


def main():
    global font, screen
    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.font.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 16)
    calculate_screen()
    pygame.display.set_caption('Project a Sketch')
    pygame.event.set_allowed(pygame.KEYDOWN)
    screen.fill((255, 255, 255))
    run_game_loop()

if __name__ == "__main__":
    main()