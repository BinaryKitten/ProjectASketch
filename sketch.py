__author__ = 'Kathryn Reeve'
import serial
import pygame

screensize = [800, 600]
cursor_pos = [screensize[0] / 2, screensize[1] / 2]
shake_surface = pygame.Surface((screensize[0], screensize[1]))
shake_surface.fill((255, 255, 255, 5))
cursor_size = 10
last_key = 0
last_key_count = 0
key_threshold = 20


def pixel(surface, color, pos):
    surface.fill(color, (pos, (cursor_size, cursor_size)))


def debounce(key):
    global last_key, last_key_count, key_threshold
    if last_key != key:
        last_key = key
        last_key_count = 0
        return False;
    elif last_key_count > key_threshold:
        last_key_count = 0
        return True
    else:
        last_key_count += 1
        return False


def button(btn_pressed):
    global cursor_pos, cursor_size
    render_pixel = False

    if btn_pressed in [pygame.K_UP, pygame.K_u]:
        cursor_pos[1] -= cursor_size
        render_pixel = True
        if cursor_pos[1] < 0:
            cursor_pos[1] = 0

    elif btn_pressed in [pygame.K_DOWN, pygame.K_d]:
        cursor_pos[1] += cursor_size
        render_pixel = True
        if cursor_pos[1] >= screensize[1] - cursor_size:
            cursor_pos[1] = screensize[1] - cursor_size

    elif btn_pressed in [pygame.K_LEFT, pygame.K_l]:
        cursor_pos[0] -= cursor_size
        render_pixel = True
        if cursor_pos[0] < 0:
            cursor_pos[0] = 0

    elif btn_pressed in [pygame.K_RIGHT, pygame.K_r]:
        cursor_pos[0] += cursor_size
        render_pixel = True
        if cursor_pos[0] >= screensize[0] - cursor_size:
            cursor_pos[0] = screensize[0] - cursor_size

    elif btn_pressed == pygame.K_s:
        screen.blit(shake_surface, (0, 0))

    if render_pixel:
        pixel(screen, (0, 0, 0), (cursor_pos[0], cursor_pos[1]))


def run_game_loop_keyboard():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_q]:
                return
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                button(pygame.K_s)

        pressed = pygame.key.get_pressed()

        if 1 in (pressed[pygame.K_DOWN], pressed[pygame.K_d]):
            if debounce(pygame.K_DOWN):
                button(pygame.K_DOWN)

        if 1 in (pressed[pygame.K_UP], pressed[pygame.K_u]):
            if debounce(pygame.K_UP):
                button(pygame.K_UP)
        
        if 1 in (pressed[pygame.K_LEFT], pressed[pygame.K_l]):
            if debounce(pygame.K_LEFT):
                button(pygame.K_LEFT)

        if 1 in (pressed[pygame.K_RIGHT], pressed[pygame.K_r]):
            if debounce(pygame.K_RIGHT):
                button(pygame.K_RIGHT)

        pygame.display.flip()


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
    run_game_loop_keyboard()
    #run_game_loop_serial()


if __name__ == "__main__":
    main()