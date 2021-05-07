import json
import math
import random
import threading
import time

import pygame as pg

data = json.load(open('settings.json'))

class set:
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
    fps = data["fps"]

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
        set.fps = data["fps"]


    @staticmethod
    def save_settings():
        data["mode"] = set.mode
        data["animationTime"] = set.animation_time
        data["size"] = (screen.get_width(), screen.get_height())
        data["highscore"] = set.best_score
        json.dump(data, open('settings.json', 'w'))

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

def getGroundStart():
    return screen.get_width() // 2 - 384, screen.get_height() // 2 - 384

pieces.append(piece())
while running:
    current_time = time.time()
    elapsed_time = current_time - start_time

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            set.save_settings()

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False
                set.save_settings()

            if event.key == pg.K_TAB:
                if set.mode == "light":
                    set.mode = "dark"
                else: set.mode = "light"
                set.update_settings(True)

            if event.key == pg.K_r:
                set.update_settings()

            if event.key == pg.K_s:
                set.save_settings()

            if event.key == pg.K_RSHIFT:
                pieces.append(piece())

            if event.key == pg.K_UP or event.key == pg.K_DOWN or event.key == pg.K_LEFT or event.key == pg.K_RIGHT:
                if not animation_start + set.animation_time > time.time():
                    animation_start = time.time()
                    if event.key == pg.K_UP:
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

                    if event.key == pg.K_DOWN:
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

                    if event.key == pg.K_LEFT:
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

                    if event.key == pg.K_RIGHT:
                        for x in range(3, -1, -1):
                            for y in range(3, -1, -1):
                                if get_piece(y, x) is not None and to_upgrade.count(get_piece(y, x).id) == 0:
                                    free_spot = x
                                    for i in range(x, 4):
                                        if get_piece(y, i) is None:
                                            free_spot = i
                                    if get_piece(y, free_spot + 1) is not None and get_piece(y, x).power == get_piece(y, free_spot + 1).power and to_upgrade.count(get_piece(y, free_spot + 1).id) == 0:
                                        get_piece(y, x).move(y, free_spot + 1)
                                    else:
                                        get_piece(y, x).move(y, free_spot)
                    thread = threading.Thread(target=after_animation)
                    thread.start()

    if elapsed_time > (1 / set.fps):
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
        screen.blit(canvas, (getGroundStart(), getGroundStart()))
        Label((screen.get_width() // 2 - canvas.get_width() // 2, screen.get_height() // 2 - canvas.get_width() // 2 - 50), "Score: " + str(piece.game_score))
        Label((screen.get_width() // 2 - canvas.get_width() // 2 + 200, screen.get_height() // 2 - canvas.get_width() // 2 - 50), "Highscore: " + str(set.best_score))
        Label((screen.get_width() // 2 - canvas.get_width() // 2 + 500, screen.get_height() // 2 - canvas.get_width() // 2 - 50), "Moves: " + str(piece.moves))
        pg.display.update()
