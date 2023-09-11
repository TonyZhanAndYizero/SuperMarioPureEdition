import pygame, os
from .. import setup
from .. import tools
from .. import consts, sound
from ..components import info


class Main_menu:
    def __init__(self):
        game_info = {
            'score': 0,
            'top_score': 0,
            'coin': 0,
            'lives': 1,
            'player_state': 'small',
            'states': 'main_menu',
            'current_time': 0,
            'time': 401
        }
        self.start(game_info, 0)
        self.sound = sound.Sound()

    def start(self, game_info, current_time):  # to make it cyclable, and a start stage
        self.current_time = current_time
        self.game_info = game_info
        self.finished = False
        self.info = info.Info('main_menu', self.game_info)
        self.next = 'load_screen'
        self.setup_background()
        self.setup_player()
        self.setup_cursor()

    def setup_background(self):
        self.background = setup.graphics['level_1']  # Surface
        # print(self.background)
        self.background_rect = self.background.get_rect()  # return a class of picture pixel info
        # print(self.background_rect)
        self.background = pygame.transform.scale(self.background,
                                                 (int(self.background_rect.width * consts.BG_MULTI_TIMES),
                                                  int(self.background_rect.height * consts.BG_MULTI_TIMES)))
        self.viewerside = setup.screen.get_rect()
        self.title = tools.get_image(setup.graphics['title_screen'], 1, 60, 176, 88, (255, 0, 22),
                                     consts.BG_MULTI_TIMES)

    def setup_player(self):
        self.player_image = tools.get_image(setup.graphics['mario_bros'], 178, 32, 12, 16, (0, 0, 0),
                                            consts.BG_PLAYER_CURSOR_TIMES)

    def setup_cursor(self):
        self.cursor = pygame.sprite.Sprite()
        self.cursor_image = tools.get_image(setup.graphics['item_objects'], 24, 160, 8.5, 8, (0, 0, 0),
                                            consts.BG_PLAYER_CURSOR_TIMES)
        rect = self.cursor_image.get_rect()
        rect.x, rect.y = (220, 367)
        self.cursor_rect = rect
        self.cursor_state = '1P'

    def update_cursor(self, keys):
        if keys[pygame.K_w]:
            self.cursor_state = '1P'
            self.cursor_rect.x = 220
            self.cursor_rect.y = 367
        elif keys[pygame.K_s]:
            self.cursor_state = '2P'
            self.cursor_rect.x = 70
            self.cursor_rect.y = 412.4
        elif keys[pygame.K_RETURN]:
            self.reset_info()
            if self.cursor_state == '1P':
                self.finished = True
                self.sound.stop_music()
                self.sound.sound('one_up')
            elif self.cursor_state == '2P':
                self.finished = True
                self.sound.stop_music()
                self.next = 'TOBEDONE'

    def update(self, surface: pygame.Surface, keys, current_time, mouse,mouse_xy):
        if not pygame.mixer.music.get_busy():
            self.sound.music('main_theme_sped_up', 0.5)
        self.current_time = current_time
        self.game_info['current_time'] = self.current_time
        self.update_cursor(keys)

        # stationary form
        surface.blit(self.background, self.viewerside)
        surface.blit(self.title, (170, 100))
        surface.blit(self.player_image, (110, 492))
        surface.blit(self.cursor_image, self.cursor_rect)

        self.info.update(self.game_info)
        self.info.draw(surface)

    def reset_info(self):
        temp = self.game_info['top_score']
        self.game_info = {
            'score': 0,
            'top_score': temp,
            'coin': 0,
            'lives': 1,
            'player_state': 'small',
            'states': 'main_menu',
            'current_time': 0,
            'time': 401
        }


class TOBEDONE(Main_menu):
    def __init__(self):
        Main_menu.__init__(self)

    def start(self, game_info, current_time):  # to make it cyclable, and a start stage
        self.current_time = current_time
        self.game_info = game_info
        self.finished = False
        self.info = info.Info('TOBEDONE', self.game_info)
        self.next = 'main_menu'
        self.setup_background()

    def setup_background(self):
        self.background = setup.graphics['level_1']  # Surface
        # print(self.background)
        self.background_rect = self.background.get_rect()  # return a class of picture pixel info
        # print(self.background_rect)
        self.background = pygame.transform.scale(self.background,
                                                 (int(self.background_rect.width * consts.BG_MULTI_TIMES - 0.05),
                                                  int(self.background_rect.height * consts.BG_MULTI_TIMES - 0.05)))
        self.viewerside = setup.screen.get_rect()

    def update(self, surface: pygame.Surface, keys, current_time, mouse,mouse_xy):
        if not pygame.mixer.music.get_busy():
            self.sound.music('world_wanderer', 0.3)
        self.current_time = current_time
        self.game_info['current_time'] = self.current_time
        surface.blit(self.background, self.viewerside)
        self.info.update(self.game_info)
        self.info.draw(surface)
        if keys[pygame.K_k]:
            self.sound.stop_music()
            self.finished = True


class GameWin(TOBEDONE):
    def __init__(self):
        self.sound = sound.Sound()

    def start(self, game_info, current_time):  # to make it cyclable, and a start stage
        self.current_time = current_time
        self.game_info = game_info
        if self.game_info['top_score'] < self.game_info['score']:
            self.game_info['top_score'] = self.game_info['score']
        self.finished = False
        self.info = info.Info('game_win', self.game_info)
        self.next = 'main_menu'
        self.setup_background()

    def setup_background(self):
        self.background = setup.graphics['level_1']  # Surface
        # print(self.background)
        self.background_rect = self.background.get_rect()  # return a class of picture pixel info
        # print(self.background_rect)
        self.background = pygame.transform.scale(self.background,
                                                 (int(self.background_rect.width * consts.BG_MULTI_TIMES),
                                                  int(self.background_rect.height * consts.BG_MULTI_TIMES)))
        self.viewerside = setup.screen.get_rect()
        self.title = tools.get_image(setup.graphics['title_screen'], 1, 60, 176, 88, (255, 0, 22),
                                     consts.BG_MULTI_TIMES)

    def update(self, surface: pygame.Surface, keys, current_time, mouse, mouse_xy):
        if not pygame.mixer.music.get_busy():
            self.sound.music('main_theme', 0.5)
        self.current_time = current_time
        self.game_info['current_time'] = self.current_time
        # stationary form
        surface.blit(self.background, self.viewerside)
        self.info.update(self.game_info)
        self.info.draw(surface, keys)
        if keys[pygame.K_w]:
            self.sound.stop_music()
            self.finished = True
            self.reset_info()

    def reset_info(self):
        temp = self.game_info['top_score']
        self.game_info = {
            'score': 0,
            'top_score': temp,
            'coin': 0,
            'lives': 1,
            'player_state': 'small',
            'states': 'main_menu',
            'current_time': 0,
            'time': 401
        }
