import pygame
from .. import tools, setup, consts, sound


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y, game_info, name='coin'):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.game_info = game_info
        self.x = x
        self.y = y
        self.frame_rects = [
            (0, 112, 16, 16),
            (16, 112, 16, 16),
            (32, 112, 16, 16),
            (48, 112, 16, 16)
        ]
        self.frames = []  # 存帧
        for frame_rect in self.frame_rects:
            self.frames.append(
                tools.get_image(setup.graphics['item_objects'], frame_rect[0], frame_rect[1], frame_rect[2],
                                frame_rect[3], (0, 0, 0), consts.BG_MULTI_TIMES))

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.g = consts.GRAVITY - 0.7
        self.state = 'rest'
        self.timer = 0
        self.sound = sound.Sound()

    def update(self, level):
        self.current_time = pygame.time.get_ticks()
        self.handle_state()  # 状态机

    def handle_state(self):  # level
        if self.state == 'rest':
            self.rest()
        elif self.state == 'up':
            self.up()  # level

    def rest(self):
        frame_durations = [375, 125, 125, 75]
        if self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index += 1
            self.frame_index %= 4
            self.timer = self.current_time
        self.image = self.frames[self.frame_index]

    def trigger_up(self):
        self.y_vel = -8
        self.state = 'up'
        self.sound.sound('coin')
        self.game_info['coin'] += 1

    def up(self):  # 更新坐标
        self.rect.y += self.y_vel
        self.y_vel += self.g
        self.frame_index = 3
        self.image = self.frames[self.frame_index]
        if self.rect.y > self.y:
            self.rect.y = self.y
            self.y_vel = 0
            self.kill()


class FlashingCoin(pygame.sprite.Sprite):  # using pygame class Sprite to simplify class FlashingCoin, a subclass.
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []  # storing image(Surface) that shines
        self.frame_index = 0  # 4 stages
        frame_rects = [
            (1, 160, 5, 8),
            (9, 160, 5, 8),
            (17, 160, 5, 8),
            (9, 160, 5, 8)
        ]  # loop to dynamic
        self.load_frames(frame_rects)

        # subclass needs
        self.image = self.frames[self.frame_index]  # the very frame
        self.rect = self.image.get_rect()
        self.rect.x = 280
        self.rect.y = 64  # location
        self.timer = 0  # flashing image

    def load_frames(self, frame_rects):
        sheet = setup.graphics['item_objects']
        for rect in frame_rects:
            self.frames.append(
                tools.get_image(sheet, rect[0], rect[1], rect[2], rect[3], (0, 0, 0), consts.BG_MULTI_TIMES))

    def update(self):
        self.current_time = pygame.time.get_ticks()
        frame_durations = [375, 125, 125, 125]
        # updating frame by durations
        if self.timer == 0:
            self.timer = self.current_time
        elif self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index += 1
            self.frame_index %= 4
            self.timer = self.current_time

        self.image = self.frames[self.frame_index]


class TonyDance(FlashingCoin):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []  # storing image(Surface) that shines
        self.frame_index = 0  # 4 stages
        self.frame_rect = (0, 0, 39, 53)
        for i in range(1, 9):
            self.frames.append(
                tools.get_image(setup.graphics['snap{}'.format(i)], self.frame_rect[0], self.frame_rect[1],
                                self.frame_rect[2],
                                self.frame_rect[3], (0, 0, 0), consts.BG_MULTI_TIMES))
        # subclass needs
        self.image = self.frames[self.frame_index]  # the very frame
        self.rect = self.image.get_rect()
        self.rect.x = 150
        self.rect.y = 397  # location
        self.timer = 0  # flashing image

    def update(self):
        self.current_time = pygame.time.get_ticks()
        frame_durations = [125, 125, 125, 125, 125, 125, 125, 125]
        # updating frame by durations
        if self.timer == 0:
            self.timer = self.current_time
        elif self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index += 1
            self.frame_index %= 8
            self.timer = self.current_time

        self.image = self.frames[self.frame_index]


class FlashingText(pygame.sprite.Sprite):
    def __init__(self, centerx, centery, text, angle, color=None):
        pygame.sprite.Sprite.__init__(self)
        self.Cx, self.Cy = centerx, centery
        self.name = 'text_info'
        font = pygame.font.Font(consts.FONT, 40)  # 调用系统字体
        self.label_image = []
        label_image = pygame.transform.rotate(font.render(text, 0, (34, 177, 76)), angle)
        self.label_image.append(label_image)
        label_image = pygame.transform.rotate(font.render(text, 0, (255, 242, 0)), angle)
        self.label_image.append(label_image)
        label_image = pygame.transform.rotate(font.render(text, 0, (255, 103, 205)), angle)
        self.label_image.append(label_image)
        # mosaic process
        self.const_image = self.label_image[0]
        self.Crect = self.const_image.get_rect()
        self.image = self.const_image
        self.state = 'zoom'
        self.timer = 0
        self.color_timer = 0
        self.color_index = 0
        self.zooming = [1, 1.02, 1.04, 1.06, 1.08, 1.1, 1.12, 1.14, 1.16, 1.18, 1.2, 1.22, 1.24, 1.26, 1.28, 1.3, 1.32,
                        1.34, 1.36, 1.38, 1.4, 1.42, 1.44, 1.46, 1.48, 1.5, 1.52, 1.54, 1.56, 1.58, 1.6, 1.62, 1.64,
                        1.66,
                        1.68, 1.7, 1.72, 1.74, 1.76, 1.78, 1.8]
        reverse = list(reversed(self.zooming))
        self.zooming = self.zooming + reverse
        self.zooming_index = 0

    def update(self, *args):
        self.rect = self.image.get_rect()
        self.rect.centerx = self.Cx
        self.rect.centery = self.Cy

        self.current_time = pygame.time.get_ticks()
        if self.state == 'zoom':
            if self.timer == 0:
                self.timer = self.current_time
            if self.current_time - self.timer > 10:
                self.image = pygame.transform.scale(self.const_image,
                                                    (int(self.Crect.width * self.zooming[self.zooming_index]),
                                                     int(self.Crect.height * self.zooming[self.zooming_index])))
                self.zooming_index += 1
                self.zooming_index %= 79
                self.timer = self.current_time

            if self.color_timer == 0:
                self.color_timer = self.current_time
            if self.current_time - self.color_timer > 1000:
                self.const_image = self.label_image[self.color_index]
                self.color_index += 1
                self.color_index %= 3
                self.color_timer = self.current_time
