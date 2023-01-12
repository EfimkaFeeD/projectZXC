import os
import pygame
import pygame_widgets
import json
import sqlite3
import logging
from sys import exit
from datetime import datetime
from tkinter import filedialog, messagebox
from screeninfo import get_monitors
from pygame_widgets.button import ButtonArray, Button
from pygame_widgets.dropdown import Dropdown
from pygame_widgets.widget import WidgetHandler
from pygame_widgets.slider import Slider
from pygame_widgets.progressbar import ProgressBar
from pygame_widgets.textbox import TextBox
from pygame_widgets.toggle import Toggle
from random import choice
from time import time, sleep


if not os.getcwd().endswith('bin'):
    os.chdir(os.getcwd() + '\\bin')


# Необходимо для определения разрешения по неясным причинам
get_monitors()

# Предопределение основных переменных
resolutions = [(1600, 900), (1920, 1080), (2560, 1440), (3840, 2160)]
fps = 60
pygame.init()
date = datetime.now()
if not os.path.isdir('system//logs'):
    os.mkdir('system//logs')
log_name = f"system//logs//{date.day}_{date.month}_{date.year}-{date.hour}_{date.minute}_{date.second}.log"
logging.basicConfig(level=logging.INFO, filename=log_name, filemode="w", format="%(asctime)s %(levelname)s %(message)s")
screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h
max_w, max_h = screen_width, screen_height
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()

# Подключение к базе данных
db_connection = sqlite3.connect('system//zxc.db')
account_id = 0

# Статистика для стандартного пользователя
anonymous_levels_played = 0
anonymous_levels_won = 0
anonymous_score = 0.0
anonymous_average_score = 0
anonymous_average_rank = 'N'
anonymous_successful = 0
anonymous_average_accuracy = 0.0
anonymous_accuracy = 0.0


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


# Класс курсора
class Cursor:
    def __init__(self):
        self.size = 70 * (screen_width / 1080)
        self.x, self.y = pygame.mouse.get_pos()
        self.image = pygame.transform.smoothscale(pygame.image.load('materials//cur.png'), (self.size, self.size))
        self.hitbox = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)
        self.hidden = False
        pygame.mouse.set_visible(False)

    # Изменения при смене разрешения
    def refactor(self):
        self.size = 70 * (screen_width / 1080)
        self.image = pygame.transform.smoothscale(pygame.image.load('materials//cur.png'), (self.size, self.size))
        self.hitbox = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, self.size, self.size)

    # Обновление позиции
    def update(self):
        self.x, self.y = pygame.mouse.get_pos()
        self.hitbox.x, self.hitbox.y = self.x - self.size // 2, self.y - self.size // 2
        if not self.hidden:
            screen.blit(self.image, self.image.get_rect(center=(self.x, self.y)))

    # Скрытие курсора
    def hide(self, mouse_hiding=True):
        self.hidden = True
        pygame.mouse.set_visible(not mouse_hiding)

    # Отмена скрытия курсора
    def show(self):
        self.hidden = False
        pygame.mouse.set_visible(False)


cursor = Cursor()


# Анимация затухания
def close_animation():
    surface = pygame.Surface((screen_width, screen_height))
    surface.fill((0, 0, 0))
    for i in range(1, fps, 2):
        surface.set_alpha(int(255 * (i / fps)))
        screen.blit(surface, (0, 0))
        pygame.display.update()
        clock.tick(fps)
    sleep(0.4)


# Вступительная анимация
def intro():
    font1 = pygame.font.Font('materials\\Press Start 2P.ttf', int(70 * (screen_width / 1920)))
    font2 = pygame.font.Font('materials\\Press Start 2P.ttf', int(40 * (screen_width / 1920)))
    text1 = font1.render('(project)', True, (77, 50, 145))
    text2 = font1.render('zxc', True, (77, 50, 145))
    text3 = font2.render('by GGergy and Efimka_FeeD', True, (77, 50, 145))
    pygame.mixer.Sound('materials//start_song.mp3').play()
    for i in range(fps * 2):
        text1.set_alpha(int(255 * (i / fps)))
        text2.set_alpha(int(255 * ((i - 60) / fps)))
        text3.set_alpha(int(255 * ((i - 100) / fps)))
        screen.blit(text1, text1.get_rect(center=(screen_width // 2, screen_height // 2)))
        screen.blit(text2, text2.get_rect(center=(1350 * (screen_width / 1920), 470 * (screen_height / 1080))))
        screen.blit(text3, text3.get_rect(center=(1400 * (screen_width / 1920), 1000 * (screen_height / 1080))))
        pygame.display.update()
        clock.tick(fps)
    sleep(0.4)


# Класс главного меню
class Menu:
    def __init__(self, args):
        self.running = True
        self.difficult = args[1]
        self.menu_songs = [arg[2] for arg in os.walk('materials//menu_musics')][0]
        self.menu_song = pygame.mixer.Sound('materials//menu_musics//' + self.menu_songs[0])
        self.volume_level = args[0]
        self.menu_song.set_volume(self.volume_level)
        if args[2]:
            self.menu_song.set_volume(0)
        self.menu_song.play(-1)
        self.confirm_exit_buttons = None
        self.song_list = [arg[1] for arg in os.walk('songs')][0]
        self.level_name = ''
        self.menu_image = pygame.image.load('materials//menu_bg.jpg')
        self.menu_image = pygame.transform.smoothscale(self.menu_image, (screen_width, screen_height))
        self.buttons = []
        self.script = ''
        self.wait_time = None
        self.buttons_scroll = 0
        self.buttons_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(15 * (screen_width / 1920)))
        self.buttons_font_color = (255, 255, 255)
        self.account_button = self.generate_account_button()
        self.stats_button = self.generate_stats_button()
        self.buttonArray = self.generate_song_button_array()
        self.FPS_dropdown_menu = self.generate_fps_dropdown_menu()
        self.difficulty_dropdown_menu = self.generate_difficulty_dropdown_menu()
        self.resolution_dropdown_menu = self.generate_resolution_dropdown_menu()
        self.confirm_button = self.generate_confirm_button()
        self.add_song_button = self.generate_add_song_button()
        self.menu_songs_dropdown_menu = self.generate_menu_songs_dropdown_menu()
        self.instructions_button = self.generate_instructions_button()
        self.volume_slider = self.generate_volume_slider()
        self.mute_button = self.generate_mute_button()
        self.start_animation()

    # Создание кнопки для управления аккаунтом
    def generate_account_button(self):
        account_button = Button(
            screen,
            screen_width - int(475 * (screen_width / 1920)),
            screen_height - int(75 * (screen_height / 1080)),
            int(200 * (screen_width / 1920)),
            int(50 * (screen_height / 1080)),
            text='account',
            radius=int(25 * (screen_height / 1080)),
            textColour=self.buttons_font_color,
            inactiveColour=(77, 50, 145),
            hoverColour=(54, 35, 103),
            pressedColour=(121, 78, 230),
            font=self.buttons_font,
            border=30 * (screen_height / 1080),
            onClick=lambda: self.account()
        )
        return account_button

    # Создание кнопки для просмотра статистики
    def generate_stats_button(self):
        stats_button = Button(
            screen,
            screen_width - int(725 * (screen_width / 1920)),
            screen_height - int(75 * (screen_height / 1080)),
            int(200 * (screen_width / 1920)),
            int(50 * (screen_height / 1080)),
            text='stats',
            radius=int(25 * (screen_height / 1080)),
            textColour=self.buttons_font_color,
            inactiveColour=(77, 50, 145),
            hoverColour=(54, 35, 103),
            pressedColour=(121, 78, 230),
            font=self.buttons_font,
            border=30 * (screen_height / 1080),
            onClick=lambda: self.stats()
        )
        return stats_button

    # Создание кнопки ддл инструкции
    def generate_instructions_button(self):
        stats_button = Button(
            screen,
            int(525 * (screen_width / 1920)),
            screen_height - int(75 * (screen_height / 1080)),
            int(200 * (screen_width / 1920)),
            int(50 * (screen_height / 1080)),
            text='instructions',
            radius=int(25 * (screen_height / 1080)),
            textColour=self.buttons_font_color,
            inactiveColour=(77, 50, 145),
            hoverColour=(54, 35, 103),
            pressedColour=(121, 78, 230),
            font=self.buttons_font,
            border=30 * (screen_height / 1080),
            onClick=self.instructions
        )
        return stats_button

    # Переход на экран инструкции при нажатии на кнопку
    def instructions(self):
        self.script = 'instructions'
        self.running = False

    # Создания списка музыки для меню
    def generate_menu_songs_dropdown_menu(self):
        menu_songs_dropdown_menu = Dropdown(
            screen, int(275 * (screen_width / 1920)), int(15 * (screen_height / 1080)),
            int(200 * (screen_width / 1920)), int(50 * (screen_height / 1080)), name='music',
            values=self.menu_songs,
            choices=[t[:t.rfind('.')] if len(t) < 14 else t[:11] for t in self.menu_songs],
            borderRadius=int(25 * (screen_height / 1080)), direction='down', textHAlign='centre',
            font=self.buttons_font,
            inactiveColour=(77, 50, 145),
            hoverColour=(54, 35, 103),
            textColour=self.buttons_font_color,
            pressedColour=(121, 78, 230)
        )
        return menu_songs_dropdown_menu

    # Создание списка кнопок треков
    def generate_song_button_array(self, text=None):
        texts = self.song_list if not text else text
        texts = texts[:9]
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
            invisible=True,
            textColours=[self.buttons_font_color for _ in range(len(texts))],
            onClicks=[self.start_waiting for _ in range(len(texts))],
            onReleases=[self.set_run_config for _ in range(len(texts))],
            onReleaseParams=[[i] for i in range(len(texts))]
        )
        return song_button_array

    # Создание списка кнопок сложностей
    def generate_difficulty_dropdown_menu(self):
        difficulty_drop_menu = Dropdown(
            screen, int(25 * (screen_width / 1920)), int(15 * (screen_height / 1080)),
            int(200 * (screen_width / 1920)), int(50 * (screen_height / 1080)), name='difficulty',
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
            choices=['30', '60', '120', '144'],
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
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(20 * (screen_width / 1920)))
        render = font.render(f'scroll↓', True, (160, 160, 160))
        screen.blit(render, render.get_rect(center=(screen_width // 2, 110 * (screen_height / 1080))))
        screen.blit(songs_text, songs_text_rect)

    # Обновление всех виджетов
    def update_widgets(self, events):
        global running
        if self.wait_time:
            self.wait_time += 1 / fps
        pygame_widgets.update(events)
        self.scroll_song_buttons(events)
        if self.menu_song.get_volume() != 0:
            self.menu_song.set_volume(self.volume_slider.getValue() / 100)
            self.volume_level = self.volume_slider.getValue()
        self.check_exit_events(events)

    # Проверка на выход из игры
    def check_exit_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                WidgetHandler.removeWidget(self.buttonArray)
                WidgetHandler.removeWidget(self.FPS_dropdown_menu)
                WidgetHandler.removeWidget(self.difficulty_dropdown_menu)
                WidgetHandler.removeWidget(self.resolution_dropdown_menu)
                WidgetHandler.removeWidget(self.confirm_button)
                WidgetHandler.removeWidget(self.add_song_button)
                WidgetHandler.removeWidget(self.volume_slider)
                WidgetHandler.removeWidget(self.mute_button)
                WidgetHandler.removeWidget(self.menu_songs_dropdown_menu)
                WidgetHandler.removeWidget(self.account_button)
                WidgetHandler.removeWidget(self.stats_button)
                WidgetHandler.removeWidget(self.instructions_button)
                window = PauseMenu(self.menu_image, 'return', 'exit', music=['materials//return.mp3', None],
                                   title='Exit?')
                if window.state == 'exit':
                    close_animation()
                    logging.info('Session ended')
                    exit()
                else:
                    self.buttonArray = self.generate_song_button_array()
                    self.FPS_dropdown_menu = self.generate_fps_dropdown_menu()
                    self.difficulty_dropdown_menu = self.generate_difficulty_dropdown_menu()
                    self.resolution_dropdown_menu = self.generate_resolution_dropdown_menu()
                    self.confirm_button = self.generate_confirm_button()
                    self.menu_image = pygame.transform.smoothscale(self.menu_image, (screen_width, screen_height))
                    self.add_song_button = self.generate_add_song_button()
                    self.volume_slider = self.generate_volume_slider()
                    self.mute_button = self.generate_mute_button()
                    self.menu_songs_dropdown_menu = self.generate_menu_songs_dropdown_menu()
                    self.account_button = self.generate_account_button()
                    self.stats_button = self.generate_stats_button()
                    self.instructions_button = self.generate_instructions_button()

    def start_waiting(self):
        self.wait_time = 1 / fps

    # Листание списка кнопок песен колёсиком мыши
    def scroll_song_buttons(self, events):
        pos = pygame.mouse.get_pos()
        if not pygame.Rect(self.buttonArray.getX(), self.buttonArray.getY(), self.buttonArray.getWidth(),
                           screen_height).collidepoint(pos):
            return
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    if self.buttons_scroll < len(self.song_list) - 1:
                        self.buttons_scroll += 1
                elif event.button == 4:
                    if self.buttons_scroll > 0:
                        self.buttons_scroll -= 1
                else:
                    return
                WidgetHandler.removeWidget(self.buttonArray)
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
        WidgetHandler.removeWidget(self.menu_songs_dropdown_menu)
        WidgetHandler.removeWidget(self.account_button)
        WidgetHandler.removeWidget(self.instructions_button)
        WidgetHandler.removeWidget(self.stats_button)
        self.buttons_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(15 * (screen_width / 1920)))
        cursor.refactor()
        self.buttonArray = self.generate_song_button_array()
        self.FPS_dropdown_menu = self.generate_fps_dropdown_menu()
        self.difficulty_dropdown_menu = self.generate_difficulty_dropdown_menu()
        self.resolution_dropdown_menu = self.generate_resolution_dropdown_menu()
        self.confirm_button = self.generate_confirm_button()
        self.menu_image = pygame.transform.smoothscale(self.menu_image, (screen_width, screen_height))
        self.add_song_button = self.generate_add_song_button()
        self.volume_slider = self.generate_volume_slider()
        self.mute_button = self.generate_mute_button()
        self.menu_songs_dropdown_menu = self.generate_menu_songs_dropdown_menu()
        self.account_button = self.generate_account_button()
        self.stats_button = self.generate_stats_button()
        self.instructions_button = self.generate_instructions_button()

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
        music_name = self.menu_songs_dropdown_menu.getSelected()
        new_fps = self.FPS_dropdown_menu.getSelected()
        new_resolution = self.resolution_dropdown_menu.getSelected()
        if new_fps:
            fps = int(new_fps)
        if new_resolution and new_resolution != (screen_width, screen_height):
            self.refactor(new_resolution)
        if music_name:
            muted = self.menu_song.get_volume() == 0
            self.menu_songs_dropdown_menu.reset()
            self.menu_song.stop()
            self.menu_song = pygame.mixer.Sound('materials//menu_musics//' + music_name)
            self.menu_song.play(-1)
            if muted:
                self.menu_song.set_volume(0)
            else:
                self.menu_song.set_volume(self.volume_level)

    # Переход на экран аккаунта при нажатии кнопки
    def account(self):
        self.script = 'account'
        self.running = False

    # Переход на экран статистики при нажатии кнопки
    def stats(self):
        self.script = 'stats'
        self.running = False

    # Кнопка для открытия редактора нового уровня
    def generate_add_song_button(self):
        button = Button(screen, screen_width // 2 - int(37.5 * (screen_width / 1920)),
                        screen_height - int(87.5 * (screen_height / 1080)), int(75 * (screen_width / 1920)),
                        int(75 * (screen_height / 1080)), text='+', font=self.buttons_font,
                        textColour=self.buttons_font_color, inactiveColour=(77, 50, 145), hoverColour=(54, 35, 103),
                        pressedColour=(121, 78, 230), radius=75, border=30 * (screen_height / 1080),
                        onClick=self.run_editor)
        add_button = button
        return add_button

    # Переход на экран редактора уровня
    def run_editor(self):
        self.script = 'editor'
        self.running = False

    # Создания настроек для открытого уровня
    def set_run_config(self, index):
        self.level_name = self.song_list[index + self.buttons_scroll]
        diff = self.difficulty_dropdown_menu.getSelected()
        if diff:
            self.difficult = diff
        if self.wait_time < 1:
            self.script = 'game'
        else:
            self.script = 'editor'
        self.running = False

    # Цикл для вывода на экран
    def run(self):
        global running
        while self.running:
            self.blit()
            self.update_widgets(pygame.event.get())
            cursor.update()
            pygame.display.update()
        self.confirm_settings()
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
            WidgetHandler.removeWidget(self.menu_songs_dropdown_menu)
            WidgetHandler.removeWidget(self.account_button)
            WidgetHandler.removeWidget(self.stats_button)
            WidgetHandler.removeWidget(self.instructions_button)

    # Анимация перехода на уровень
    def start_animation(self):
        surface = pygame.Surface((screen_width, screen_height))
        surface.fill((0, 0, 0))
        for i in range(fps, 1, -2):
            self.blit()
            self.update_widgets(pygame.event.get())
            surface.set_alpha(int(255 * (i / fps)))
            screen.blit(surface, (0, 0))
            cursor.update()
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
        self.objects = self.create_object_list()
        if not self.objects:
            self.level_music.play()
            EmptyLevelWindow()
            self.level_music.stop()
            self.running = False
            return
        self.possible_objects = len(self.objects)
        self.start_animation()
        self.total_objects = 0
        self.start_time = None
        self.successful_hits = 0
        self.bar_speed = self.level_data['common']['bar_speed'] * (60 / fps)
        self.score_delta_up = self.level_data['common']['delta_up']
        self.score_delta_down = self.level_data['common']['delta_down']
        self.bar_percent = 1 + self.bar_speed
        self.score_bar = self.generate_scorebar()

    # Анимация появления уровня
    def start_animation(self):
        surface = pygame.Surface((screen_width, screen_height))
        surface.fill((0, 0, 0))
        for i in range(fps, 1, -2):
            self.blit_background()
            surface.set_alpha(int(255 * (i / fps)))
            screen.blit(surface, (0, 0))
            pygame.display.update()
            clock.tick(fps)

    # Смена заднего фона на задний фон уровня
    def blit_background(self):
        screen.blit(self.level_background, (0, 0))

    # Вывод точности попаданий справа от scorebar
    def blit_accuracy(self):
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(20 * (screen_width / 1920)))
        if self.total_objects == 0:
            txt = '100.0%'
        elif self.successful_hits == 0:
            txt = '0.0%'
        else:
            txt = f'{round(self.successful_hits / self.total_objects * 100, 2)}%'
        render = font.render(txt, True, (124, 62, 249))
        screen.blit(render, (int(570 * (screen_width / 1920)), int(20 * (screen_height / 1080))))

    # Создание целей
    def create_object_list(self):
        objects = []
        radius = self.level_data['common']['radius']
        speed = self.level_data['common']['speed']
        color = self.level_data['common']['color']
        max_radius = int(radius * (screen_width / 1920))
        outline_image = pygame.transform.smoothscale(pygame.image.load('materials//circle_out.png'),
                                                     (max_radius * 2 + 10 * (screen_width / 1920),
                                                      max_radius * 2 + 10 * (screen_width / 1920)))
        font = pygame.font.SysFont('roboto', max_radius * 2)
        fail_img = pygame.transform.smoothscale(pygame.image.load('materials\\circ_fail.png'), (max_radius, max_radius))
        suc_img = pygame.transform.smoothscale(pygame.image.load('materials\\circ_suc.png'), (max_radius, max_radius))
        for data in self.level_data["circles"]:
            objects.append(TargetCircle(start_time=data['time'], x=data["x"], y=data["y"], speed=speed,
                                        radius=radius, key=self.generate_key(), color=color, suc=suc_img,
                                        fail=fail_img, outline=outline_image, font=font,
                                        volume=self.level_music.get_volume()))
        return objects

    # Расположение на уровне
    def object_events(self, events):
        marking = False
        clicked = False
        for obj in self.objects:
            if obj.start_time > (time() - self.start_time):
                return
            data = obj.frame_update(events, clicked)
            if obj.clicked and obj.death == 1:
                clicked = True
            if data[0]:
                if not obj.is_checked:
                    self.score(data[1])
                    self.total_objects += 1
                    obj.is_checked = True
                if data[2]:
                    del self.objects[self.objects.index(obj)]
            elif not marking:
                obj.mark()
                marking = True

    # Создание нового кадра игры
    def generate_frame(self, events):
        self.blit_background()
        self.blit_accuracy()
        self.object_events(events)
        self.check_end_game()
        pygame_widgets.update(events)
        if self.check_exit_event(events):
            quit()

    # Выход из игры в меню
    def check_exit_event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or not pygame.mouse.get_focused():
                WidgetHandler.removeWidget(self.score_bar)
                pygame.mixer.pause()
                wait_time = time()
                for obj in self.objects:
                    obj.pause()
                pause_menu = PauseMenu(self.level_background, 'continue', 'back')
                if pause_menu.state == 'back':
                    self.running = False
                else:
                    pygame.mixer.unpause()
                    for obj in self.objects:
                        obj.unpause()
                    self.start_time += time() - wait_time
                    self.score_bar = self.generate_scorebar()

    # Проверка на завершение игры
    def check_end_game(self):
        if self.bar_percent < 0:
            WidgetHandler.removeWidget(self.score_bar)
            GameResultMenu('loose', self.successful_hits, self.total_objects, self.difficult, self.possible_objects)
        elif len(self.objects) == 0:
            WidgetHandler.removeWidget(self.score_bar)
            GameResultMenu('win', self.successful_hits, self.total_objects, self.difficult)
        else:
            return
        self.running = False

    # Цикл для вывода на экран
    def run(self):
        if not self.running:
            return
        self.level_music.play()
        self.start_time = time()
        while self.running:
            self.generate_frame(pygame.event.get())
            cursor.update()
            pygame.display.update()
            clock.tick(fps)
        self.level_music.stop()
        close_animation()

    # Успешное попадание
    def score(self, successful):
        if successful:
            self.successful_hits += 1
            if self.bar_percent <= (1 - self.score_delta_up):
                self.bar_percent += self.score_delta_up
            else:
                self.bar_percent = 1
        else:
            self.bar_percent -= self.score_delta_down

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
                                self.update_bar_percent, curved=True, completedColour=(110, 0, 238),
                                incompletedColour=(187, 134, 252))
        return score_bar

    def update_bar_percent(self):
        if self.bar_percent >= self.bar_speed:
            self.bar_percent -= self.bar_speed
        return self.bar_percent


# Класс цели в виде кружка
class TargetCircle:
    hit_sound = pygame.mixer.Sound('materials\\circle_click.mp3')

    def __init__(self, x, y, radius, speed, start_time, key, color, outline, font, suc, fail, cheats=False, volume=1.0):
        self.hit_sound.set_volume(volume)
        self.x = int(x * (screen_width / 1920))
        self.y = int(y * (screen_height / 1080))
        self.max_radius = int(radius * (screen_width / 1920))
        self.speed = self.max_radius / (fps * speed)
        self.key = key
        self.start_time = start_time
        self.lifetime = None
        self.text_key = pygame.key.name(key)
        self.start_successful_time = speed * 0.8
        self.end_successful_time = speed * 1.2
        self.radius = 0
        self.death = 0
        self.is_checked = False
        self.clicked = False
        self.cheats = cheats
        self.hit_time = None
        self.marked_color = color
        self.color = (156, 156, 156)
        self.wait_time = None
        self.hitbox = pygame.Rect(self.x - self.max_radius // 2, self.y - self.max_radius // 2, self.max_radius,
                                  self.max_radius)
        self.outline_image = outline
        self.font = font
        self.text = self.font.render(self.text_key, True, (255, 255, 255))
        self.fail_img = fail
        self.suc_img = suc

    # Движение кружка
    def move(self):
        if self.radius == 0:
            self.lifetime = time()
        if self.radius >= self.max_radius and self.cheats:
            self.hit_time = -1
        if (time() - self.lifetime) > self.end_successful_time and not self.hit_time:
            self.hit_time = -1
        if self.death:
            self.death += 1
            return
        self.radius += self.speed
        if self.radius > self.max_radius:
            self.death = 1
            if self.cheats:
                self.hit_sound.play()

    def mark(self):
        self.color = self.marked_color

    # Обновление всех параметров
    def frame_update(self, events, clicked=True):
        self.move()
        self.blit()
        if not clicked:
            self.collision(events)
        return self.get_data()

    # Реакция на результат попадания
    def blit(self):
        if self.hit_time and not self.cheats:
            if self.start_successful_time <= self.hit_time <= self.end_successful_time:
                screen.blit(self.suc_img, self.suc_img.get_rect(center=(self.x, self.y)))
            else:
                screen.blit(self.fail_img, self.fail_img.get_rect(center=(self.x, self.y)))
            return
        screen.blit(self.outline_image, self.outline_image.get_rect(center=(self.x, self.y)))
        pygame.draw.circle(screen, color=self.color, center=(self.x, self.y), radius=self.radius)
        screen.blit(self.text, self.text.get_rect(center=(self.x, self.y)))

    # Обработка попадания
    def collision(self, events):
        if time() - self.lifetime > self.end_successful_time or self.cheats:
            return
        uncorrected_keys = [pygame.K_x, pygame.K_c, pygame.K_z]
        uncorrected_keys.remove(self.key)
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == self.key:
                for el in uncorrected_keys:
                    if pygame.key.get_pressed()[el]:
                        return
                if self.hitbox.colliderect(cursor.hitbox):
                    self.hit_sound.play()
                    self.hit_time = time() - self.lifetime
                    self.death = 1
                    self.clicked = True

    # При переходе в меню паузы
    def pause(self):
        self.wait_time = time()

    # При выходе из меню паузы
    def unpause(self):
        if self.lifetime:
            self.lifetime += time() - self.wait_time

    # Возврат состояния
    def get_data(self):
        if self.hit_time:
            return [True, self.start_successful_time <= self.hit_time <= self.end_successful_time,
                    self.death > 45 * (fps / 60)]
        else:
            return [False]


# Класс редактора для создания уровней
class LevelEditor:
    def __init__(self, level_name=None, volume_level=1):
        self.default_bg = pygame.transform.smoothscale(pygame.image.load('materials//redactor_default.jpg'),
                                                       (screen_width, screen_height))
        self.running = True
        self.button_invincible = False
        self.frame = 0
        self.volume_level = volume_level
        self.level_name = level_name
        self.tools = ['set bg', 'set speed', 'set radius', 'set bar speed', 'set up delta', 'set down delta',
                      'delete level', 'rename']
        if not level_name:
            self.directory = self.get_new_level()
            if not self.directory:
                self.running = False
                return
            self.create_directory()
            self.level_name = self.directory[self.directory.rfind('/') + 1: self.directory.rfind('.mp3')]
        self.level_music, self.level_background, self.objects, self.common_data = self.load_materials()
        self.mapping_buttons = self.generate_mapping_buttons()
        self.tool_buttons = self.generate_tool_buttons()
        self.color_dropdown = self.generate_color_dropdown()
        self.confirm_color_button = self.generate_confirm_color_button()

    # Создание нового уровня
    def get_new_level(self):
        screen.blit(self.default_bg, (0, 0))
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
        self.level_name = name
        os.makedirs(f'songs//{name}')
        old_bytes = open('materials//redactor_default.jpg', mode='rb').read()
        open(f'songs//{name}//bg.jpg', mode='wb').write(old_bytes)
        open(f'songs//{name}//level.json', mode='w').write('{"common": {"radius":  50, "speed":  0.9, "delta_up":  0.2,'
                                                           ' "delta_down":  0.3, "bar_speed":  0.0009,'
                                                           ' "color": "black"},'
                                                           ' "circles": []}')
        old_bytes = open(self.directory, mode='rb').read()
        open(f'songs//{name}//song.mp3', mode='wb').write(old_bytes)

    # Загрузка музыки, заднего фона, json уровня
    def load_materials(self):
        level_music = pygame.mixer.Sound('songs\\' + self.level_name + '\\' + 'song.mp3')
        level_background = pygame.transform.smoothscale(
            pygame.image.load('songs\\' + self.level_name + '\\' + 'bg.jpg'), (screen_width, screen_height))
        objects = []
        with open('songs\\' + self.level_name + '\\' + 'level.json') as f:
            file = json.load(f)
            common_data = file['common']
            for data in file["circles"]:
                objects.append({'x': data['x'], 'y': data['y'], 'time': data['time']})
        return level_music, level_background, objects, common_data

    # Цикл для вывода на экран
    def run(self):
        if not self.level_name:
            return
        self.level_music.set_volume(self.volume_level)
        self.level_music.play(-1)
        while self.running:
            if self.button_invincible and self.frame - self.button_invincible > 3:
                self.button_invincible = False
            self.blit_bg()
            events = pygame.event.get()
            pygame_widgets.update(events)
            self.check_exit_event(events)
            cursor.update()
            pygame.display.update()
            self.frame += 1
        self.level_music.stop()
        WidgetHandler.removeWidget(self.tool_buttons)
        WidgetHandler.removeWidget(self.mapping_buttons)
        WidgetHandler.removeWidget(self.color_dropdown)
        WidgetHandler.removeWidget(self.confirm_color_button)

    # Вывод заднего фона и приветствия
    def blit_bg(self):
        screen.blit(self.level_background, (0, 0))
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(50 * (screen_width / 1920)))
        text = font.render('Welcome to LevelEditor!', True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(screen_width // 2, 900 * (screen_height / 1080))))

    # Проверка на выход из редактора в меню
    def check_exit_event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                WidgetHandler.removeWidget(self.mapping_buttons)
                WidgetHandler.removeWidget(self.tool_buttons)
                WidgetHandler.removeWidget(self.color_dropdown)
                WidgetHandler.removeWidget(self.confirm_color_button)
                window = PauseMenu(self.level_background, 'save and exit', 'return')
                if window.state == 'save and exit':
                    self.running = False
                self.tool_buttons = self.generate_tool_buttons()
                self.mapping_buttons = self.generate_mapping_buttons()
                self.color_dropdown = self.generate_color_dropdown()
                self.confirm_color_button = self.generate_confirm_color_button()

    # Создание кнопок для редактирования и проверки уровня
    def generate_mapping_buttons(self):
        width = 500 * (screen_width / 1920)
        height = (60 * (screen_height / 1080) + 30 * (screen_height / 1080)) * 2
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(25 * (screen_width / 1920)))
        button_array = NewButtonArray(
            screen,
            int(screen_width // 2 - width // 2),
            int(screen_height // 2 - height // 2),
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
            fonts=[font for _ in range(2)],
            texts=['Start live-mapping', 'Check and test'],
            invisible=True,
            textColours=[(255, 255, 255) for _ in range(2)],
            onClicks=[lambda x: self.start(x) for _ in range(2)],
            onClickParams=[['live'], ['check']]
        )
        return button_array

    # Создание кнопок для редактирования параметров уровня
    def generate_tool_buttons(self):
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(10 * (screen_width / 1920)))
        tools = self.tools
        button_array = NewButtonArray(
            screen,
            int(25 * (screen_width / 1920)), int(15 * (screen_height / 1080)),
            int(200 * (screen_width / 1920)) * len(tools), int(50 * (screen_height / 1080)),
            (len(tools), 1),
            border=30 * (screen_height / 1080),
            topBorder=0,
            bottomBorder=0,
            leftBorder=0,
            rightBorder=0,
            inactiveColours=[(77, 50, 145) for _ in range(len(tools))],
            hoverColours=[(54, 35, 103) for _ in range(len(tools))],
            pressedColours=[(121, 78, 230) for _ in range(len(tools))],
            radii=[int(25 * (screen_height / 1080)) for _ in range(len(tools))],
            fonts=[font for _ in range(len(tools))],
            texts=tools,
            invisible=True,
            textColours=[(255, 255, 255) for _ in range(len(tools))],
            onClicks=[lambda x: self.tool(x) for _ in range(len(tools))],
            onClickParams=[[i] for i in tools]
        )
        return button_array

    # Создание меню выбора цвета целей
    @staticmethod
    def generate_color_dropdown():
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(10 * (screen_width / 1920)))
        colors = ['black', 'blue', 'green', 'red', 'yellow']
        x = int(25 * (screen_width / 1920))
        dropdown_menu = Dropdown(
            screen, x, int(75 * (screen_height / 1080)),
            int(170 * (screen_width / 1920)), int(50 * (screen_height / 1080)), name='circle color',
            choices=colors,
            borderRadius=int(25 * (screen_height / 1080)), direction='down', textHAlign='centre',
            font=font,
            inactiveColour=(77, 50, 145),
            hoverColour=(54, 35, 103),
            textColour=(255, 255, 255),
            pressedColour=(121, 78, 230)
        )
        return dropdown_menu

    # Создание кнопки подтверждения цвета целей
    def generate_confirm_color_button(self):
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(10 * (screen_width / 1920)))
        x = int(225 * (screen_width / 1920))
        button = Button(
            screen,
            x,
            int(75 * (screen_height / 1080)),
            int(170 * (screen_width / 1920)),
            int(50 * (screen_height / 1080)),
            text='confirm color',
            radius=int(25 * (screen_height / 1080)),
            textColour=(255, 255, 255),
            inactiveColour=(77, 50, 145),
            hoverColour=(54, 35, 103),
            pressedColour=(121, 78, 230),
            font=font,
            border=30 * (screen_height / 1080),
            onClick=self.select_color,
        )
        return button

    # Применение цвета на цели
    def select_color(self):
        new_color = self.color_dropdown.getSelected()
        if new_color:
            with open('songs\\' + self.level_name + '\\' + 'level.json') as f:
                wl = json.load(f)
                wl['common']['color'] = new_color
            with open('songs\\' + self.level_name + '\\' + 'level.json', mode='w') as f:
                json.dump(wl, f)
            self.common_data['color'] = new_color

    # Запуск редактирования или проверки уровня
    def start(self, process):
        if self.button_invincible:
            return
        if process == 'live':
            WidgetHandler.removeWidget(self.mapping_buttons)
            WidgetHandler.removeWidget(self.tool_buttons)
            WidgetHandler.removeWidget(self.color_dropdown)
            WidgetHandler.removeWidget(self.confirm_color_button)
            if self.objects:
                window = PauseMenu(self.level_background, 'start over', 'continue editing', 'back')
            else:
                window = PauseMenu(self.level_background, 'start over', 'back')
            if window.state == 'start over':
                self.live_mapping()
            elif window.state == 'continue editing':
                self.live_mapping(restart=False)
            else:
                self.tool_buttons = self.generate_tool_buttons()
                self.mapping_buttons = self.generate_mapping_buttons()
                self.color_dropdown = self.generate_color_dropdown()
                self.confirm_color_button = self.generate_confirm_color_button()
        if process == 'check':
            self.check_window()

    # Создание уровня в реальном времени
    def live_mapping(self, restart=True):
        self.level_music.stop()
        window = LiveMapWindow(f'songs//{self.level_name}//song.mp3', self.level_background, self.common_data,
                               self.objects, restart, volume_level=self.volume_level)
        if window.saving:
            data = window.pack()
            self.objects = data
            with open('songs\\' + self.level_name + '\\' + 'level.json') as f:
                wl = json.load(f)
                wl['circles'] = data
            with open('songs\\' + self.level_name + '\\' + 'level.json', mode='w') as f:
                json.dump(wl, f)
        self.level_music.set_volume(self.volume_level)
        self.level_music.play(-1)
        self.mapping_buttons = self.generate_mapping_buttons()
        self.tool_buttons = self.generate_tool_buttons()
        self.color_dropdown = self.generate_color_dropdown()
        self.confirm_color_button = self.generate_confirm_color_button()

    # Режим проверки уровня
    def check_window(self):
        WidgetHandler.removeWidget(self.mapping_buttons)
        WidgetHandler.removeWidget(self.tool_buttons)
        WidgetHandler.removeWidget(self.color_dropdown)
        WidgetHandler.removeWidget(self.confirm_color_button)
        self.level_music.stop()
        TestMenu(self.common_data, self.objects, self.level_background, f'songs//{self.level_name}//song.mp3',
                 self.volume_level)
        self.mapping_buttons = self.generate_mapping_buttons()
        self.tool_buttons = self.generate_tool_buttons()
        self.color_dropdown = self.generate_color_dropdown()
        self.confirm_color_button = self.generate_confirm_color_button()
        self.level_music.set_volume(self.volume_level)
        self.level_music.play()

    # Редактирование параметров уровня
    def tool(self, name):
        WidgetHandler.removeWidget(self.tool_buttons)
        WidgetHandler.removeWidget(self.mapping_buttons)
        WidgetHandler.removeWidget(self.color_dropdown)
        WidgetHandler.removeWidget(self.confirm_color_button)
        if name == 'delete level':
            if len([arg[1] for arg in os.walk('songs')][0]) == 1:
                self.mapping_buttons = self.generate_mapping_buttons()
                self.tool_buttons = self.generate_tool_buttons()
                self.color_dropdown = self.generate_color_dropdown()
                self.confirm_color_button = self.generate_confirm_color_button()
                return
            window = PauseMenu(self.level_background, 'cancel', 'delete')
            if window.state == 'delete':
                try:
                    os.remove(f'songs//{self.level_name}//bg.jpg')
                    os.remove(f'songs//{self.level_name}//level.json')
                    os.remove(f'songs//{self.level_name}//song.mp3')
                    os.rmdir(f'songs//{self.level_name}')
                    self.running = False
                    self.mapping_buttons = self.generate_mapping_buttons()
                    self.tool_buttons = self.generate_tool_buttons()
                    self.color_dropdown = self.generate_color_dropdown()
                    self.confirm_color_button = self.generate_confirm_color_button()
                    return
                except Exception as e:
                    logging.warning(e, exc_info=True)
        if name == 'rename':
            window = DialogWindow(self.level_background,
                                  description=['Enter new level name',
                                               f'Now - {self.level_name}'], data_type=str)
            new_name = window.text
            if new_name:
                new_name = new_name.strip()
                for _ in range(5):
                    try:
                        os.rename(f'songs//{self.level_name}', f'songs//{new_name}')
                        self.level_name = new_name
                        break
                    except Exception as e:
                        logging.warning(e, exc_info=True)
                        continue
        if name == 'set bg':
            screen.blit(self.default_bg, (0, 0))
            font = pygame.font.Font('materials\\Press Start 2P.ttf', int(75 * (screen_width / 1920)))
            text = font.render('select image', True, (124, 62, 249))
            screen.blit(text, text.get_rect(center=(screen_width // 2, screen_height - 200 * (screen_height / 1080))))
            pygame.display.update()
            new_name = filedialog.askopenfilename(filetypes=(("jpg image", "*.jpg"),), title='select new background')
            if new_name:
                self.level_background = pygame.transform.smoothscale(pygame.image.load(new_name),
                                                                     (screen_width, screen_height))
                old_bytes = open(new_name, mode='rb').read()
                open(f'songs//{self.level_name}//bg.jpg', mode='wb').write(old_bytes)
        if name == 'set up delta':
            window = DialogWindow(self.level_background,
                                  description=['Enter new up delta',
                                               '(percentage of change in the score',
                                               'scale from a successful hit)',
                                               f'Now - {self.common_data["delta_up"]}'], data_type=float)
            new_delta = window.text
            if new_delta or new_delta == 0:
                with open('songs\\' + self.level_name + '\\' + 'level.json') as f:
                    wl = json.load(f)
                    wl['common']['delta_up'] = new_delta
                with open('songs\\' + self.level_name + '\\' + 'level.json', mode='w') as f:
                    json.dump(wl, f)
        if name == 'set down delta':
            window = DialogWindow(self.level_background,
                                  description=['Enter new down delta',
                                               '(percentage of change in the score',
                                               'scale from a miss)',
                                               f'Now - {self.common_data["delta_down"]}'], data_type=float)
            new_delta = window.text
            if new_delta or new_delta == 0:
                with open('songs\\' + self.level_name + '\\' + 'level.json') as f:
                    wl = json.load(f)
                    wl['common']['delta_down'] = new_delta
                with open('songs\\' + self.level_name + '\\' + 'level.json', mode='w') as f:
                    json.dump(wl, f)
        if name == 'set bar speed':
            window = DialogWindow(self.level_background,
                                  description=['Enter new bar speed',
                                               '(percentage of change in the score scale every frame)',
                                               f'Now - {self.common_data["bar_speed"]}'], data_type=float)
            new_speed = window.text
            if new_speed or new_speed == 0:
                with open('songs\\' + self.level_name + '\\' + 'level.json') as f:
                    wl = json.load(f)
                    wl['common']['bar_speed'] = new_speed
                with open('songs\\' + self.level_name + '\\' + 'level.json', mode='w') as f:
                    json.dump(wl, f)
        if name == 'set speed':
            window = DialogWindow(self.level_background,
                                  description=['Enter new circle speed',
                                               '(how many seconds does it take to fill',
                                               f'Now - {self.common_data["speed"]}'], data_type=float)
            new_speed = window.text
            if new_speed:
                with open('songs\\' + self.level_name + '\\' + 'level.json') as f:
                    data = json.load(f)
                for index, circle in enumerate(data['circles']):
                    circle['time'] = circle['time'] - (new_speed - data['common']['speed'])
                    self.objects[index]['time'] = circle['time']
                data['common']['speed'] = new_speed
                with open('songs\\' + self.level_name + '\\' + 'level.json', mode='w') as f:
                    json.dump(data, f)
        if name == 'set radius':
            window = DialogWindow(self.level_background,
                                  description=['Enter new circle radius.',
                                               f'Now - {self.common_data["radius"]}'], data_type=float)
            new_radius = window.text
            if new_radius:
                with open('songs\\' + self.level_name + '\\' + 'level.json') as f:
                    data = json.load(f)
                data['common']['radius'] = new_radius
                with open('songs\\' + self.level_name + '\\' + 'level.json', mode='w') as f:
                    json.dump(data, f)
        with open('songs\\' + self.level_name + '\\' + 'level.json') as f:
            self.common_data = json.load(f)['common']
        self.mapping_buttons = self.generate_mapping_buttons()
        self.tool_buttons = self.generate_tool_buttons()
        self.color_dropdown = self.generate_color_dropdown()
        self.confirm_color_button = self.generate_confirm_color_button()
        self.button_invincible = self.frame


# Окно для создания уровня в реальном времени
class LiveMapWindow:
    def __init__(self, music, bg, common, objects, restarting, volume_level):
        self.music = pygame.mixer.Sound(music)
        pygame.mixer.music.load(music)
        self.bg = bg
        self.common_data = common
        self.bar_speed = 1 / ((self.music.get_length() + 3) * 60)
        self.time_upscaling = 0
        if not restarting:
            self.old_objects = objects
            self.time_upscaling = objects[-1]['time'] + common['speed']
            self.bar_percent = self.time_upscaling / self.music.get_length()
        else:
            self.old_objects = []
            self.bar_percent = -self.bar_speed
        self.objects = []
        self.running = True
        self.saving = True
        self.bar = self.generate_progress_bar()
        self.start_time = time()
        pygame.mixer.music.set_volume(volume_level)
        pygame.mixer.music.play(start=self.time_upscaling)
        self.run()

    # Цикл для вывода на экран
    def run(self):
        while self.running:
            screen.blit(self.bg, (0, 0))
            events = pygame.event.get()
            pygame_widgets.update(events)
            self.spawn_objects(events)
            self.check_exit_event(events)
            for circle in self.objects:
                circle.blit()
            cursor.update()
            pygame.display.update()
            clock.tick(60)
        WidgetHandler.removeWidget(self.bar)
        pygame.mixer.music.stop()

    # Создание объектов по клику на экран
    def spawn_objects(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                self.objects.append(MappingCircle(pos[0], pos[1], time() - self.start_time + self.time_upscaling))

    # Проверка на выход в меню
    def check_exit_event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or not pygame.mouse.get_focused():
                WidgetHandler.removeWidget(self.bar)
                pygame.mixer.music.pause()
                wait_time = time()
                pause_menu = PauseMenu(self.bg, 'continue', 'save and exit', 'exit without saving')
                if pause_menu.state == 'save and exit':
                    self.running = False
                if pause_menu.state == 'exit without saving':
                    self.saving = False
                    self.running = False
                else:
                    self.start_time += time() - wait_time
                    pygame.mixer.music.unpause()
                self.bar = self.generate_progress_bar()

    # Создание списка целей для json файла
    def pack(self):
        data = self.old_objects
        for circle in self.objects:
            data.append({'x': circle.x * (1920 / screen_width), 'y': circle.y * (1080 / screen_height),
                         'time': circle.start_time - self.common_data['speed']})
        return data

    # Создание progressbar для длины уровня
    def generate_progress_bar(self):
        score_bar = ProgressBar(screen, int(30 * (screen_width / 1920)), int(10 * (screen_height / 1080)),
                                int(1860 * (screen_width / 1920)), int(35 * (screen_height / 1080)),
                                self.update_bar_percent, curved=True, completedColour=(110, 0, 238),
                                incompletedColour=(187, 134, 252))
        return score_bar

    # Обновление значения progressbar
    def update_bar_percent(self):
        self.bar_percent += self.bar_speed
        if self.bar_percent >= 1:
            self.running = False
        return self.bar_percent


# Вспомогательное окно для класса LiveMapWindow
class MappingCircle:
    def __init__(self, x, y, start_time):
        self.image = pygame.transform.smoothscale(pygame.image.load('materials//livemapcircle.png'),
                                                  (50 * (screen_width / 1920), 50 * (screen_width / 1920)))
        self.x = x
        self.y = y
        self.start_time = start_time
        self.blit_frame = 0

    # Вывод нажатий на экран
    def blit(self):
        if self.blit_frame < 7:
            screen.blit(self.image, self.image.get_rect(center=(self.x, self.y)))
        self.blit_frame += 1


# Окно для проверки созданного уровня
class TestMenu:
    def __init__(self, common, objects, bg, music, volume_level):
        self.common = common
        self.bg = bg
        self.music = pygame.mixer.Sound(music)
        pygame.mixer.music.load(music)
        self.music.set_volume(volume_level)
        if not objects:
            return
        self.bar_speed = 1 / ((objects[-1]['time'] + common['speed'] + 3) * fps)
        self.bar_percent = -self.bar_speed
        self.bar = self.generate_bar()
        self.targets = self.unpack(objects)
        self.start_time = None
        self.running = True
        self.run()

    # Создание целей из json файла
    def unpack(self, objects):
        new = []
        radius = self.common['radius']
        max_radius = int(radius * (screen_width / 1920))
        outline_image = pygame.transform.smoothscale(pygame.image.load('materials//circle_out.png'),
                                                     (max_radius * 2 + 10 * (screen_width / 1920),
                                                      max_radius * 2 + 10 * (screen_width / 1920)))
        font = pygame.font.SysFont('roboto', max_radius * 2)
        fail_img = pygame.transform.smoothscale(pygame.image.load('materials\\circ_fail.png'), (max_radius, max_radius))
        suc_img = pygame.transform.smoothscale(pygame.image.load('materials\\circ_suc.png'), (max_radius, max_radius))
        for obj in objects:
            new.append(TargetCircle(x=obj['x'], y=obj['y'], start_time=obj['time'], speed=self.common['speed'],
                                    radius=self.common['radius'], key=pygame.K_c, cheats=True,
                                    color=self.common['color'], suc=suc_img,
                                    fail=fail_img, outline=outline_image, font=font, volume=self.music.get_volume()))
        return new

    # Создание progressbar для длины уровня
    def generate_bar(self):
        score_bar = ProgressBar(screen, int(30 * (screen_width / 1920)), int(10 * (screen_height / 1080)),
                                int(1860 * (screen_width / 1920)), int(35 * (screen_height / 1080)),
                                self.update_bar_percent, curved=True, completedColour=(110, 0, 238),
                                incompletedColour=(187, 134, 252))
        return score_bar

    # Обновление значения progressbar
    def update_bar_percent(self):
        self.bar_percent += self.bar_speed
        if self.bar_percent >= 1:
            self.running = False
        return self.bar_percent

    # Обработка событий для целей
    def object_events(self, events):
        if self.targets:
            self.targets[0].mark()
        for obj in self.targets:
            if obj.start_time > (time() - self.start_time):
                return
            obj.frame_update(events)
            if obj.hit_time:
                del self.targets[self.targets.index(obj)]

    # Проверка на выход в редактор уровня
    def check_exit_event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or not pygame.mouse.get_focused():
                pygame.mixer.music.pause()
                WidgetHandler.removeWidget(self.bar)
                wait_time = time()
                for obj in self.targets:
                    obj.pause()
                window = PauseMenu(self.bg, 'exit', 'continue')
                if window.state == 'exit':
                    self.running = False
                else:
                    self.start_time += time() - wait_time
                    for obj in self.targets:
                        obj.unpause()
                    pygame.mixer.music.unpause()
                self.bar = self.generate_bar()

    # Цикл для вывода на экран
    def run(self):
        pygame.mixer.music.play()
        self.start_time = time()
        while self.running:
            screen.blit(self.bg, (0, 0))
            events = pygame.event.get()
            self.object_events(events)
            pygame_widgets.update(events)
            self.check_exit_event(events)
            cursor.update()
            pygame.display.update()
            clock.tick(fps)
        WidgetHandler.removeWidget(self.bar)
        pygame.mixer.music.stop()


# Класс для управления аккаунтом
class AccountMenu:
    def __init__(self):
        self.running = True
        self.image = pygame.transform.smoothscale(pygame.image.load('materials//menu_bg.jpg'),
                                                  (screen_width, screen_height))
        self.image = pygame.transform.smoothscale(self.image, (screen_width, screen_height))
        self.buttons_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(15 * (screen_width / 1920)))
        self.buttons = self.generate_account_buttons()
        self.username_textbox = self.generate_username_textbox()
        self.password_textbox = self.generate_password_textbox()
        self.create_stats_toggle = self.generate_create_stats_toggle()
        self.login_stats_toggle = self.generate_login_stats_toggle()
        self.username_text, self.username_text_rect = self.generate_username_text()
        self.password_text, self.password_text_rect = self.generate_password_text()
        self.login_status_colour = self.generate_status_colour(0)
        self.create_status_colour = self.generate_status_colour(0)
        self.delete_status_colour = self.generate_status_colour(0)
        self.status_circle = ((screen_width - (700 * (screen_width // 1920))),
                              (screen_height - (420 * (screen_height // 1080))), (50 * (screen_height // 1080)))
        self.login_starttime = None
        self.create_starttime = None
        self.delete_starttime = None

    # Создание поля ввода имени пользователя
    @staticmethod
    def generate_username_textbox():
        font = pygame.font.Font('materials\\Ubuntu-Bold.ttf', int(45 * (screen_width / 1920)))
        textbox = TextBox(screen, int((screen_width / 2) - (400 * (screen_width / 1920))),
                          int(250 * (screen_height / 1080)),
                          int(800 * (screen_width / 1920)), int(75 * (screen_height / 1080)),
                          fontSize=int(75 * (screen_height / 1080)), textColour=(121, 78, 230),
                          radius=int(25 * (screen_height / 1080)), font=font
                          )
        if account_id:
            textbox.text = [db_connection.cursor().execute(
                """SELECT username FROM main WHERE id = ?""", (account_id,)).fetchone()[0]]
        return textbox

    # Создание поля ввода пароля
    @staticmethod
    def generate_password_textbox():
        font = pygame.font.Font('materials\\Ubuntu-Bold.ttf', int(45 * (screen_width / 1920)))
        textbox = TextBox(screen, int((screen_width / 2) - (400 * (screen_width / 1920))),
                          int(500 * (screen_height / 1080)),
                          int(800 * (screen_width / 1920)), int(75 * (screen_height / 1080)),
                          fontSize=int(75 * (screen_height / 1080)), textColour=(121, 78, 230),
                          radius=int(25 * (screen_height / 1080)), font=font
                          )
        return textbox

    # Создание переключателя переноса статистики при регистрации аккаунта
    @staticmethod
    def generate_create_stats_toggle():
        toggle = Toggle(screen, int(screen_width - (615 * (screen_width / 1920))),
                        int(screen_height - (315 * (screen_height / 1080))),
                        int(35 * (screen_width / 1920)), int(25 * (screen_height / 1080)),
                        startOn=True, onColour=(79, 239, 81), offColour=(176, 0, 32),
                        handleOnColour=(255, 255, 255), handleOffColour=(255, 255, 255),
                        handleRadius=int((15 * (screen_height / 1080)))
                        )
        return toggle

    # Создание переключателя переноса статистики при входе в аккаунт
    @staticmethod
    def generate_login_stats_toggle():
        toggle = Toggle(screen, int(screen_width - (615 * (screen_width / 1920))),
                        int(screen_height - (415 * (screen_height / 1080))),
                        int(35 * (screen_width / 1920)), int(25 * (screen_height / 1080)),
                        startOn=True, onColour=(79, 239, 81), offColour=(176, 0, 32),
                        handleOnColour=(255, 255, 255), handleOffColour=(255, 255, 255),
                        handleRadius=int((15 * (screen_height / 1080)))
                        )
        return toggle

    # Создание кнопок для управления аккаунтом
    def generate_account_buttons(self):
        width = 500 * (screen_width / 1920)
        height = (60 * (screen_height / 1080) + 30 * (screen_height / 1080)) * 4
        button_array = NewButtonArray(
            screen,
            int(screen_width // 2 - width // 2),
            int(650 * (screen_height / 1080)),
            int(width),
            int(height),
            (1, 4),
            border=30 * (screen_height / 1080),
            topBorder=0,
            bottomBorder=0,
            leftBorder=0,
            rightBorder=0,
            inactiveColours=[(77, 50, 145) for _ in range(4)],
            hoverColours=[(54, 35, 103) for _ in range(4)],
            pressedColours=[(121, 78, 230) for _ in range(4)],
            radii=[int(25 * (screen_height / 1080)) for _ in range(4)],
            fonts=[self.buttons_font for _ in range(4)],
            texts=['Login', 'Create', 'Delete', 'Return'],
            invisible=True,
            textColours=[(255, 255, 255) for _ in range(4)],
            onClicks=[lambda x: self.buttons_functions(x) for _ in range(4)],
            onClickParams=[['login'], ['create'], ['delete'], ['return']]
        )
        return button_array

    # Создание текста имени пользователя
    @staticmethod
    def generate_username_text():
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(40 * (screen_width / 1920)))
        text = font.render('Username', True, (124, 62, 249))
        text_rect = text.get_rect(center=(screen_width // 2, 200 * (screen_height / 1080)))
        return text, text_rect

    # Создание текста пароля
    @staticmethod
    def generate_password_text():
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(40 * (screen_width / 1920)))
        text = font.render('Password', True, (124, 62, 249))
        text_rect = text.get_rect(center=(screen_width // 2, 450 * (screen_height / 1080)))
        return text, text_rect

    # Возврат нужного цвета
    def generate_status_colour(self, arg, counter=None):
        colour = (150, 150, 150)
        if arg == 1:
            colour = (79, 239, 81)
        elif arg == 2:
            colour = (176, 0, 32)
        if colour != (150, 150, 150):
            if counter == 'login':
                self.login_starttime = time()
            if counter == 'create':
                self.create_starttime = time()
            if counter == 'delete':
                self.delete_starttime = time()
        return colour

    # Функции кнопок
    def buttons_functions(self, arg):
        username = self.username_textbox.getText()
        password = self.password_textbox.getText()
        if arg == 'login':
            self.login(username, password)
        elif arg == 'create':
            self.create(username, password)
        elif arg == 'delete':
            self.delete(username, password)
        elif arg == 'return':
            self.running = False

    # Вход в аккаунт
    def login(self, username, password):
        global account_id, account_id, anonymous_levels_played, anonymous_levels_won, anonymous_score,\
            anonymous_average_score, anonymous_average_rank, anonymous_successful, anonymous_average_accuracy,\
            anonymous_accuracy
        if db_connection.cursor().execute(
                """SELECT id FROM main WHERE username = ? AND password = ?""", (username, password)).fetchone():
            account_id = db_connection.cursor().execute(
                """SELECT id FROM main WHERE username = ? AND password = ?""", (username, password)).fetchone()[0]
            self.login_status_colour = self.generate_status_colour(1, 'login')
            if self.login_stats_toggle.getValue() and anonymous_levels_played:
                current_score = db_connection.cursor().execute(
                    """SELECT score FROM main WHERE id = ?""", (account_id,)).fetchone()[0]
                current_successful = db_connection.cursor().execute(
                    """SELECT successful FROM main WHERE id = ?""", (account_id,)).fetchone()[0]
                current_levels_played = db_connection.cursor().execute(
                    """SELECT levels_played FROM main WHERE id = ?""", (account_id,)).fetchone()[0]
                current_levels_won = db_connection.cursor().execute(
                    """SELECT levels_won FROM main WHERE id = ?""", (account_id,)).fetchone()[0]
                current_accuracy = db_connection.cursor().execute(
                    """SELECT accuracy FROM main WHERE id = ?""", (account_id,)).fetchone()[0]
                accuracy = current_accuracy + anonymous_accuracy
                average_accuracy = accuracy / (current_levels_played + anonymous_levels_played)
                average_rank = 'N'
                if average_accuracy >= 95:
                    average_rank = 'SS'
                elif average_accuracy >= 90:
                    average_rank = 'S'
                elif average_accuracy >= 80:
                    average_rank = 'A'
                elif average_accuracy >= 70:
                    average_rank = 'B'
                elif average_accuracy >= 60:
                    average_rank = 'C'
                elif average_accuracy < 60:
                    average_rank = 'D'
                db_connection.execute("""UPDATE main SET levels_played = ? WHERE id = ?""",
                                      (current_levels_played + anonymous_levels_played, account_id))
                db_connection.execute("""UPDATE main SET levels_won = ? WHERE id = ?""",
                                      (current_levels_won + anonymous_levels_won, account_id))
                db_connection.execute("""UPDATE main SET score = ? WHERE id = ?""",
                                      (current_score + anonymous_score, account_id))
                db_connection.execute("""UPDATE main SET average_score = ? WHERE id = ?""",
                                      ((anonymous_score + current_score) /
                                       (anonymous_levels_played + current_levels_played), account_id))
                db_connection.execute("""UPDATE main SET successful = ? WHERE id = ?""",
                                      (current_successful + anonymous_successful, account_id))
                db_connection.execute("""UPDATE main SET average_accuracy = ? WHERE id = ?""",
                                      (average_accuracy, account_id))
                db_connection.execute("""UPDATE main SET average_rank = ? WHERE id = ?""",
                                      (average_rank, account_id))
                db_connection.execute("""UPDATE main SET accuracy = ? WHERE id = ?""",
                                      (accuracy, account_id))
                db_connection.commit()
        else:
            self.login_status_colour = self.generate_status_colour(2, 'login')

    # Создание нового аккаунта
    def create(self, username, password):
        global account_id, anonymous_levels_played, anonymous_levels_won, anonymous_score, anonymous_average_score,\
            anonymous_average_rank, anonymous_successful, anonymous_average_accuracy, anonymous_accuracy
        if not (db_connection.cursor().execute(
                """SELECT id FROM main WHERE username = ?""", (username,)).fetchone()):
            db_connection.cursor().execute(
                """INSERT INTO main(username, password) VALUES(?, ?)""", (username, password))
            db_connection.commit()
            if db_connection.cursor().execute(
                    """SELECT id FROM main WHERE username = ? AND password = ?""", (username, password)).fetchone():
                account_id = db_connection.cursor().execute(
                    """SELECT id FROM main WHERE username = ? AND password = ?""", (username, password)).fetchone()[0]
                if self.create_stats_toggle.getValue():
                    db_connection.execute("""UPDATE main SET levels_played = ? WHERE id = ?""",
                                          (anonymous_levels_played, account_id))
                    db_connection.execute("""UPDATE main SET levels_won = ? WHERE id = ?""",
                                          (anonymous_levels_won, account_id))
                    db_connection.execute("""UPDATE main SET score = ? WHERE id = ?""",
                                          (anonymous_score, account_id))
                    db_connection.execute("""UPDATE main SET average_score = ? WHERE id = ?""",
                                          (anonymous_average_score, account_id))
                    db_connection.execute("""UPDATE main SET successful = ? WHERE id = ?""",
                                          (anonymous_successful, account_id))
                    db_connection.execute("""UPDATE main SET average_accuracy = ? WHERE id = ?""",
                                          (anonymous_average_accuracy, account_id))
                    db_connection.execute("""UPDATE main SET average_rank = ? WHERE id = ?""",
                                          (anonymous_average_rank, account_id))
                    db_connection.execute("""UPDATE main SET accuracy = ? WHERE id = ?""",
                                          (anonymous_accuracy, account_id))
                    db_connection.commit()
                anonymous_levels_played = 0
                anonymous_levels_won = 0
                anonymous_score = 0.0
                anonymous_average_score = 0
                anonymous_average_rank = 'N'
                anonymous_successful = 0
                anonymous_average_accuracy = 0.0
                anonymous_accuracy = 0.0
                self.create_status_colour = self.generate_status_colour(1, 'create')
        else:
            self.create_status_colour = self.generate_status_colour(2, 'create')

    # Удаление аккаунта
    def delete(self, username, password):
        global account_id
        if (db_connection.cursor().execute(
                """SELECT id FROM main WHERE username = ? AND password = ?""", (username, password)).fetchone()):
            WidgetHandler.removeWidget(self.buttons)
            WidgetHandler.removeWidget(self.username_textbox)
            WidgetHandler.removeWidget(self.password_textbox)
            WidgetHandler.removeWidget(self.create_stats_toggle)
            WidgetHandler.removeWidget(self.login_stats_toggle)
            window = PauseMenu(self.image, 'cancel', 'confirm', title='Would you like to confirm?')
            self.buttons = self.generate_account_buttons()
            self.username_textbox = self.generate_username_textbox()
            self.password_textbox = self.generate_password_textbox()
            self.create_stats_toggle = self.generate_create_stats_toggle()
            self.login_stats_toggle = self.generate_login_stats_toggle()
            if window.state == 'cancel':
                return
            self.username_textbox.text = []
            db_connection.cursor().execute(
                """DELETE FROM main WHERE username = ? AND password = ?""", (username, password))
            db_connection.commit()
            account_id = 0
            if not (db_connection.cursor().execute(
                    """SELECT id FROM main WHERE username = ? AND password = ?""", (username, password)).fetchone()):
                self.delete_status_colour = self.generate_status_colour(1, 'delete')
        else:
            self.delete_status_colour = self.generate_status_colour(2, 'delete')

    # Проверка выхода в меню
    def check_exit_event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    # Цикл для вывода на экран
    def run(self):
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(50 * (screen_width / 1920)))
        text = font.render('Login or create your account', True, (124, 62, 249))
        text_rect = text.get_rect(center=(screen_width // 2, 50 * (screen_height / 1080)))
        while self.running:
            screen.blit(self.image, (0, 0))
            screen.blit(text, text_rect)
            screen.blit(self.username_text, self.username_text_rect)
            screen.blit(self.password_text, self.password_text_rect)
            pygame.draw.circle(screen, self.login_status_colour, (int(screen_width - (675 * (screen_width / 1920))),
                                                                  int(screen_height - (398 * (screen_height / 1080)))),
                               int(25 * (screen_height / 1080)))
            pygame.draw.circle(screen, self.create_status_colour, (int(screen_width - (675 * (screen_width / 1920))),
                                                                   int(screen_height - (300 * (screen_height / 1080)))),
                               int(25 * (screen_height / 1080)))
            pygame.draw.circle(screen, self.delete_status_colour, (int(screen_width - (675 * (screen_width / 1920))),
                                                                   int(screen_height - (200 * (screen_height / 1080)))),
                               int(25 * (screen_height / 1080)))
            events = pygame.event.get()
            if self.login_starttime and time() - self.login_starttime >= 2:
                self.login_status_colour = self.generate_status_colour(0)
            if self.create_starttime and time() - self.create_starttime >= 2:
                self.create_status_colour = self.generate_status_colour(0)
            if self.delete_starttime and time() - self.delete_starttime >= 2:
                self.delete_status_colour = self.generate_status_colour(0)
            self.check_exit_event(events)
            pygame_widgets.update(events)
            cursor.update()
            pygame.display.update()
        WidgetHandler.removeWidget(self.buttons)
        WidgetHandler.removeWidget(self.username_textbox)
        WidgetHandler.removeWidget(self.password_textbox)
        WidgetHandler.removeWidget(self.create_stats_toggle)
        WidgetHandler.removeWidget(self.login_stats_toggle)
        close_animation()


# Класс для просмотра статистики
class StatsMenu:
    def __init__(self):
        self.running = True
        self.image = pygame.transform.smoothscale(pygame.image.load('materials//menu_bg.jpg'),
                                                  (screen_width, screen_height))
        self.image = pygame.transform.smoothscale(self.image, (screen_width, screen_height))
        self.buttons_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(15 * (screen_width / 1920)))
        self.buttons = self.generate_buttons()
        self.stats = self.generate_stats()
        self.stats_buttons = self.generate_stats_buttons()
        if self.stats_buttons:
            self.stats_buttons.disable()

    # Создание кнопок
    def generate_buttons(self):
        button_array = NewButtonArray(
            screen,
            int((screen_width // 2) - (350 * (screen_width / 1920))),
            int(screen_height - (100 * (screen_height / 1080))),
            int(350 * (screen_width / 1920)) * 2, int(75 * (screen_height / 1080)),
            (2, 1),
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
            texts=['reset', 'exit'],
            invisible=True,
            textColours=[(255, 255, 255) for _ in range(2)],
            onClicks=[lambda x: self.buttons_functions(x) for _ in range(2)],
            onClickParams=[['reset'], ['exit']]
        )
        return button_array

    # Создание статистики
    def generate_stats_buttons(self):
        if not self.stats:
            return
        width = 700 * (screen_width / 1920)
        height = (60 * (screen_height / 1080) + 20 * (screen_height / 1080)) * len(self.stats)
        button_array = NewButtonArray(
            screen,
            int(screen_width // 2 - width // 2),
            int(150 * (screen_height / 1080)),
            int(width),
            int(height),
            (1, len(self.stats)),
            border=30 * (screen_height / 1080),
            topBorder=0,
            bottomBorder=0,
            leftBorder=0,
            rightBorder=0,
            inactiveColours=[(77, 50, 145) for _ in range(len(self.stats))],
            hoverColours=[(54, 35, 103) for _ in range(len(self.stats))],
            pressedColours=[(121, 78, 230) for _ in range(len(self.stats))],
            radii=[int(25 * (screen_height / 1080)) for _ in range(len(self.stats))],
            fonts=[self.buttons_font for _ in range(len(self.stats))],
            texts=self.stats,
            invisible=True,
            textColours=[(255, 255, 255) for _ in range(len(self.stats))],
        )
        return button_array

    # Создание списка статистики
    @staticmethod
    def generate_stats():
        if account_id:
            name = 'nickname: ' + db_connection.execute(
                """SELECT username FROM main WHERE id = ?""", (account_id,)).fetchone()[0]
            levels_played = 'levels played: ' + str(db_connection.execute(
                """SELECT levels_played FROM main WHERE id = ?""", (account_id,)).fetchone()[0])
            levels_won = 'levels won: ' + str(db_connection.execute(
                """SELECT levels_won FROM main WHERE id = ?""", (account_id,)).fetchone()[0])
            successful = 'successful hits: ' + str(db_connection.execute(
                """SELECT successful FROM main WHERE id = ?""", (account_id,)).fetchone()[0])
            average_score = 'average score: ' + str(round(db_connection.execute(
                """SELECT average_score FROM main WHERE id = ?""", (account_id,)).fetchone()[0], 2))
            average_rank = 'average rank: ' + str(db_connection.execute(
                """SELECT average_rank FROM main WHERE id = ?""", (account_id,)).fetchone()[0])
            average_accuracy = 'average accuracy: ' + str(round(db_connection.execute(
                """SELECT average_accuracy FROM main WHERE id = ?""", (account_id,)).fetchone()[0], 2))
            return name, levels_played, levels_won, successful, average_score, average_rank, average_accuracy
        elif account_id == 0:
            name = 'nickname: Default User'
            levels_played = 'levels played: ' + str(anonymous_levels_played)
            levels_won = 'levels won: ' + str(anonymous_levels_won)
            successful = 'successful hits: ' + str(anonymous_successful)
            average_score = 'average score: ' + str(round(anonymous_average_score, 2))
            average_rank = 'average rank: ' + str(anonymous_average_rank)
            average_accuracy = 'average accuracy: ' + str(round(anonymous_average_accuracy, 2))
            return name, levels_played, levels_won, successful, average_score, average_rank, average_accuracy

    # Сброс статистики
    def reset_stats(self):
        global anonymous_levels_played, anonymous_levels_won, anonymous_score, anonymous_average_score,\
            anonymous_average_rank, anonymous_successful, anonymous_average_accuracy, anonymous_accuracy
        if account_id:
            db_connection.execute("""UPDATE main SET levels_played = ? WHERE id = ?""",
                                  (0, account_id))
            db_connection.execute("""UPDATE main SET levels_won = ? WHERE id = ?""",
                                  (0, account_id))
            db_connection.execute("""UPDATE main SET score = ? WHERE id = ?""",
                                  (0, account_id))
            db_connection.execute("""UPDATE main SET average_score = ? WHERE id = ?""",
                                  (0.0, account_id))
            db_connection.execute("""UPDATE main SET successful = ? WHERE id = ?""",
                                  (0, account_id))
            db_connection.execute("""UPDATE main SET average_accuracy = ? WHERE id = ?""",
                                  (0.0, account_id))
            db_connection.execute("""UPDATE main SET average_rank = ? WHERE id = ?""",
                                  ('N', account_id))
            db_connection.execute("""UPDATE main SET accuracy = ? WHERE id = ?""",
                                  (0.0, account_id))
            db_connection.commit()
            self.stats = self.generate_stats()
        elif account_id == 0:
            anonymous_levels_played = 0
            anonymous_levels_won = 0
            anonymous_score = 0.0
            anonymous_average_score = 0
            anonymous_average_rank = 'N'
            anonymous_successful = 0
            anonymous_average_accuracy = 0.0
            anonymous_accuracy = 0.0
            self.stats = self.generate_stats()

    # Функции кнопок
    def buttons_functions(self, name):
        if name == 'exit':
            self.running = False
        elif name == 'reset':
            WidgetHandler.removeWidget(self.buttons)
            WidgetHandler.removeWidget(self.stats_buttons)
            window = PauseMenu(self.image, 'cancel', 'confirm', title='Reset your stats?')
            if window.state == 'confirm':
                self.reset_stats()
            self.buttons = self.generate_buttons()
            self.stats_buttons = self.generate_stats_buttons()
            self.stats_buttons.disable()

    # Проверка на выход в меню
    def check_exit_event(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False

    # Цикл для вывода на экран
    def run(self):
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(50 * (screen_width / 1920)))
        text = font.render('Your stats', True, (124, 62, 249))
        text_rect = text.get_rect(center=(screen_width // 2, 50 * (screen_height / 1080)))
        while self.running:
            screen.blit(self.image, (0, 0))
            screen.blit(text, text_rect)
            events = pygame.event.get()
            self.check_exit_event(events)
            pygame_widgets.update(events)
            cursor.update()
            pygame.display.update()
        WidgetHandler.removeWidget(self.buttons)
        if self.stats_buttons:
            WidgetHandler.removeWidget(self.stats_buttons)
        close_animation()


# Окно меню паузы
class PauseMenu:
    def __init__(self, bg, *args, **kwargs):
        self.bg_image = bg
        self.state = ''
        self.text = args
        self.music = kwargs.get('music', [None for _ in args])
        self.title = kwargs.get('title', None)
        self.buttons = self.generate_buttons()
        self.running = True
        self.run()

    # Создание кнопок
    def generate_buttons(self):
        width = 500 * (screen_width / 1920)
        height = (60 * (screen_height / 1080) + 30 * (screen_height / 1080)) * len(self.text)
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(15 * (screen_width / 1920)))
        button_array = NewButtonArray(
            screen,
            int(screen_width // 2 - width // 2),
            int(250 * (screen_height / 1080)),
            int(width),
            int(height),
            (1, len(self.text)),
            border=30 * (screen_height / 1080),
            topBorder=0,
            bottomBorder=0,
            leftBorder=0,
            rightBorder=0,
            inactiveColours=[(77, 50, 145) for _ in range(len(self.text))],
            hoverColours=[(54, 35, 103) for _ in range(len(self.text))],
            pressedColours=[(121, 78, 230) for _ in range(len(self.text))],
            radii=[int(25 * (screen_height / 1080)) for _ in range(len(self.text))],
            fonts=[font for _ in range(len(self.text))],
            texts=self.text,
            invisible=True,
            textColours=[(255, 255, 255) for _ in range(len(self.text))],
            onClicks=[lambda x: self.update_state(x) for _ in range(len(self.text))],
            onClickParams=[[i] for i in self.text]
        )
        return button_array

    # Обновление состояния
    def update_state(self, state):
        self.state = state
        self.running = False

    # Вывод на экран
    def blit(self):
        screen.blit(self.bg_image, (0, 0))
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(50 * (screen_width / 1920)))
        text = font.render(self.title, True, (124, 62, 249))
        text_rect = text.get_rect(center=(screen_width // 2, 50 * (screen_height / 1080)))
        screen.blit(text, text_rect)

    # Цикл для вывода на экран
    def run(self):
        while self.running:
            self.blit()
            events = pygame.event.get()
            pygame_widgets.update(events)
            for e in events:
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    self.state = self.text[0]
                    self.running = False
            cursor.update()
            pygame.display.update()
        music = self.music[self.text.index(self.state)]
        if music:
            pygame.mixer.Sound(music).play()
        WidgetHandler.removeWidget(self.buttons)


# Окно результатов игры
class GameResultMenu:
    def __init__(self, state, suc=0, total=0, diff='', len_possible=None):
        self.state = state
        if total == 0:
            self.accuracy = 100
        else:
            self.accuracy = round(suc / total * 100, 2)
        if state == 'win':
            self.bg = pygame.transform.smoothscale(pygame.image.load('materials//win.jpg'),
                                                   (screen_width, screen_height))
        else:
            self.bg = pygame.transform.smoothscale(pygame.image.load('materials//loose.jpg'),
                                                   (screen_width, screen_height))
        self.successful = suc
        self.len_possible = len_possible
        self.total = total
        self.difficult = diff
        if account_id:
            self.current_score = db_connection.cursor().execute(
                """SELECT score FROM main WHERE id = ?""", (account_id, )).fetchone()[0]
            self.current_successful = db_connection.cursor().execute(
                """SELECT successful FROM main WHERE id = ?""", (account_id, )).fetchone()[0]
            self.current_levels_played = db_connection.cursor().execute(
                """SELECT levels_played FROM main WHERE id = ?""", (account_id, )).fetchone()[0]
            self.current_levels_won = db_connection.cursor().execute(
                """SELECT levels_won FROM main WHERE id = ?""", (account_id, )).fetchone()[0]
            self.current_average_score = db_connection.cursor().execute(
                """SELECT average_score FROM main WHERE id = ?""", (account_id, )).fetchone()[0]
            self.current_average_rank = db_connection.cursor().execute(
                """SELECT average_rank FROM main WHERE id = ?""", (account_id, )).fetchone()[0]
            self.current_average_accuracy = db_connection.cursor().execute(
                """SELECT average_accuracy FROM main WHERE id = ?""", (account_id, )).fetchone()[0]
            self.current_accuracy = db_connection.cursor().execute(
                """SELECT accuracy FROM main WHERE id = ?""", (account_id, )).fetchone()[0]
        self.running = True
        self.run()

    # Вывод на экран
    def blit(self):
        global anonymous_levels_won
        screen.blit(self.bg, (0, 0))
        big_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(100 * (screen_width / 1920)))
        small_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(50 * (screen_width / 1920)))
        if self.state == 'loose':
            text = big_font.render('LOOSE!', True, (124, 62, 249))
            screen.blit(text, text.get_rect(center=(screen_width // 2, 75 * (screen_height / 1080))))
            text = small_font.render(f'percentage of completion - {round(self.total / self.len_possible * 100, 2)}%',
                                     True, (124, 62, 249))
            screen.blit(text, text.get_rect(center=(screen_width // 2, 600 * (screen_height / 1080))))
        else:
            text = big_font.render('WIN!', True, (124, 62, 249))
            screen.blit(text, text.get_rect(center=(screen_width // 2, 75 * (screen_height / 1080))))
            if account_id:
                self.current_levels_won += 1
            elif account_id == 0:
                anonymous_levels_won += 1
        text = small_font.render(f'accuracy - {self.accuracy}%', True, (124, 62, 249))
        screen.blit(text, text.get_rect(center=(screen_width // 2, 200 * (screen_height / 1080))))
        text = small_font.render(f'successful - {self.successful}', True, (124, 62, 249))
        screen.blit(text, text.get_rect(center=(screen_width // 2, 300 * (screen_height / 1080))))
        text = small_font.render(f'total - {self.total}', True, (124, 62, 249))
        screen.blit(text, text.get_rect(center=(screen_width // 2, 400 * (screen_height / 1080))))
        text = small_font.render(f'difficult - {self.difficult}', True, (124, 62, 249))
        screen.blit(text, text.get_rect(center=(screen_width // 2, 500 * (screen_height / 1080))))

    # Обновление данных в базе данных
    def update_database(self):
        self.current_levels_played += 1
        self.current_score += self.total
        self.current_successful += self.successful
        self.current_average_score = self.current_score / self.current_levels_played
        self.current_accuracy += self.accuracy
        self.current_average_accuracy = self.current_accuracy / self.current_levels_played
        if self.current_average_accuracy >= 95:
            self.current_average_rank = 'SS'
        elif self.current_average_accuracy >= 90:
            self.current_average_rank = 'S'
        elif self.current_average_accuracy >= 80:
            self.current_average_rank = 'A'
        elif self.current_average_accuracy >= 70:
            self.current_average_rank = 'B'
        elif self.current_average_accuracy >= 60:
            self.current_average_rank = 'C'
        elif self.current_average_accuracy < 60:
            self.current_average_rank = 'D'
        db_connection.execute("""UPDATE main SET levels_played = ? WHERE id = ?""",
                              (self.current_levels_played, account_id))
        db_connection.execute("""UPDATE main SET levels_won = ? WHERE id = ?""",
                              (self.current_levels_won, account_id))
        db_connection.execute("""UPDATE main SET score = ? WHERE id = ?""",
                              (self.current_score, account_id))
        db_connection.execute("""UPDATE main SET average_score = ? WHERE id = ?""",
                              (self.current_average_score, account_id))
        db_connection.execute("""UPDATE main SET successful = ? WHERE id = ?""",
                              (self.current_successful, account_id))
        db_connection.execute("""UPDATE main SET average_accuracy = ? WHERE id = ?""",
                              (self.current_average_accuracy, account_id))
        db_connection.execute("""UPDATE main SET average_rank = ? WHERE id = ?""",
                              (self.current_average_rank, account_id))
        db_connection.execute("""UPDATE main SET accuracy = ? WHERE id = ?""",
                              (self.accuracy, account_id))
        db_connection.commit()

    # Обновление данных стандартного пользователя
    def update_anonymous_stats(self):
        global anonymous_levels_played, anonymous_levels_won, anonymous_score, anonymous_average_score,\
            anonymous_average_rank, anonymous_successful, anonymous_average_accuracy, anonymous_accuracy
        anonymous_levels_played += 1
        anonymous_score += self.total
        anonymous_successful += self.successful
        anonymous_average_score = anonymous_score / anonymous_levels_played
        anonymous_accuracy += self.accuracy
        anonymous_average_accuracy = anonymous_accuracy / anonymous_levels_played
        if anonymous_average_accuracy >= 95:
            anonymous_average_rank = 'SS'
        elif anonymous_average_accuracy >= 90:
            anonymous_average_rank = 'S'
        elif anonymous_average_accuracy >= 80:
            anonymous_average_rank = 'A'
        elif anonymous_average_accuracy >= 70:
            anonymous_average_rank = 'B'
        elif anonymous_average_accuracy >= 60:
            anonymous_average_rank = 'C'
        elif anonymous_average_accuracy < 60:
            anonymous_average_rank = 'D'

    # Цикл для вывода на экран
    def run(self):
        self.blit()
        if account_id:
            self.update_database()
        elif account_id == 0:
            self.update_anonymous_stats()
        cursor.hide(mouse_hiding=True)
        pygame.display.update()
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    self.running = False
        cursor.show()


# Окно для уровней с пустым json файлом
class EmptyLevelWindow:
    def __init__(self):
        self.bg = pygame.transform.smoothscale(pygame.image.load('materials//empty.jpg'), (screen_width, screen_height))
        self.font = pygame.font.Font('materials\\Press Start 2P.ttf', int(50 * (screen_width / 1920)))
        self.running = True
        self.run()

    # Цикл для вывода на экран
    def run(self):
        self.blit()
        cursor.hide(mouse_hiding=True)
        pygame.display.update()
        while self.running:
            for e in pygame.event.get():
                if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                    self.running = False
        cursor.show()

    # Вывод на экран
    def blit(self):
        screen.blit(self.bg, (0, 0))
        render = self.font.render('This is empty level', True, (124, 62, 249))
        screen.blit(render, render.get_rect(center=(screen_width // 2, 50 * (screen_height / 1080))))


# Окно для ввода информации
class DialogWindow:
    def __init__(self, bg, description, data_type):
        self.texts = description
        self.text = None
        self.bg = bg
        self.data_type = data_type
        self.entering = self.generate_entering()
        self.buttons = self.generate_buttons()
        self.running = True
        self.run()

    # Создание поля для ввода информации
    def generate_entering(self):
        width = 800 * (screen_width / 1920)
        height = 80 * (screen_height / 1080)
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(35 * (screen_width / 1920)))
        textbox = TextBox(screen, int(screen_width // 2 - width // 2), int(screen_height // 2 - height // 2),
                          int(width), int(height), fontSize=50, borderColour=(77, 50, 145), font=font,
                          textColour=(121, 78, 230), onSubmit=lambda: self.change_text(True), radius=10,
                          borderThickness=5)
        return textbox

    # Создание кнопок
    def generate_buttons(self):
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(10 * (screen_width / 1920)))
        button_array = NewButtonArray(
            screen,
            screen_width // 2, int(screen_height // 2 + 150 * (screen_height / 1920)),
            int(200 * (screen_width / 1920)) * 2, int(50 * (screen_height / 1080)),
            (2, 1),
            border=30 * (screen_height / 1080),
            topBorder=0,
            bottomBorder=0,
            leftBorder=0,
            rightBorder=0,
            inactiveColours=[(77, 50, 145) for _ in range(2)],
            hoverColours=[(54, 35, 103) for _ in range(2)],
            pressedColours=[(121, 78, 230) for _ in range(2)],
            radii=[int(25 * (screen_height / 1080)) for _ in range(2)],
            fonts=[font for _ in range(2)],
            texts=['OK', 'cancel'],
            invisible=True,
            textColours=[(255, 255, 255) for _ in range(2)],
            onClicks=[lambda x: self.change_text(x) for _ in range(2)],
            onClickParams=[[True], [False]]
        )
        return button_array

    # Проверка и сохранение данных
    def change_text(self, condition):
        if condition:
            self.text = self.entering.getText()
            try:
                self.text = self.data_type(self.text)
            except ValueError:
                self.text = None
        self.running = False

    # Цикл для вывода на экран
    def run(self):
        font = pygame.font.Font('materials\\Press Start 2P.ttf', int(35 * (screen_width / 1920)))
        while self.running:
            screen.blit(self.bg, (0, 0))
            y = 250 * (screen_height / 1080)
            for text in self.texts:
                render = font.render(text, True, (255, 255, 255))
                screen.blit(render, render.get_rect(center=(screen_width // 2, y)))
                y += 40 * (screen_height / 1080)
            pygame_widgets.update(pygame.event.get())
            cursor.update()
            pygame.display.update()
        WidgetHandler.removeWidget(self.entering)
        WidgetHandler.removeWidget(self.buttons)


# Окно инструкции
class InstructionsWindow:
    def __init__(self):
        self.buttons_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(15 * (screen_width / 1920)))
        self.big_font = pygame.font.Font('materials\\Press Start 2P.ttf', int(30 * (screen_width / 1920)))
        self.buttons = self.generate_buttons()
        with open('system//instructions.txt', encoding='utf-8') as file:
            self.pages = file.read().split('***')
        self.line = 1
        self.step = 12
        self.image = pygame.transform.smoothscale(pygame.image.load('materials//menu_bg.jpg'),
                                                  (screen_width, screen_height))
        self.image.set_alpha(20)
        self.page_num = 0
        self.current_page = self.generate_page()
        self.running = True

    # Создание кнопок
    def generate_buttons(self):
        button_array = NewButtonArray(
            screen,
            int((screen_width // 2) - (520 * (screen_width / 1920))),
            int(screen_height - (100 * (screen_height / 1080))),
            int(350 * (screen_width / 1920)) * 3, int(75 * (screen_height / 1080)),
            (3, 1),
            border=30 * (screen_height / 1080),
            topBorder=0,
            bottomBorder=0,
            leftBorder=0,
            rightBorder=0,
            inactiveColours=[(77, 50, 145) for _ in range(3)],
            hoverColours=[(54, 35, 103) for _ in range(3)],
            pressedColours=[(121, 78, 230) for _ in range(3)],
            radii=[int(25 * (screen_height / 1080)) for _ in range(3)],
            fonts=[self.buttons_font for _ in range(3)],
            texts=['previous page', 'next page', 'exit'],
            invisible=True,
            textColours=[(255, 255, 255) for _ in range(3)],
            onClicks=[lambda x: self.buttons_functions(x) for _ in range(3)],
            onClickParams=[['prev'], ['next'], ['exit']]
        )
        return button_array

    # Прокрутка текста колесом мыши
    def spin(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    if self.line < len(self.current_page) - 1:
                        self.line += 1
                elif event.button == 4:
                    if self.line > 1:
                        self.line -= 1

    # Функции кнопок
    def buttons_functions(self, arg):
        if arg == 'next':
            if self.page_num < len(self.pages) - 1:
                self.page_num += 1
        if arg == 'prev':
            if self.page_num >= 1:
                self.page_num -= 1
        if arg == 'exit':
            self.running = False
        self.line = 1
        self.current_page = self.generate_page()

    # Вывод инутсрукции на экран
    def blit(self):
        pygame.draw.rect(screen, 'black', (0, 0, screen_width, screen_height))
        screen.blit(self.image, (0, 0))
        render = self.big_font.render(f'page {self.page_num + 1}', True, (160, 160, 160))
        screen.blit(render, render.get_rect(center=(screen_width // 2, 900 * (screen_height / 1080))))
        render = self.big_font.render(f'scroll↓', True, (160, 160, 160))
        screen.blit(render, render.get_rect(center=(screen_width // 2, 50 * (screen_height / 1080))))
        render = self.big_font.render(self.current_page[0], True, (160, 160, 160))
        screen.blit(render, render.get_rect(center=(screen_width // 2, 200 * (screen_height / 1080))))
        y = 250 * (screen_height / 1080)
        for line in range(self.line, min([self.line + self.step, len(self.current_page)])):
            render = self.big_font.render(self.current_page[line][:-1], True, (160, 160, 160))
            screen.blit(render, render.get_rect(center=(screen_width // 2, y)))
            y += 50 * (screen_height / 1080)

    # Создание текста страницы инструкции
    def generate_page(self):
        words = self.pages[self.page_num].split()
        title = words[0]
        page = [title]
        words = words[1:]
        word_index = 0
        while word_index != len(words):
            line = ''
            while word_index < len(words) and len(line) + len(words[word_index]) <= 50:
                line += words[word_index] + ' '
                word_index += 1
            page.append(line)
        return page

    # Проверка на выход в меню
    def check_exit_events(self, events):
        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.running = False

    # Вывод на экран
    def run(self):
        while self.running:
            events = pygame.event.get()
            self.check_exit_events(events)
            self.blit()
            self.spin(events)
            pygame_widgets.update(events)
            cursor.update()
            pygame.display.update()
        WidgetHandler.removeWidget(self.buttons)


running = True


# Основной цикл игры
def main():
    global running
    logging.info('Create new session')
    intro()
    settings_data = [100, 'normal', False]
    while running:
        menu = Menu(settings_data)
        menu.run()
        settings_data = [menu.volume_level, menu.difficult, menu.menu_song.get_volume() == 0]
        script = menu.script
        if script == 'game':
            logging.info(f'start game on {menu.level_name}')
            game = Game(menu.level_name, menu.difficult, menu.volume_level)
            game.run()
        elif script == 'editor':
            if menu.level_name:
                logging.info(f'start editor on {menu.level_name}')
            else:
                logging.info(f'start editior on new level')
            editor = LevelEditor(menu.level_name, menu.volume_level / 100)
            editor.run()
        elif script == 'account':
            logging.info(f'start account')
            account = AccountMenu()
            account.run()
        elif script == 'stats':
            logging.info(f'start stats')
            stats = StatsMenu()
            stats.run()
        elif script == 'instructions':
            logging.info(f'start instructions')
            instructions = InstructionsWindow()
            instructions.run()


if __name__ == '__main__':
    try:
        main()
    except Exception as exception:
        logging.critical(exception, exc_info=True)
        logging.shutdown()
        pygame.mouse.set_visible(True)
        os.rename(log_name, log_name[:log_name.rfind('//') + 1] + "FATAL!!! " + log_name[log_name.rfind('//') + 2:])
        messagebox.showerror(message="Game crashed, you can see log file in launcher", title='game has been crashed')
