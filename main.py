import json
import math
import random
import threading
import time

import cv2
import pygame as pg

hand_detection = True
cam = pg.Surface((640, 480))
indikator = pg.Surface((40, 40))
loop_on = True
Hand_open = False
cam_fps = 0

data = json.load(open('settings.json'))

class set:
    loop_on = True
    mode = data["mode"]
    BACKGROUND = data[mode]["background"]
    COLOR1 = data[mode]["color1"]
    COLOR2 = data[mode]["color2"]
    animation_time = data["animationTime"]
    size = data["size"]
    colors = data[mode]["pieces"]
    font = data["font"]
    best_score = data["highscore"]
    font_color1 = data[mode]["fontColor1"]
    font_color2 = data[mode]["fontColor2"]

    @staticmethod
    def update_settings(only_colors=False):
        data = json.load(open('settings.json'))
        set.colors = data[set.mode]["pieces"]
        set.BACKGROUND = data[set.mode]["background"]
        set.COLOR1 = data[set.mode]["color1"]
        set.COLOR2 = data[set.mode]["color2"]
        set.font_color1 = data[set.mode]["fontColor1"]
        set.font_color2 = data[set.mode]["fontColor2"]
        if only_colors:
            return
        set.mode = data["mode"]
        set.animation_time = data["animationTime"]
        set.size = data["size"]
        set.font = data["font"]
        set.best_score = data["highscore"]

indikator.fill(set.BACKGROUND)
pg.draw.circle(indikator, (255, 0, 0), (20, 20), 20)

pg.init()
screen = pg.display.set_mode(set.size, pg.RESIZABLE)
pg.display.set_caption('4096')

running = True
start_time = time.time() - set.animation_time
frame = 0
width = 11
side_lenght = 748 + width
piece_lenght = 176
pieces = []
obstacles = []
to_upgrade = []
animation_start = time.time()

canvas = pg.Surface((side_lenght, side_lenght))

pg.font.init()
myfont = pg.font.SysFont(set.font, 30)

fonts = [pg.font.SysFont(set.font, 100 - (i * 20)) for i in range(10)]

def Label(pos, args):
    label = myfont.render(f"{args}", True, set.font_color2)
    screen.fill(set.BACKGROUND, (pos, (screen.get_width(), 30)))
    screen.blit(label, pos)

def get_animation_progres():
    return - ((animation_start - time.time()) * (1 / set.animation_time))

def get_piece_start(piece):
    return (piece * (piece_lenght + width)) + width

def get_free_spawn():
    if len(pieces) > 15:
        pieces.clear()
        piece.game_score = 0
        piece.moves = 0
    ok = True
    while ok:
        y, x = (random.randint(0, 3), random.randint(0, 3))
        if (y, x) not in [(i.grid_y, i.grid_x) for i in pieces]:
            return y, x

def get_piece(y, x):
    pos = [(i.grid_y, i.grid_x) for i in pieces]
    if pos.count((y, x)) == 0:
        return None
    else:
        return pieces[pos.index((y, x))]

def after_animation():
    piece.moves += 1
    time.sleep(set.animation_time)
    obstacles.clear()
    for i in to_upgrade:
        for x in pieces:
            if i == x.id:
                x.update_value()
                piece.game_score += int(x.value)
    if piece.game_score > set.best_score:
        set.best_score = piece.game_score
    pieces.append(piece())
    to_upgrade.clear()
    for i in pieces:
        i.update_value()

class piece:
    game_score = 0
    moves = 0

    def __init__(self):
        self.id = random.randint(0, 2147483647)
        self.power = 1
        self.grid_y, self.grid_x = get_free_spawn()
        self.x, self.y = (get_piece_start(self.grid_x), get_piece_start(self.grid_y))
        self.prev_x, self.prev_y = self.get_temp_x(), self.get_temp_y()
        self.value = 2
        self.update_value()

    def move(self, y, x):
        if (y, x) == (self.grid_y, self.grid_x):
            return
        elif get_piece(y, x) is not None and get_piece(y, x).power == self.power and to_upgrade.count(
                get_piece(y, x).id) == 0:
            obstacles.append(get_piece(y, x))
            pieces.remove(get_piece(y, x))
            self.power += 1
            to_upgrade.append(self.id)
        self.prev_x, self.prev_y = self.get_temp_x(), self.get_temp_y()
        self.grid_y, self.grid_x = y, x

    def render(self):
        canvas.fill(self.get_color(), ((self.get_x(), self.get_y()), (piece_lenght, piece_lenght)))
        textsurface = fonts[len(str(self.value)) - 1].render(str(self.value), False, self.get_font_color())
        canvas.blit(textsurface, (self.get_x() + (piece_lenght // 2) - (textsurface.get_width() // 2),
                                  self.get_y() + (piece_lenght // 2) - (textsurface.get_height() // 2)))

    def update_value(self):
        self.value = str(int(math.pow(2, self.power)))

    def get_temp_x(self):
        return get_piece_start(self.grid_x)

    def get_temp_y(self):
        return get_piece_start(self.grid_y)

    def get_color(self):
        try:
            return set.colors[int(math.sqrt(int(self.value)) - 1)]
        except IndexError:
            return set.colors[0]

    def get_font_color(self):
        if int(self.value) > 4:
            return set.font_color1
        return set.font_color2

    def get_x(self):
        if animation_start + set.animation_time > time.time():
            return self.prev_x + ((self.get_temp_x() - self.prev_x) * (get_animation_progres()))
        self.prev_x = self.get_temp_x()
        return self.get_temp_x()

    def get_y(self):
        if animation_start + set.animation_time > time.time():
            return self.prev_y + ((self.get_temp_y() - self.prev_y) * (get_animation_progres()))
        self.prev_y = self.get_temp_y()
        return self.get_temp_y()

def get_ground_start():
    return screen.get_width() // 4 - 384, screen.get_height() // 2 - 384

def move_piece(inp):
    print(inp)
    if inp == pg.K_UP or inp == 'up':
        for y in range(4):
            for x in range(4):
                if get_piece(y, x) is not None and to_upgrade.count(get_piece(y, x).id) == 0:
                    free_spot = y
                    for i in range(y, -1, -1):
                        if get_piece(i, x) is None:
                            free_spot = i
                    if get_piece(free_spot - 1, x) is not None and get_piece(y, x).power == get_piece(
                            free_spot - 1, x).power and to_upgrade.count(get_piece(
                        free_spot - 1, x).id) == 0:
                        get_piece(y, x).move(free_spot - 1, x)
                    else:
                        get_piece(y, x).move(free_spot, x)

    if inp == pg.K_DOWN or inp == 'down':
        for y in range(3, -1, -1):
            for x in range(3, -1, -1):
                if get_piece(y, x) is not None and to_upgrade.count(get_piece(y, x).id) == 0:
                    free_spot = y
                    for i in range(y, 4):
                        if get_piece(i, x) is None:
                            free_spot = i
                    if get_piece(free_spot + 1, x) is not None and get_piece(y, x).power == get_piece(
                            free_spot + 1, x).power and to_upgrade.count(get_piece(
                        free_spot + 1, x).id) == 0:
                        get_piece(y, x).move(free_spot + 1, x)
                    else:
                        get_piece(y, x).move(free_spot, x)

    if inp == pg.K_LEFT or inp == 'left':
        for x in range(4):
            for y in range(4):
                if get_piece(y, x) is not None and to_upgrade.count(get_piece(y, x).id) == 0:
                    free_spot = x
                    for i in range(x, -1, -1):
                        if get_piece(y, i) is None:
                            free_spot = i
                    if get_piece(y, free_spot - 1) is not None and get_piece(y, x).power == get_piece(y,
                                                                                                      free_spot - 1).power and to_upgrade.count(
                        get_piece(
                            y, free_spot - 1).id) == 0:
                        get_piece(y, x).move(y, free_spot - 1)
                    else:
                        get_piece(y, x).move(y, free_spot)

    if inp == pg.K_RIGHT or inp == 'right':
        for x in range(3, -1, -1):
            for y in range(3, -1, -1):
                if get_piece(y, x) is not None and to_upgrade.count(get_piece(y, x).id) == 0:
                    free_spot = x
                    for i in range(x, 4):
                        if get_piece(y, i) is None:
                            free_spot = i
                    if get_piece(y, free_spot + 1) is not None and get_piece(y, x).power == get_piece(y,
                                                                                                      free_spot + 1).power and to_upgrade.count(
                            get_piece(y, free_spot + 1).id) == 0:
                        get_piece(y, x).move(y, free_spot + 1)
                    else:
                        get_piece(y, x).move(y, free_spot)

def game_loop():
    pieces.append(piece())
    while set.loop_on:
        current_time = time.time()
        elapsed_time = current_time - start_time

        for event in pg.event.get():
            if event.type == pg.QUIT:
                set.loop_on = False
                cv2.destroyAllWindows()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    set.loop_on = False
                    cv2.destroyAllWindows()

                if event.key == pg.K_TAB:
                    if set.mode == "light":
                        set.mode = "dark"
                    else: set.mode = "light"
                    set.update_settings(True)

                if event.key == pg.K_r:
                    set.update_settings()

                if event.key == pg.K_RSHIFT:
                    pieces.append(piece())

                if event.key == pg.K_UP or event.key == pg.K_DOWN or event.key == pg.K_LEFT or event.key == pg.K_RIGHT:
                    # if not animation_start + set.animation_time > time.time():
                        animation_start = time.time()
                        # move_piece(event.key)
                        threading.Thread(target=move_piece, args=event.key).start()
                        threading.Thread(target=after_animation).start()

        if elapsed_time > (1 / 1):
            screen.fill(set.BACKGROUND)
            canvas.fill(set.COLOR1)
            for i in range(6):
                pg.draw.line(canvas, set.COLOR2, (i * (side_lenght - width) / 4 + (width // 2), 0),
                             (i * (side_lenght - width) / 4 + (width // 2), side_lenght), width)
                pg.draw.line(canvas, set.COLOR2, (0, i * (side_lenght - width) / 4 + (width // 2)),
                             (side_lenght, i * (side_lenght - width) / 4 + (width // 2)), width)
            for i in obstacles:
                i.render()
            for i in pieces:
                i.render()
            screen.blit(canvas, (get_ground_start(), get_ground_start()))
            Label((screen.get_width() // 4 - canvas.get_width() // 2, screen.get_height() // 2 - canvas.get_width() // 2 - 50), "Score: " + str(piece.game_score))
            Label((screen.get_width() // 4 - canvas.get_width() // 2 + 200, screen.get_height() // 2 - canvas.get_width() // 2 - 50), "Highscore: " + str(set.best_score))
            Label((screen.get_width() // 4 - canvas.get_width() // 2 + 500, screen.get_height() // 2 - canvas.get_width() // 2 - 50), "Moves: " + str(piece.moves))

            screen.blit(cam, (screen.get_width() // 2 + 0, screen.get_height() // 2 - 264))
            Label((screen.get_width() // 4 - canvas.get_width() // 2 + 700, screen.get_height() // 2 - canvas.get_width() // 2 - 50), f'FPS: {int(cam_fps)}')
            Label((screen.get_width() // 4 - canvas.get_width() // 2, screen.get_height() // 2 - canvas.get_width() // 2 - 100), 'https://github.com/Nicky5/handcontrolled-4096')
            if Hand_open:
                screen.blit(indikator, (screen.get_width() // 4 - canvas.get_width() // 2 + 700, screen.get_height() // 2 - canvas.get_width() // 2 - 100))

            pg.display.update()
            print('game loop')