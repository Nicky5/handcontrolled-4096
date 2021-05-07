import math
import random
import threading
import time

import pygame as pg

BACKGROUND = (250, 248, 239)

COLOR1 = (205, 193, 180)

COLOR2 = (187, 173, 160)

pg.init()
screen = pg.display.set_mode((1792, 896), pg.RESIZABLE)
pg.display.set_caption('4096')

running = True
animation_time = 0.2
start_time = time.time() - animation_time
frame = 0
width = 11
side_lenght = 748 + width
piece_lenght = 176
pieces = []
obstacles = []
to_upgrade = []
animation_start = time.time()
colors = [(243, 234, 225), (238, 227, 206), (244, 184, 135), (247, 159, 115), (246, 137, 111), (247, 110, 81),
          (239, 211, 127), (239, 209, 113), (238, 238, 98), (239, 203, 83), (244, 207, 75), (82, 77, 72)]

canvas = pg.Surface((side_lenght, side_lenght))
canvas.fill(COLOR1)

pg.font.init()
myfont = pg.font.SysFont('Comic Sans MS', 30)

def dbg_label(Print=False, *args, **kwargs):
    label = myfont.render(f"{args, kwargs}", True, COLOR2)
    fill_block(screen, (BACKGROUND, ((0, 0), (screen.get_width(), 30))))
    screen.blit(label, (0, 0))
    if Print:
        print(args, kwargs)

def Label(pos, args):
    label = myfont.render(f"{args}", True, COLOR2)
    fill_block(screen, (BACKGROUND, (pos, (screen.get_width(), 30))))
    screen.blit(label, pos)

def get_animation_offset():
    return - ((animation_start - time.time()) * (1 / animation_time))

def fill_block(frame, Input):
    (r, g, b), ((x, y), (i, j)) = Input
    if x < 0:
        i -= 0 - x
    if y < 0:
        j -= 0 - y
    frame.fill((r, g, b), ((x, y), (i, j)))

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
    time.sleep(animation_time)
    obstacles.clear()
    for i in to_upgrade:
        for x in pieces:
            if i == x.id:
                x.upfate_value()
                piece.game_score += int(x.value)
    if piece.game_score > piece.best_score:
        piece.best_score = piece.game_score
    pieces.append(piece())
    to_upgrade.clear()

class piece:
    game_score = 0
    moves = 0
    best_score = game_score
    colors = [(243, 234, 225), (238, 227, 206), (244, 184, 135), (247, 159, 115), (246, 137, 111), (247, 110, 81),
              (239, 211, 127), (239, 209, 113), (238, 238, 98), (239, 203, 83), (244, 207, 75), (82, 77, 72)]

    def __init__(self):
        self.id = random.randint(0, 2147483647)
        self.moving = False
        self.power = 1
        self.grid_y, self.grid_x = get_free_spawn()
        self.x, self.y = (get_piece_start(self.grid_x), get_piece_start(self.grid_y))
        self.prev_x, self.prev_y = self.get_temp_x(), self.get_temp_y()
        self.value = 2
        self.priority = 0
        self.color = colors[0]
        self.upfate_value()

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
        canvas.fill(self.color, ((self.get_x(), self.get_y()), (piece_lenght, piece_lenght)))
        textsurface = myfont.render(str(self.value), False, self.get_font_color())
        canvas.blit(textsurface, (self.get_x() + (piece_lenght // 2) - (textsurface.get_width() // 2),
                                  self.get_y() + (piece_lenght // 2) - (textsurface.get_height() // 2)))

    def upfate_value(self):
        self.value = str(int(math.pow(2, self.power)))
        self.color = self.get_color()

    def get_temp_x(self):
        return get_piece_start(self.grid_x)

    def get_temp_y(self):
        return get_piece_start(self.grid_y)

    def get_color(self):
        try:
            return colors[self.power - 1]
        except IndexError:
            return 82, 77, 72

    def get_font_color(self):
        if self.power > 2:
            return 255, 255, 255
        return 31, 30, 26

    def get_x(self):
        if animation_start + animation_time > time.time():
            return self.prev_x + ((self.get_temp_x() - self.prev_x) * (get_animation_offset()))
        self.prev_x = self.get_temp_x()
        return self.get_temp_x()

    def get_y(self):
        if animation_start + animation_time > time.time():
            return self.prev_y + ((self.get_temp_y() - self.prev_y) * (get_animation_offset()))
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

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                running = False

        if event.type == pg.KEYDOWN:
            if not animation_start + animation_time > time.time():
                animation_start = time.time()
                if event.key == pg.K_UP:
                    priority = 0
                    for y in range(4):
                        for x in range(4):
                            if get_piece(y, x) is not None and to_upgrade.count(get_piece(y, x).id) == 0:
                                get_piece(y, x).priority = priority
                                priority += 1
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
                    priority = 0
                    for y in range(3, -1, -1):
                        for x in range(3, -1, -1):
                            if get_piece(y, x) is not None and to_upgrade.count(get_piece(y, x).id) == 0:
                                get_piece(y, x).priority = priority
                                priority += 1
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
                    priority = 0
                    for x in range(4):
                        for y in range(4):
                            if get_piece(y, x) is not None and to_upgrade.count(get_piece(y, x).id) == 0:
                                get_piece(y, x).priority = priority
                                priority += 1
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
                    priority = 0
                    for x in range(3, -1, -1):
                        for y in range(3, -1, -1):
                            if get_piece(y, x) is not None and to_upgrade.count(get_piece(y, x).id) == 0:
                                get_piece(y, x).priority = priority
                                priority += 1
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

    if elapsed_time > 0.05:
        frame += 1

        screen.fill(BACKGROUND)
        canvas.fill(COLOR1)
        for i in range(6):
            pg.draw.line(canvas, COLOR2, (i * (side_lenght - width) / 4 + (width // 2), 0),
                         (i * (side_lenght - width) / 4 + (width // 2), side_lenght), width)
            pg.draw.line(canvas, COLOR2, (0, i * (side_lenght - width) / 4 + (width // 2)),
                         (side_lenght, i * (side_lenght - width) / 4 + (width // 2)), width)

        for i in obstacles:
            i.render()

        for i in pieces:
            i.render()

        screen.blit(canvas, (getGroundStart(), getGroundStart()))
        Label((screen.get_width() // 2 - canvas.get_width() // 2, screen.get_height() // 2 - canvas.get_width() // 2 - 50), "Score: " + str(piece.game_score))
        Label((screen.get_width() // 2 - canvas.get_width() // 2 + 200, screen.get_height() // 2 - canvas.get_width() // 2 - 50),
              "Highscore: " + str(piece.best_score))
        Label((screen.get_width() // 2 - canvas.get_width() // 2 + 500, screen.get_height() // 2 - canvas.get_width() // 2 - 50), "Moves: " + str(piece.moves))
        pg.display.update()
