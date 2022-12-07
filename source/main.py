import pygame
import os
import json
from random import choice
from time import time


pygame.init()
screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h
max_w, max_h = screen_width, screen_height
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
pygame.mouse.set_visible(False)
cur = pygame.transform.smoothscale(pygame.image.load('materials\\cur.png'), (60, 60))
level_name = ''
FPS = 60


# главное меню и перезагрузка цикла игры
def restart_or_menu(menu):
    global level_name, level_music, cur, level_img, level_data, start_time, active_circles, ac_times, letter_count, difficult, screen, screen_width, screen_height, FPS, score_board
    if menu:
        difficult = 'medium'
        menu_song = pygame.mixer.Sound('materials//menu_mc.mp3')
        menu_song.play()
        song_list = [arg[1] for arg in os.walk('songs')][0]
        level_name = ''
        pr = 0
        p_change = False
        def refactor():
            menu_image = pygame.image.load('materials//menu_bg.jpg')
            menu_image = pygame.transform.smoothscale(menu_image, (screen_width, screen_height))
            screen.blit(menu_image, menu_image.get_rect(center=(screen_width // 2, screen_height // 2)))
            buttons = []
            y = 100 * (screen_height / 1080)
            for i, elem in enumerate(song_list):
                nmb = pr_text(txt=elem, n=40, cord=(screen_width // 2, y), color=(253, 149, 253))
                buttons.append(Button(nmb.topleft[0] - 5, nmb.topleft[1] - 5, nmb.width + 10, nmb.height + 10, tp='song',
                                      data=i))
                y += 75 * (screen_height / 1080)
            diff_box = ComboBox('difficulty', (75 * (screen_width / 1920), 20 * (screen_height / 1080)),
                                [['normal', 'normal'], ['medium', 'medium'], ['hard', 'hard'],
                                 ['insane', 'insane'], ['psycho', 'psycho']])
            diff_box.objects[1].is_choice = True
            resolutions = [(1600, 900), (1920, 1080), (2560, 1440), (3840, 2160)]
            res_box = ComboBox('resolution', (250 * (screen_width / 1920), 20 * (screen_height / 1080)),
                               [(i, f'{i[0]}*{i[1]}') for i in resolutions[:resolutions.index((max_w, max_h)) + 1]])
            res_box.objects[resolutions.index((screen_width, screen_height))].is_choice = True
            frame_box = ComboBox('frame rate', (425 * (screen_width / 1920), 20 * (screen_height / 1080)),
                                 [[30, '30 FPS'], [60, '60 FPS'], [120, '120 FPS'],
                                  [144, '144 FPS'], [165, '165 FPS']])
            frame_box.objects[[30, 60, 120, 144, 165].index(FPS)].is_choice = True
            boxes = [res_box, diff_box, frame_box]
            score_board = ScoreBoard()
            return menu_image, buttons, diff_box, boxes, score_board
        menu_image, buttons, diff_box, boxes, score_board = refactor()
        while not level_name:
            screen.blit(menu_image, menu_image.get_rect(center=(screen_width // 2, screen_height // 2)))
            pr_text(txt='Your songs:', n=50, cord=(screen_width // 2, 25 * (screen_height / 1080)), color=(253, 149, 253))
            y = 100 * (screen_height / 1080)
            if p_change:
                buttons.clear()
            for i, elem in enumerate(song_list[pr:]):
                nmb = pr_text(txt=elem, n=40, cord=(screen_width // 2, y), color=(253, 149, 253))
                if p_change:
                    buttons.append(
                        Button(nmb.topleft[0] - 5, nmb.topleft[1] - 5, nmb.width + 10, nmb.height + 10, tp='song',
                               data=i))
                y += 75 * (screen_height / 1080)
            p_change = False
            for button in buttons:
                button.is_click()
            for elem in boxes:
                elem.blit()
                elem.is_click(False)
            cx, cy = pygame.mouse.get_pos()
            screen.blit(cur, cur.get_rect(center=(cx, cy)))
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for elem in boxes:
                        elem.is_click()
                        if elem.get_data():
                            box_data = elem.get_data()
                            if box_data[0] == 'resolution' and box_data[1] != (screen_width, screen_height):
                                screen_width, screen_height = box_data[1]
                                screen = pygame.display.set_mode(box_data[1])
                                menu_image, buttons, diff_box, boxes, score_board = refactor()
                            if box_data[0] == 'difficulty':
                                difficult = box_data[1]
                            if box_data[0] == 'frame rate':
                                FPS = box_data[1]
                    for button in buttons:
                        if button.is_click():
                            level_name = song_list[button.data]
                if event.type == pygame.MOUSEBUTTONDOWN:
                    p_change = True
                    if event.button == 4:
                        if pr < len(song_list) - 1:
                            pr += 1
                    elif event.button == 5:
                        if pr > 0:
                            pr -= 1
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    quit()
            clock.tick(FPS)
            pygame.display.update()
        menu_song.stop()
        level_music = pygame.mixer.Sound('songs\\' + level_name + '\\' + 'song.mp3')
        level_img = pygame.transform.smoothscale(pygame.image.load('songs\\' + level_name + '\\' + 'bg.jpg'),
                                                 (screen_width, screen_height))
        with open('songs\\' + level_name + '\\' + 'level.json') as f:
            level_data = json.load(f)
    srf = pygame.Surface((screen_width, screen_height))
    srf.fill((0, 0, 0))
    c = pygame.time.Clock()
    for i in range(1, FPS):
        srf.set_alpha(255 * (i / FPS))
        screen.blit(srf, (0, 0))
        pygame.display.update()
        c.tick(FPS)
    for i in range(FPS, 1, -1):
        draw_bg()
        srf.set_alpha(255 * (i / FPS))
        screen.blit(srf, (0, 0))
        pygame.display.update()
        c.tick(FPS)
    active_circles = []
    ac_times = []
    level_music.play()
    start_time = time()
    letter_count = 0


# вывод текста с центровкой или без, возвращает прямоугольник текста
def pr_text(txt, cord, n=20, color=(255, 255, 255), ctr=True, frmt=False):
    n = int(n * (screen_width / 1920))
    font = pygame.font.SysFont('roboto', n)
    text = font.render(txt, True, color)
    if frmt:
        return text.get_rect(center=cord)
    if ctr:
        text_rect = text.get_rect(center=cord)
        screen.blit(text, text_rect)
    else:
        screen.blit(text, cord)
    return text.get_rect(center=cord)


def draw_bg():
    screen.blit(level_img, level_img.get_rect(center=(screen_width // 2, screen_height // 2)))


class Button:
    def __init__(self, x, y, w=0, h=0, data=None, tp='default', text=None) -> None:
        self.x = x
        self.y = y
        if text:
            self.text = text
            nmb = pr_text(txt=text, n=30, cord=(x, y), color=(253, 149, 253), frmt=True)
            self.w = nmb.width + 10
            self.h = nmb.height + 10
        else:
            self.w = w
            self.h = h
        self.data = data
        self.type = tp
        self.heatbox = pygame.Rect(x, y, self.w, self.h)
        self.sound = pygame.mixer.Sound('materials\\button_sd.mp3')
        self.last_light = False
        self.img = pygame.image.load('materials\\button_ch.png')
        self.img = pygame.transform.smoothscale(self.img, (50, 50))
        self.is_choice = False

    def is_click(self, p=False):
        x, y = pygame.mouse.get_pos()
        if self.heatbox.collidepoint(x, y):
            if p:
                self.is_choice = True
            self.light()
            if not self.last_light:
                self.sound.play()
            self.last_light = True
            return True
        else:
            self.last_light = False

    def text_blit(self):
        pr_text(txt=self.text, n=30, cord=(self.x + 5, self.y + 5), color=(253, 149, 253), ctr=False)
        if self.is_choice:
            screen.blit(self.img, self.img.get_rect(center=(self.x + self.w + 20, self.y + 15)))

    def light(self):
        color = (168, 162, 252)
        pygame.draw.rect(screen, color, self.heatbox, 5)


class Circle:
    def __init__(self, x, y, speed):
        global letter_count, difficult
        self.x = int(x * (screen_width / 1920))
        self.y = int(y * (screen_height / 1080))
        self.speed = speed * (60 / FPS)
        if difficult == 'normal':
            self.letter = 'c'
        elif difficult == 'medium':
            self.letter = ['c', 'x'][letter_count % 2]
        elif difficult == 'hard':
            self.letter = ['z', 'x', 'c'][letter_count % 3]
        elif difficult == 'insane':
            self.letter = choice(['c', 'x'])
        elif difficult == 'psycho':
            self.letter = choice(['z', 'c', 'x'])
        letter_count += 1
        self.lower_p = 35
        self.upper_p = 53
        self.key = pygame.K_z if self.letter == 'z' else pygame.K_x if self.letter == 'x' else pygame.K_c
        self.stade = 0
        self.col_stade = None
        self.dead_stade = None
        self.heatbox = pygame.Rect(self.x, self.y, 120, 120)
        self.sound = pygame.mixer.Sound('materials\\circle_click.mp3')
        self.fail_img = pygame.transform.smoothscale(pygame.image.load('materials\\circ_fail.png'), (75, 75))
        self.suc_img = pygame.transform.smoothscale(pygame.image.load('materials\\circ_suc.png'), (75, 75))

    def blit(self):
        if self.col_stade:
            return
        pygame.draw.circle(screen, (66, 170, 255), (self.x, self.y), self.stade)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, self.y), 50, 3)
        pr_text(txt=self.letter, n=70, color=(253, 149, 253), cord=(self.x, self.y))
        self.stade += self.speed

    def collision(self, x, y):
        if self.dead_stade:
            return
        if self.stade > self.upper_p:
            self.col_stade = 1
            if not self.dead_stade:
                self.dead_stade = 1
                return -1
            return
        if self.heatbox.collidepoint(x, y) and pygame.key.get_pressed()[self.key]:
            self.sound.play()
            self.col_stade = self.stade
            self.dead_stade = 1
            return 1

    def blit_res(self):
        self.dead_stade += 1
        if self.col_stade < self.lower_p:
            screen.blit(self.fail_img, self.fail_img.get_rect(center=(self.x, self.y)))
        else:
            screen.blit(self.suc_img, self.suc_img.get_rect(center=(self.x, self.y)))


class ComboBox:
    def __init__(self, name, cords, args):
        self.x = cords[0]
        self.y = cords[1]
        self.name = name
        self.sound = pygame.mixer.Sound('materials\\button_sd.mp3')
        self.last_light = False
        self.objects = []
        self.anim_step = 0.05
        y = self.y + 25 * (screen_height / 1080)
        self.active = False
        for elem in args:
            obj = Button(x=self.x + 50 * (screen_width / 1920) - 5, y=y - 5, data=elem[0], text=elem[1], tp=name)
            self.objects.append(obj)
            y += 50
        data = pr_text(txt=self.name, n=35, cord=(self.x, self.y), color=(253, 149, 253))
        self.heatbox = pygame.Rect(data.x - 5, data.y - 5, data.w + 10, data.h + 10)
        self.animated_stade = 1

    def is_click(self, p=True):
        x, y = pygame.mouse.get_pos()
        if self.heatbox.collidepoint(x, y):
            if p:
                self.active = not self.active
                if not self.active:
                    self.animated_stade = self.anim_step * len(self.objects) * FPS
                else:
                    self.animated_stade = 1
            self.light()
            if not self.last_light:
                self.sound.play()
            self.last_light = True
            return True
        else:
            self.last_light = False

    def blit(self):
        pr_text(txt=self.name, n=35, cord=(self.x, self.y), color=(253, 149, 253))
        if self.active:
            max_anim = self.anim_step * len(self.objects) * FPS
            if self.animated_stade < max_anim:
                for obj in self.objects[:int(self.animated_stade // (self.anim_step * FPS))]:
                    obj.is_click()
                    obj.text_blit()
                self.animated_stade += 1
            else:
                for obj in self.objects:
                    obj.is_click()
                    obj.text_blit()
        else:
            if self.animated_stade > 0:
                for obj in self.objects[:int(self.animated_stade // (self.anim_step * FPS))]:
                    obj.is_click()
                    obj.text_blit()
                self.animated_stade -= 1

    def get_data(self):
        if self.active:
            for obj in self.objects:
                if obj.is_click(True):
                    for o in self.objects:
                        if o == obj:
                            continue
                        o.is_choice = False
                    return obj.type, obj.data

    def light(self):
        color = (168, 162, 252)
        pygame.draw.rect(screen, color, self.heatbox, 5)


class ScoreBoard:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.max_w = 500 * (screen_width / 1920)
        self.w = self.max_w
        self.h = 40 * (screen_height / 1080)
        self.image = pygame.transform.smoothscale(pygame.image.load('materials\\score_bg.jpg'),
                                                  (self.max_w, self.h))
        self.image.set_alpha(100)
        self.rect = self.image.get_rect(center=(x, y))
        self.max_price = 1
        self.player_price = 1

    def blit(self):
        img = pygame.transform.smoothscale(self.image, (self.w, self.h))
        screen.blit(img, img.get_rect(center=(self.x + self.w // 2, self.y + self.h // 2)))
        ac = round(self.player_price / self.max_price * 100, 2)
        text_x = self.x + self.w + 40 * (screen_width / 1920)
        pr_text(txt=f'{ac}%', cord=(text_x, self.y + self.h // 2), n=30, color=(168, 162, 252))

    def update_score(self, data):
        if data[0] == 'circle':
            self.max_price += 50
            if data[1] == 1:
                self.player_price += 50
        self.w = self.max_w * (self.player_price / self.max_price)


restart_or_menu(True)
while True:
    draw_bg()
    x, y = pygame.mouse.get_pos()
    cur_time = round(time() - start_time, 1)
    if str(cur_time) in level_data and cur_time not in ac_times:
        data = level_data[str(cur_time)]
        ac_times.append(cur_time)
        for d in data:
            if d[0] == 'circle':
                active_circles.append(Circle(d[1], d[2], d[3]))
    for circle in active_circles:
        score = circle.collision(x, y)
        if score:
            score_board.update_score(['circle', score])
        if not circle.col_stade:
            circle.blit()
        else:
            circle.blit_res()
            if circle.dead_stade > 30:
                del active_circles[active_circles.index(circle)]
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            level_music.stop()
            restart_or_menu(True)
    screen.blit(cur, cur.get_rect(center=(x, y)))
    score_board.blit()
    pygame.display.update()
    clock.tick(FPS)
