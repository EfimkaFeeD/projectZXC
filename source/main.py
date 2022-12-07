import os
import pygame
import pygame_widgets
from pygame_widgets.button import ButtonArray


FPS = 144
pygame.init()
screen_width = pygame.display.Info().current_w
screen_height = pygame.display.Info().current_h
max_w, max_h = screen_width, screen_height
screen = pygame.display.set_mode((screen_width, screen_height))


# Переопределение класса из библеотеки pyбавления
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


class Menu:
    def __init__(self, s):
        self.screen = s
        self.difficult = 'medium'
        self.menu_song = pygame.mixer.Sound('materials//menu_mc.mp3')
        self.menu_song.play()
        self.song_list = [arg[1] for arg in os.walk('songs')][0]
        self.level_name = ''
        self.spin = 0
        self.menu_image = pygame.image.load('materials//menu_bg.jpg')
        self.menu_image = pygame.transform.smoothscale(self.menu_image, (screen_width, screen_height))
        self.buttons = []
        width = 500 * (screen_width / 1920)
        height = 500 * (screen_height / 1080)
        self.song_name = ''
        fonts = pygame.font.SysFont('roboto', int(35 * (screen_width / 1920)))
        # Создание списка кнопок
        self.buttonArray = NewButtonArray(
            self.screen,
            screen_width // 2 - width // 2,
            100 * (screen_height / 1080),
            width,
            height,
            (1, len(self.song_list)),
            border=100,
            topBorder=0,
            bottomBorder=0,
            leftBorder=0,
            rightBorder=0,
            inactiveColours=[(77, 50, 145) for _ in range(len(self.song_list))],
            hoverColours=[(54, 35, 103) for _ in range(len(self.song_list))],
            pressedColours=[(121, 78, 230) for _ in range(len(self.song_list))],
            radii=[25 for _ in range(len(self.song_list))],
            fonts=[fonts for _ in range(len(self.song_list))],
            texts=self.song_list,
            colour=(255, 255, 255),
            invisible=True,
            onClicks=[lambda x: self.get_song_name(x) for _ in range(len(self.song_list))],
            onClickParams=[[i] for i in range(len(self.song_list))]
        )

    # Обновление названия трека
    def get_song_name(self, index):
        self.song_name = self.song_list[index]

    # Вывод текста и заднего фона
    def blit(self):
        self.screen.blit(self.menu_image, self.menu_image.get_rect(center=(screen_width // 2, screen_height // 2)))
        font = pygame.font.SysFont('roboto', int(100 * (screen_width / 1920)))
        songs_text = font.render('Your Songs:', True, (255, 255, 255))
        songs_text_rect = songs_text.get_rect(center=(screen_width // 2, 50 * (screen_height / 1080)))
        self.screen.blit(songs_text, songs_text_rect)

    # Обновление всех виджетов
    def update_widgets(self, event):
        pygame_widgets.update(event)


menu = Menu(screen)
clock = pygame.time.Clock()
running = True
while running:
    menu.blit()
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    menu.update_widgets(events)
    pygame.display.update()
    clock.tick(FPS)
