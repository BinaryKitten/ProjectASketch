__author__ = 'Kathryn Reeve'
import serial
import pygame
import random
import json
import sys

json_data = open('./config.json')
config = json.load(json_data)
json_data.close()

shake_alpha = (255 / 100) * config["screen"]["shake_alpha_perc"]
shake_amount = 1
screensize = [0, 0]
cursor_pos = [0, 0]
screen = False
cursor_size = 5
shake_reads = []
shake_avg = 0


def pixel(surface, color, pos):
    if config["cursor"]["style"] == "square":
        surface.fill(color, (pos, (config["cursor"]["height"], config["cursor"]["width"])))
    elif config["cursor"]["style"] == "circle":
        pygame.draw.circle(surface, color, pos, config["cursor"]["width"])


def toggle_full_screen():
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

    if 1 == pressed[pygame.K_DOWN] and cursor_pos[1] < screensize[1] - cursor_size:
        render_pixel = True
        cursor_pos[1] += cursor_size

    if 1 == pressed[pygame.K_UP] and cursor_pos[1] > 0:
        cursor_pos[1] -= cursor_size
        render_pixel = True

    if 1 == pressed[pygame.K_LEFT] and cursor_pos[0] > 0:
        cursor_pos[0] -= cursor_size
        render_pixel = True

    if 1 == pressed[pygame.K_RIGHT] and cursor_pos[0] < screensize[0] - cursor_size:
        cursor_pos[0] += cursor_size
        render_pixel = True

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
    global use_serial, shake_avg, shake_reads
    pygame.display.flip()
    if config["process"] == "serial":
        ser = serial.Serial(config["serial"]["port"], config["serial"]["baud"])
        ser.setDTR(False)
        pygame.time.wait(100)
        ser.flushInput()
        ser.setDTR(True)

    while True:
        for event in pygame.event.get():
            if event.type is pygame.KEYDOWN and (event.key == pygame.K_RETURN and (event.mod & (pygame.KMOD_LALT | pygame.KMOD_RALT)) != 0):
                toggle_full_screen()
                pygame.display.flip()
            elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]):
                if config["process"] == "serial":
                    ser.close()
                return

        if config["process"] == "serial":
            # pressed = array thingy
            # build using the standard keys
            serial_line = ser.readline().strip()

            if not serial_line:
                continue

            # sys.stderr.write("%s\n" % serial_line)

            pressed = {
                pygame.K_UP: 0,
                pygame.K_DOWN: 0,
                pygame.K_LEFT: 0,
                pygame.K_RIGHT: 0,
                pygame.K_s: 0
            }

            if serial_line == 'u':
                pressed[pygame.K_UP] = 1
            elif serial_line == 'd':
                pressed[pygame.K_DOWN] = 1
            elif serial_line == 'l':
                pressed[pygame.K_LEFT] = 1
            elif serial_line == 'r':
                pressed[pygame.K_RIGHT] = 1
            elif serial_line[0] == 'X':
                x, y, z = serial_line.split()
                letter_z, shake_axis_pos = y.split(":")
                shake_axis_pos = int(shake_axis_pos)
                if len(shake_reads) < config['shake']['reads']:
                    shake_reads.append(shake_axis_pos)
                else:
                    shake_avg = sum(shake_reads) / config['shake']['reads']

                    if shake_axis_pos not in range(shake_avg - config['shake']['threshold'], shake_avg + config['shake']['threshold']):
                        pressed[pygame.K_s] = 1

            if any(t==1 for t in pressed.itervalues()):
                # sys.stderr.write("%s\n" % pressed)
                project_a_sketch(pressed)
                pygame.time.wait(10)
                ser.flushInput()

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


def setup_screen():
    global screensize, cursor_pos, screen

    if config["screen"]["fullscreen"] == 1:
        screenData = pygame.display.Info()
        screensize = [screenData.current_w, screenData.current_h]
        screen = pygame.display.set_mode(screensize, pygame.FULLSCREEN)
    else:
        screensize = [config["screen"]["width"], config["screen"]["height"]]
        screen = pygame.display.set_mode(screensize)
        pygame.display.set_caption('Project a Sketch')

    cursor_pos = [screensize[0] / 2, screensize[1] / 2]
    screen.fill((255, 255, 255))


def setup_cursor():
    pass


def main():
    global font, screen
    sys.stderr.write("Project a Sketch - Start up\n")
    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.font.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 16)

    sys.stderr.write("Project a Sketch - Setting Screen\n")
    setup_screen()

    sys.stderr.write("Project a Sketch - Setting Cursor\n")
    setup_cursor()

    sys.stderr.write("Project a Sketch - Setting only Key Down and Quit as allowed events\n")
    pygame.event.set_allowed([pygame.KEYDOWN, pygame.QUIT])
    sys.stderr.write("Project a Sketch - Starting Sketch\n")
    run_game_loop()

    sys.stderr.write("Project a Sketch - Exiting System\n")
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
