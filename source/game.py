import pygame
import json
from menu import screen, fps, clock, screen_width, screen_height


# Основной класс игры
class GameCore:
    def __init__(self, level_name, difficult):
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

    @staticmethod
    def check_exit_event(events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
        return False
