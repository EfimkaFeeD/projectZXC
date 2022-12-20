import os
import pygame
import pygame_widgets
import json
from tkinter import filedialog
from screeninfo import get_monitors
from pygame_widgets.button import ButtonArray, Button
from pygame_widgets.dropdown import Dropdown
from pygame_widgets.widget import WidgetHandler
from pygame_widgets.slider import Slider
from pygame_widgets.progressbar import ProgressBar
from random import choice


# Необходимо для определения разрешения по неясным причинам
get_monitors()

# Предопределение основных переменных
resolutions = [(1600, 900), (1920, 1080), (2560, 1440), (3840, 2160)]
fps = 60
pygame.init()
screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h
max_w, max_h = screen_width, screen_height
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()


# Переопределение класса из библиотеки для добавления возможности убирания заднего фона
class NewButtonArray(ButtonArray):
    def __init__(self, win, x, y, width, height, shape, **kwargs):
        super().__init__(win, x, y, width, height, shape, **kwargs)
        self.invisible = kwargs.get('invisible', False)

    def draw(self):
        if not self._hidden:
            rects = [
                (self._x + self.borderRadius, self._y, self._width - self.borderRadius * 2, self._height),
                (self._x, self._y + self.borderRadius, self._width, self._height - self.borderRadius * 2)
            ]

            circles = [
                (self._x + self.borderRadius, self._y + self.borderRadius),
                (self._x + self.borderRadius, self._y + self._height - self.borderRadius),
                (self._x + self._width - self.borderRadius, self._y + self.borderRadius),
                (self._x + self._width - self.borderRadius, self._y + self._height - self.borderRadius)
            ]
            if not self.invisible:
                for rect in rects:
                    pygame.draw.rect(self.win, self.colour, rect)

            for circle in circles:
                pygame.draw.circle(self.win, self.colour, circle, self.borderRadius)

            for button in self.buttons:
                button.draw()


# Анимация затухания
def close_animation():
    surface = pygame.Surface((screen_width, screen_height))
    surface.fill((0, 0, 0))
    for i in range(1, fps):
        surface.set_alpha(int(255 * (i / fps)))
        screen.blit(surface, (0, 0))
        pygame.display.update()
        clock.tick(fps)


# Класс главного меню
class Menu:
    def __init__(self, args):
        self.running = True
        self.difficult = args[1]
        self.menu_song = pygame.mixer.Sound('materials//menu_mc.mp3')
        self.menu_song.play(-1)
        self.return_sound = pygame.mixer.Sound('materials//return.mp3')
        self.confirm_exit_buttons = None
        self.song_list = [arg[1] for arg in os.walk('songs')][0]
        self.level_name = ''
        self.menu_image = pygame.image.load('materials//menu_bg.jpg')
        self.menu_image = pygame.transform.smoothscale(self.menu_image, (screen_width, screen_height))
        self.buttons = []
        self.script = ''
        self.buttons_scroll = 0
        self.buttons_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(15 * (screen_width / 1920)))
        self.buttons_font_color = (255, 255, 255)
        self.buttonArray = self.generate_song_button_array()
        self.FPS_dropdown_menu = self.generate_fps_dropdown_menu()
        self.difficulty_dropdown_menu = self.generate_difficulty_dropdown_menu()
        self.resolution_dropdown_menu = self.generate_resolution_dropdown_menu()
        self.confirm_button = self.generate_confirm_button()
        self.add_song_button = self.generate_add_song_button()
        self.volume_level = args[0]
        if args[2]:
            self.menu_song.set_volume(0)
        self.volume_slider = self.generate_volume_slider()
        self.mute_button = self.generate_mute_button()
        self.start_animation()

    # Создание списка кнопок треков
    def generate_song_button_array(self, text=None):
        texts = self.song_list if not text else text
        width = 500 * (screen_width / 1920)
        height = (60 * (screen_height / 1080) + 30 * (screen_height / 1080)) * len(texts)
        song_button_array = NewButtonArray(
            screen,
            int(screen_width // 2 - width // 2),
            int(150 * (screen_height / 1080)),
            int(width),
            int(height),
            (1, len(texts)),
            border=30 * (screen_height / 1080),
            topBorder=0,
            bottomBorder=0,
            leftBorder=0,
            rightBorder=0,
            inactiveColours=[(77, 50, 145) for _ in range(len(texts))],
            hoverColours=[(54, 35, 103) for _ in range(len(texts))],
            pressedColours=[(121, 78, 230) for _ in range(len(texts))],
            radii=[int(25 * (screen_height / 1080)) for _ in range(len(self.song_list))],
            fonts=[self.buttons_font for _ in range(len(texts))],
            texts=[t if len(t) < 30 else t[:31] for t in texts],
            colour=(255, 255, 255),
            invisible=True,
            textColours=[self.buttons_font_color for _ in range(len(texts))],
            onClicks=[lambda x: self.set_run_config(x) for _ in range(len(texts))],
            onClickParams=[[i] for i in range(len(texts))]
        )
        return song_button_array

    # Создание списка кнопок сложностей
    def generate_difficulty_dropdown_menu(self):
        difficulty_drop_menu = Dropdown(
            screen, int(25 * (screen_width / 1920)), int(15 * (screen_height / 1080)),
            int(200 * (screen_width / 1920)), int(50 * (screen_height / 1080)), name='difficult',
            choices=[
                'normal',
                'medium',
                'hard',
                'insane',
                'psycho'
            ],
            borderRadius=int(25 * (screen_height / 1080)), direction='down', textHAlign='centre',
            font=self.buttons_font,
            inactiveColour=(77, 50, 145),
            hoverColour=(54, 35, 103),
            textColour=self.buttons_font_color,
            pressedColour=(121, 78, 230)
        )
        return difficulty_drop_menu

    # Создание списка кнопок разрешений экрана
    def generate_resolution_dropdown_menu(self):
        possible_resolutions = resolutions.copy()
        if (screen_width, screen_height) not in possible_resolutions:
            possible_resolutions.append((screen_width, screen_height))
        possible_resolutions.sort(key=lambda x: (x[0], x[1]))
        possible_resolutions = possible_resolutions[:possible_resolutions.index((max_w, max_h)) + 1]
        resolution_drop_menu = Dropdown(
            screen, screen_width - int(225 * (screen_width / 1920)), int(15 * (screen_height / 1080)),
            int(200 * (screen_width / 1920)),
            int(50 * (screen_height / 1080)), name='resolution',
            values=possible_resolutions,
            choices=[f'{resolution[0]}*{resolution[1]}' for resolution in possible_resolutions],
            borderRadius=int(25 * (screen_height / 1080)), direction='down', textHAlign='centre',
            font=self.buttons_font,
            inactiveColour=(77, 50, 145),
            textColour=self.buttons_font_color,
            hoverColour=(54, 35, 103),
            pressedColour=(121, 78, 230),
        )
        return resolution_drop_menu

    # Создание списка кнопок FPS
    def generate_fps_dropdown_menu(self):
        fps_drop_menu = Dropdown(
            screen, int(screen_width - 225 * (screen_width / 1920) * 2 - (30 * (screen_width / 1920))),
            int(15 * (screen_height / 1080)), int(200 * (screen_width / 1920)),
            int(50 * (screen_height / 1080)), name='frame rate',
            choices=['30', '60', '120', '144', '240'],
            borderRadius=int(25 * (screen_height / 1080)), direction='down', textHAlign='centre',
            font=self.buttons_font,
            textColour=self.buttons_font_color,
            inactiveColour=(77, 50, 145),
            hoverColour=(54, 35, 103),
            pressedColour=(121, 78, 230),
        )
        return fps_drop_menu

    # Создание ползунка громкости трека меню
    def generate_volume_slider(self):
        volume_slider = Slider(screen, int(50 * (screen_width / 1920)),
                               int(screen_height - 75 * (screen_height / 1080)),
                               int(250 * (screen_width / 1920)), int(50 * (screen_height / 1080)),
                               min=5, max=100, step=5, initial=self.volume_level,
                               colour=(77, 50, 145), handleColour=(121, 78, 230))
        pygame.display.update()
        return volume_slider

    # Переключение состояния музыки
    def toggle_mute(self):
        if self.menu_song.get_volume() != 0:
            self.menu_song.set_volume(0)
            WidgetHandler.removeWidget(self.mute_button)
            self.mute_button = self.generate_mute_button()
        else:
            self.menu_song.set_volume(self.volume_level)
            WidgetHandler.removeWidget(self.mute_button)
            self.mute_button = self.generate_mute_button()

    # Создание кнопки переключения состояния музыки
    def generate_mute_button(self):
        color = (255, 0, 0) if self.menu_song.get_volume() == 0 else self.buttons_font_color
        mute_button = Button(
            screen,
            int(350 * (screen_width / 1920)),
            screen_height - int(75 * (screen_height / 1080)),
            int(150 * (screen_width / 1920)),
            int(50 * (screen_height / 1080)),
            text='mute',
            radius=int(25 * (screen_height / 1080)),
            textColour=color,
            inactiveColour=(77, 50, 145),
            hoverColour=(54, 35, 103),
            pressedColour=(121, 78, 230),
            font=self.buttons_font,
            border=30 * (screen_height / 1080),
            onClick=lambda: self.toggle_mute()
        )
        return mute_button

    # Вывод текста и заднего фона
    def blit(self):
        screen.blit(self.menu_image, self.menu_image.get_rect(center=(screen_width // 2, screen_height // 2)))
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(50 * (screen_width / 1920)))
        songs_text = font.render('Your songs:', True, (124, 62, 249))
        songs_text_rect = songs_text.get_rect(center=(screen_width // 2, 50 * (screen_height / 1080)))
        screen.blit(songs_text, songs_text_rect)

    # Обновление всех виджетов
    def update_widgets(self, events):
        global running
        pygame_widgets.update(events)
        self.scroll_song_buttons(events)
        if self.menu_song.get_volume() != 0:
            self.menu_song.set_volume(self.volume_slider.getValue() / 100)
            self.volume_level = self.volume_slider.getValue()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.script = 'exit'
                self.running = False

    # Диалог подтверждения выхода из игры
    def confirm_exit(self, arg):
        global running
        if arg:
            self.running = False
            running = False
        else:
            self.buttonArray = self.generate_song_button_array()
            self.FPS_dropdown_menu = self.generate_fps_dropdown_menu()
            self.difficulty_dropdown_menu = self.generate_difficulty_dropdown_menu()
            self.resolution_dropdown_menu = self.generate_resolution_dropdown_menu()
            self.confirm_button = self.generate_confirm_button()
            self.add_song_button = self.generate_add_song_button()
            self.volume_slider = self.generate_volume_slider()
            self.mute_button = self.generate_mute_button()

    # Листание списка кнопок песен колёсиком мыши
    def scroll_song_buttons(self, events):
        if self.confirm_exit_buttons:
            return
        pos = pygame.mouse.get_pos()
        if not pygame.Rect(self.buttonArray.getX(), self.buttonArray.getY(), self.buttonArray.getWidth(),
                           screen_height).collidepoint(pos):
            return
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                WidgetHandler.removeWidget(self.buttonArray)
                if event.button == 5:
                    if self.buttons_scroll < len(self.song_list) - 1:
                        self.buttons_scroll += 1
                elif event.button == 4:
                    if self.buttons_scroll > 0:
                        self.buttons_scroll -= 1
                self.buttonArray = self.generate_song_button_array(text=self.song_list[self.buttons_scroll:])

    # Изменение под новое разрешение экрана
    def refactor(self, resolution):
        global screen_width, screen_height, screen
        screen_width, screen_height = resolution
        screen = pygame.display.set_mode((screen_width, screen_height))
        WidgetHandler.removeWidget(self.buttonArray)
        WidgetHandler.removeWidget(self.FPS_dropdown_menu)
        WidgetHandler.removeWidget(self.difficulty_dropdown_menu)
        WidgetHandler.removeWidget(self.resolution_dropdown_menu)
        WidgetHandler.removeWidget(self.confirm_button)
        WidgetHandler.removeWidget(self.add_song_button)
        WidgetHandler.removeWidget(self.volume_slider)
        WidgetHandler.removeWidget(self.mute_button)
        self.buttons_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(15 * (screen_width / 1920)))
        self.buttonArray = self.generate_song_button_array()
        self.FPS_dropdown_menu = self.generate_fps_dropdown_menu()
        self.difficulty_dropdown_menu = self.generate_difficulty_dropdown_menu()
        self.resolution_dropdown_menu = self.generate_resolution_dropdown_menu()
        self.confirm_button = self.generate_confirm_button()
        self.menu_image = pygame.transform.smoothscale(self.menu_image, (screen_width, screen_height))
        self.add_song_button = self.generate_add_song_button()
        self.volume_slider = self.generate_volume_slider()
        self.mute_button = self.generate_mute_button()

    # Создание кнопки подтверждения настроек
    def generate_confirm_button(self):
        confirm_button = Button(
            screen,
            screen_width - int(225 * (screen_width / 1920)),
            screen_height - int(75 * (screen_height / 1080)),
            int(200 * (screen_width / 1920)),
            int(50 * (screen_height / 1080)),
            text='confirm',
            radius=int(25 * (screen_height / 1080)),
            textColour=self.buttons_font_color,
            inactiveColour=(77, 50, 145),
            hoverColour=(54, 35, 103),
            pressedColour=(121, 78, 230),
            font=self.buttons_font,
            border=30 * (screen_height / 1080),
            onClick=self.confirm_settings
        )
        return confirm_button

    # Изменение настроек
    def confirm_settings(self):
        global fps
        new_fps = self.FPS_dropdown_menu.getSelected()
        new_resolution = self.resolution_dropdown_menu.getSelected()
        if new_fps:
            fps = int(new_fps)
        if new_resolution and new_resolution != (screen_width, screen_height):
            self.refactor(new_resolution)

    # Кнопка для открытия редактора нового уровня
    def generate_add_song_button(self):
        button = Button(screen, screen_width // 2 - int(37.5 * (screen_width / 1920)),
                        screen_height - int(87.5 * (screen_height / 1080)), int(75 * (screen_width / 1920)),
                        int(75 * (screen_height / 1080)), text='+', font=self.buttons_font,
                        textColour=self.buttons_font_color, inactiveColour=(77, 50, 145), hoverColour=(54, 35, 103),
                        pressedColour=(121, 78, 230), radius=75, border=30 * (screen_height / 1080),
                        onClick=self.run_redactor)
        add_button = button
        return add_button

    def run_redactor(self):
        self.script = 'redactor'
        self.running = False

    # Создания настроек для открытого уровня
    def set_run_config(self, index):
        self.level_name = self.song_list[index]
        diff = self.difficulty_dropdown_menu.getSelected()
        if diff:
            self.difficult = diff
        self.script = 'game'
        self.running = False

    # Цикл для вывода на экран
    def run(self):
        global running
        while self.running:
            self.blit()
            self.update_widgets(pygame.event.get())
            pygame.display.update()
        self.confirm_settings()
        if self.script != 'exit':
            close_animation()
            self.menu_song.stop()
        if running:
            WidgetHandler.removeWidget(self.buttonArray)
            WidgetHandler.removeWidget(self.FPS_dropdown_menu)
            WidgetHandler.removeWidget(self.difficulty_dropdown_menu)
            WidgetHandler.removeWidget(self.resolution_dropdown_menu)
            WidgetHandler.removeWidget(self.confirm_button)
            WidgetHandler.removeWidget(self.add_song_button)
            WidgetHandler.removeWidget(self.volume_slider)
            WidgetHandler.removeWidget(self.mute_button)

    # Анимация перехода на уровень
    def start_animation(self):
        surface = pygame.Surface((screen_width, screen_height))
        surface.fill((0, 0, 0))
        for i in range(fps, 1, -1):
            self.blit()
            self.update_widgets(pygame.event.get())
            surface.set_alpha(int(255 * (i / fps)))
            screen.blit(surface, (0, 0))
            pygame.display.update()
            clock.tick(fps)


# Основной класс игры
class Game:
    def __init__(self, level_name, difficult, volume):
        self.running = True
        self.level_music = pygame.mixer.Sound('songs\\' + level_name + '\\' + 'song.mp3')
        self.level_music.set_volume(volume / 100)
        self.level_background = pygame.transform.smoothscale(
            pygame.image.load('songs\\' + level_name + '\\' + 'bg.jpg'), (screen_width, screen_height))
        with open('songs\\' + level_name + '\\' + 'level.json') as f:
            self.level_data = json.load(f)
        self.difficult = difficult
        self.circle_key_step = -1
        self.frame = 0
        self.objects = self.create_object_list()
        self.start_animation()
        self.level_music.play()
        self.total_objects = 0
        self.successful_hits = 0
        self.bar_percent = 1
        self.bar_speed = 0.0005 * (60 / fps)
        self.score_delta = 0.1
        self.score_bar = self.generate_scorebar()

    # Анимация появления уровня
    def start_animation(self):
        surface = pygame.Surface((screen_width, screen_height))
        surface.fill((0, 0, 0))
        for i in range(fps, 1, -1):
            self.blit_background()
            surface.set_alpha(int(255 * (i / fps)))
            screen.blit(surface, (0, 0))
            pygame.display.update()
            clock.tick(fps)

    # Смена заднего фона на задний фон уровня
    def blit_background(self):
        screen.blit(self.level_background, (0, 0))

    def blit_accuracy(self):
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(20 * (screen_width / 1920)))
        if self.total_objects == 0:
            txt = '100%'
        elif self.successful_hits == 0:
            txt = '0%'
        else:
            txt = f'{round(self.successful_hits / self.total_objects * 100, 2)}%'
        render = font.render(txt, True, (124, 62, 249))
        screen.blit(render, (int(570 * (screen_width / 1920)), int(20 * (screen_height / 1080))))

    # Создание целей
    def create_object_list(self):
        objects = []
        for data in self.level_data["circles"]:
            objects.append(TargetCircle(frame=data['frame'], x=data["x"], y=data["y"], speed=data["speed"],
                                        radius=data["radius"], key=self.generate_key()))
        return objects

    # Расположение на уровне
    def object_events(self, events):
        WidgetHandler.removeWidget(self.score_bar)
        self.score_bar = self.generate_scorebar()
        for obj in self.objects:
            if obj.start_frame > self.frame:
                return
            data = obj.frame_update(events)
            if data[0]:
                if not obj.is_checked:
                    self.score(data[1])
                    obj.is_checked = True
                if data[2]:
                    del self.objects[self.objects.index(obj)]
                elif data[3]:
                    self.total_objects += 1

    # Создание нового кадра игры
    def generate_frame(self, events):
        self.blit_background()
        self.blit_accuracy()
        self.object_events(events)
        pygame_widgets.update(events)
        if self.check_exit_event(events):
            quit()
        self.frame += 1

    # Выход из игры в меню
    def check_exit_event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    # Цикл для вывода на экран
    def run(self):
        while self.running:
            self.generate_frame(pygame.event.get())
            pygame.display.update()
            clock.tick(fps)
        WidgetHandler.removeWidget(self.score_bar)
        self.level_music.stop()
        close_animation()

    # Успешное попадание
    def score(self, successful):
        if successful:
            self.successful_hits += 1
            if self.bar_percent <= (1 - self.score_delta):
                self.bar_percent += self.score_delta
            else:
                self.bar_percent = 1
        else:
            self.bar_percent -= self.score_delta

    # Создания целей по уровню сложности
    def generate_key(self):
        self.circle_key_step += 1
        if self.difficult == 'normal':
            return pygame.K_c
        elif self.difficult == 'medium':
            return [pygame.K_x, pygame.K_c][self.circle_key_step % 2]
        elif self.difficult == 'hard':
            return [pygame.K_z, pygame.K_x, pygame.K_c][self.circle_key_step % 3]
        elif self.difficult == 'insane':
            return choice([pygame.K_x, pygame.K_c])
        elif self.difficult == 'psycho':
            return choice([pygame.K_z, pygame.K_x, pygame.K_c])

    # Создание scorebar
    def generate_scorebar(self):
        score_bar = ProgressBar(screen, int(30 * (screen_width / 1920)), int(10 * (screen_height / 1080)),
                                int(500 * (screen_width / 1920)), int(35 * (screen_height / 1080)),
                                lambda: self.bar_percent, curved=True, completedColour=(110, 0, 238),
                                incompletedColour=(187, 134, 252))
        self.bar_percent -= self.bar_speed
        return score_bar


# Класс цели в виде кружка
class TargetCircle:
    def __init__(self, x, y, radius, speed, frame, key):
        self.x = int(x * (screen_width / 1920))
        self.y = int(y * (screen_height / 1080))
        self.max_radius = int(radius * (screen_width / 1920))
        self.speed = self.max_radius / (fps * speed)
        self.key = key
        self.start_frame = frame * (fps / 60)
        self.text_key = pygame.key.name(key)
        self.start_successful_frame = (self.max_radius / self.speed) * 0.75
        self.frame = 0
        self.radius = 0
        self.death = 0
        self.is_checked = False
        self.hit_frame = None
        self.hitbox = pygame.Rect(self.x - self.max_radius // 2, self.y - self.max_radius // 2, self.max_radius,
                                  self.max_radius)
        self.outline_image = pygame.transform.smoothscale(pygame.image.load('materials//circle_out.png'),
                                                          (self.max_radius + 10 * (screen_width / 1920),
                                                           self.max_radius + 10 * (screen_width / 1920)))
        self.inline_image = pygame.image.load('materials//circle_in.png')
        self.font = pygame.font.Font('materials\\Press Start 2P.ttf', self.max_radius // 2)
        self.text = self.font.render(self.text_key, True, (255, 255, 255))
        size = self.max_radius // 2
        self.fail_img = pygame.transform.smoothscale(pygame.image.load('materials\\circ_fail.png'), (size, size))
        self.suc_img = pygame.transform.smoothscale(pygame.image.load('materials\\circ_suc.png'), (size, size))
        self.hit_sound = pygame.mixer.Sound('materials\\circle_click.mp3')

    # Движение кружка
    def move(self):
        if self.death:
            self.death += 1
            return
        self.radius += self.speed
        self.frame += 1
        if self.radius > self.max_radius:
            self.death = 1
            self.hit_frame = -1

    # Обновление всех параметров
    def frame_update(self, events):
        self.move()
        self.blit()
        self.collision(events)
        return self.get_data()

    # Реакция на результат попадания
    def blit(self):
        if self.death:
            if self.hit_frame >= self.start_successful_frame:
                screen.blit(self.suc_img, self.suc_img.get_rect(center=(self.x, self.y)))
            else:
                screen.blit(self.fail_img, self.fail_img.get_rect(center=(self.x, self.y)))
            return
        screen.blit(self.outline_image, self.outline_image.get_rect(center=(self.x, self.y)))
        inline_blit_img = pygame.transform.smoothscale(self.inline_image, (self.radius, self.radius))
        screen.blit(inline_blit_img, inline_blit_img.get_rect(center=(self.x, self.y)))
        screen.blit(self.text, self.text.get_rect(center=(self.x, self.y)))

    # Обработка попадания
    def collision(self, events):
        if self.death:
            return
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == self.key:
                if self.hitbox.collidepoint(pygame.mouse.get_pos()):
                    self.hit_sound.play()
                    self.hit_frame = self.frame
                    self.death = 1

    # Возврат состояния
    def get_data(self):
        if self.death:
            return [True, self.hit_frame >= self.start_successful_frame, self.death > 45 * (fps / 60), self.death == 1]
        else:
            return [False]


# Класс редактора для создания уровней
class LevelEditor:
    def __init__(self, level_name=None):
        self.bg_image = pygame.transform.smoothscale(pygame.image.load('materials//redactor_default.jpg'),
                                                     (screen_width, screen_height))
        if not level_name:
            self.directory = self.get_new_level()
            if self.directory:
                self.create_directory()

    # Создание нового уровня
    def get_new_level(self):
        screen.blit(self.bg_image, (0, 0))
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(50 * (screen_width / 1920)))
        text = font.render('select song', True, (124, 62, 249))
        screen.blit(text, text.get_rect(center=(screen_width // 2, screen_height - 200 * (screen_height / 1080))))
        pygame.display.update()
        name = filedialog.askopenfilename(filetypes=(("music files", "*.mp3"),), title='select level music (.mp3)')
        return name

    # Создание папок для хранения материалов уровня
    def create_directory(self):
        name = self.directory[self.directory.rfind('/') + 1: self.directory.rfind('.mp3')]
        c = 1
        while os.path.exists(f'songs//{name}'):
            name += str(c)
        os.makedirs(f'songs//{name}')
        old_bytes = open('materials//redactor_default.jpg', mode='rb').read()
        open(f'songs//{name}//bg.jpg', mode='wb').write(old_bytes)
        open(f'songs//{name}//level.json', mode='w').write('{"circles": []}')
        old_bytes = open(self.directory, mode='rb').read()
        open(f'songs//{name}//song.mp3', mode='wb').write(old_bytes)

    def run(self):
        pass


class ExitMenu:
    def __init__(self):
        self.running = True
        self.image = pygame.image.load('materials//menu_bg.jpg')
        self.image = pygame.transform.smoothscale(self.image, (screen_width, screen_height))
        self.buttons_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(15 * (screen_width / 1920)))
        self.buttons = self.generate_confirm_exit_buttons()

    def generate_confirm_exit_buttons(self):
        width = 500 * (screen_width / 1920)
        height = (60 * (screen_height / 1080) + 30 * (screen_height / 1080)) * 2
        button_array = NewButtonArray(
            screen,
            int(screen_width // 2 - width // 2),
            int(250 * (screen_height / 1080)),
            int(width),
            int(height),
            (1, 2),
            border=30 * (screen_height / 1080),
            topBorder=0,
            bottomBorder=0,
            leftBorder=0,
            rightBorder=0,
            inactiveColours=[(77, 50, 145) for _ in range(2)],
            hoverColours=[(54, 35, 103) for _ in range(2)],
            pressedColours=[(121, 78, 230) for _ in range(2)],
            radii=[int(25 * (screen_height / 1080)) for _ in range(2)],
            fonts=[self.buttons_font for _ in range(2)],
            texts=['Exit', 'Return'],
            invisible=True,
            textColours=[(255, 255, 255) for _ in range(2)],
            onClicks=[lambda x: self.confirm_exit(x) for _ in range(2)],
            onClickParams=[[True], [False]]
        )
        return button_array

    def confirm_exit(self, arg):
        global running
        if arg:
            running = False
        self.running = False

    def check_exit_event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    def run(self):
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(50 * (screen_width / 1920)))
        text = font.render('Exit?', True, (124, 62, 249))
        text_rect = text.get_rect(center=(screen_width // 2, 50 * (screen_height / 1080)))
        while self.running:
            screen.blit(self.image, (0, 0))
            screen.blit(text, text_rect)
            events = pygame.event.get()
            self.check_exit_event(events)
            pygame_widgets.update(events)
            pygame.display.update()
        pygame.mixer.stop()
        WidgetHandler.removeWidget(self.buttons)
        if not running:
            close_animation()


running = True


# Основной цикл игры
def main():
    global running
    settings_data = [100, 'normal', False]
    while running:
        menu = Menu(settings_data)
        menu.run()
        settings_data = [menu.volume_level, menu.difficult, menu.menu_song.get_volume() == 0]
        script = menu.script
        if script == 'game':
            game = Game(menu.level_name, menu.difficult, menu.volume_level)
            game.run()
        elif script == 'redactor':
            editor = LevelEditor(menu.level_name)
            editor.run()
        elif script == 'exit':
            window = ExitMenu()
            window.run()


if __name__ == '__main__':
    main()
