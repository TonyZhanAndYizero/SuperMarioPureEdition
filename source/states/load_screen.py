from ..components import info
from .. import sound
import pygame


class LoadScreen:
    def start(self, game_info, current_time):
        self.game_info = game_info
        self.game_info['states'] = 'load_screen'
        self.finished = False
        self.next = 'level'
        self.duration = 2000
        self.timer = 0
        self.info = info.Info('load_screen', self.game_info)
        self.sound = sound.Sound()

    def update(self, surface, keys, current_time,mouse,mouse_xy):
        self.current_time = current_time
        self.draw(surface)
        if self.timer == 0:
            self.timer = pygame.time.get_ticks()
        elif pygame.time.get_ticks() - self.timer > self.duration:
            self.finished = True
            self.timer = 0

    def draw(self, surface: pygame.Surface):
        surface.fill((0, 0, 0))
        self.info.update(self.game_info)
        self.info.draw(surface)


class Load_level2(LoadScreen):
    def __init__(self):
        LoadScreen.__init__(self)

    def start(self, game_info, current_time):
        self.game_info = game_info
        self.game_info['states'] = 'load_level2'
        self.finished = False
        self.next = 'level2'
        self.duration = 5000
        self.timer = 0
        self.info = info.Info('load_level2', self.game_info)
        self.sound = sound.Sound()


class Load_level3(LoadScreen):
    def __init__(self):
        LoadScreen.__init__(self)

    def start(self, game_info, current_time):
        self.game_info = game_info
        self.game_info['states'] = 'load_level3'
        self.finished = False
        self.next = 'level3'
        self.duration = 5000
        self.timer = 0
        self.info = info.Info('load_level3', self.game_info)
        self.sound = sound.Sound()


class Load_level4(LoadScreen):
    def __init__(self):
        LoadScreen.__init__(self)

    def start(self, game_info, current_time):
        self.game_info = game_info
        self.game_info['states'] = 'load_level4'
        self.finished = False
        self.next = 'level4'
        self.duration = 5000

        self.timer = 0
        self.info = info.Info('load_level4', self.game_info)
        self.sound = sound.Sound()


class GameOver(LoadScreen):  # a sub class!!! Learning that the knew class succeed all the legacy of its class
    def __init__(self):
        pass

    def start(self, game_info, current_time):  # no need to sub class
        game_info['lives'] = 1
        game_info['score'] = 0
        game_info['coin'] = 0

        self.game_info = game_info
        self.game_info['states'] = 'game_over'
        self.finished = False
        self.duration = 4000
        self.next = 'main_menu'
        self.timer = 0
        self.info = info.Info('game_over', self.game_info)
