import os
import pygame
import pygame_widgets
import json
from screeninfo import get_monitors
from pygame_widgets.button import ButtonArray, Button
from pygame_widgets.dropdown import Dropdown
from pygame_widgets.widget import WidgetHandler
from pygame_widgets.slider import Slider
from random import choice

# Необходимо для определения разрешения по неясным причинам
get_monitors()

# Предопределение основных переменных
resolutions = [(1600, 900), (1920, 1080), (2560, 1440), (3840, 2160)]
fps = 144
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


# Класс главного меню
class Menu:
    def __init__(self):
        self.running = True
        self.difficult = 'medium'
        self.menu_song = pygame.mixer.Sound('materials//menu_mc.mp3')
        self.exit_sound = pygame.mixer.Sound('materials//exit.mp3')
        self.menu_song.play()
        self.song_list = [arg[1] for arg in os.walk('songs')][0]
        self.level_name = ''
        self.menu_image = pygame.image.load('materials//menu_bg.jpg')
        self.menu_image = pygame.transform.smoothscale(self.menu_image, (screen_width, screen_height))
        self.buttons = []
        self.buttons_scroll = 0
        self.buttons_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(15 * (screen_width / 1920)))
        self.buttons_font_color = (255, 255, 255)
        self.buttonArray = self.generate_song_button_array()
        self.FPS_dropdown_menu = self.generate_fps_dropdown_menu()
        self.difficulty_dropdown_menu = self.generate_difficulty_dropdown_menu()
        self.resolution_dropdown_menu = self.generate_resolution_dropdown_menu()
        self.confirm_button = self.generate_confirm_button()
        self.add_song_button = self.generate_add_song_button()
        self.volume_level = 100
        self.volume_slider = self.generate_volume_slider()

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

    # Вывод текста и заднего фона
    def blit(self):
        screen.blit(self.menu_image, self.menu_image.get_rect(center=(screen_width // 2, screen_height // 2)))
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(50 * (screen_width / 1920)))
        songs_text = font.render('Your Songs:', True, (124, 62, 249))
        songs_text_rect = songs_text.get_rect(center=(screen_width // 2, 50 * (screen_height / 1080)))
        screen.blit(songs_text, songs_text_rect)

    # Обновление всех виджетов
    def update_widgets(self, events):
        global running
        pygame_widgets.update(events)
        self.scroll_song_buttons(events)
        self.menu_song.set_volume(self.volume_slider.getValue() / 100)
        self.volume_level = self.volume_slider.getValue()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
                self.running = False

    # Листание списка кнопок песен колёсиком мыши
    def scroll_song_buttons(self, events):
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
        self.buttons_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(15 * (screen_width / 1920)))
        self.buttonArray = self.generate_song_button_array()
        self.FPS_dropdown_menu = self.generate_fps_dropdown_menu()
        self.difficulty_dropdown_menu = self.generate_difficulty_dropdown_menu()
        self.resolution_dropdown_menu = self.generate_resolution_dropdown_menu()
        self.confirm_button = self.generate_confirm_button()
        self.menu_image = pygame.transform.smoothscale(self.menu_image, (screen_width, screen_height))
        self.add_song_button = self.generate_add_song_button()
        self.volume_slider = self.generate_volume_slider()

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
                        pressedColour=(121, 78, 230), radius=75, border=30 * (screen_height / 1080))
        add_button = button
        return add_button

    # Анимация затухания меню
    def close_animation(self):
        surface = pygame.Surface((screen_width, screen_height))
        surface.fill((0, 0, 0))
        self.exit_sound.play()
        for i in range(1, fps):
            surface.set_alpha(int(255 * (i / fps)))
            screen.blit(surface, (0, 0))
            pygame.display.update()
            clock.tick(fps)

    # Создания настроек для открытого уровня
    def set_run_config(self, index):
        self.level_name = self.song_list[index]
        diff = self.difficulty_dropdown_menu.getSelected()
        if diff:
            self.difficult = diff
        self.running = False

    # Цикл для вывода на экран
    def run(self):
        while self.running:
            self.blit()
            self.update_widgets(pygame.event.get())
            pygame.display.update()
        self.close_animation()
        self.menu_song.stop()


# Основной класс игры
class Game:
    def __init__(self, level_name, difficult):
        self.running = True
        self.level_music = pygame.mixer.Sound('songs\\' + level_name + '\\' + 'song.mp3')
        self.level_background = pygame.transform.smoothscale(
            pygame.image.load('songs\\' + level_name + '\\' + 'bg.jpg'), (screen_width, screen_height))
        with open('songs\\' + level_name + '\\' + 'level.json') as f:
            self.level_data = json.load(f)
        self.difficult = difficult
        self.start_animation()
        self.level_music.play()

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

    # Создание объектов
    def update_object_list(self):
        pass

    # Расположение на уровне
    def move_objects(self):
        pass

    # Создание нового кадра игры
    def generate_frame(self, events):
        self.blit_background()
        self.update_object_list()
        self.move_objects()
        if self.check_exit_event(events):
            quit()

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
        self.level_music.stop()


# Класс цели в виде кружка
class TargetCircle:
    def __init__(self):
        pass


# Основной цикл игры
running = True
while running:
    menu = Menu()
    menu.run()
    if running:
        game = Game(menu.level_name, menu.difficult)
        game.run()
