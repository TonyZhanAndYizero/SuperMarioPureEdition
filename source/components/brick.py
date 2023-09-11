import pygame
from .. import tools, setup, consts, sound
from .powerup import create_powerup
from .box import Textinfo


class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, brick_type, group, color=None, name='brick'):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.brick_type = brick_type
        self.name = name
        self.group = group
        bright = [(16, 0, 16, 16), (48, 0, 16, 16)]
        dark = [(16, 32, 16, 16), (48, 32, 16, 16)]

        if not color:
            self.frame_rects = bright
        else:
            self.frame_rects = dark

        self.frames = []  # 存帧
        for frame_rect in self.frame_rects:
            self.frames.append(
                tools.get_image(setup.graphics['tile_set'], frame_rect[0], frame_rect[1], frame_rect[2], frame_rect[3],
                                (0, 0, 0), consts.BG_MULTI_TIMES + 0.01))

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.state = 'rest'
        self.g = consts.GRAVITY - 0.3
        self.timer = 0
        self.sound = sound.Sound()

    def update(self, level):
        self.current_time = pygame.time.get_ticks()
        self.handle_state(level)  # 状态机

    def handle_state(self, level):
        if self.state == 'rest':
            self.rest()
        elif self.state == 'up':
            self.up(level)
        elif self.state == 'open':
            self.open()

    def rest(self):
        pass

    def trigger_up(self):
        self.y_vel = -8
        self.state = 'up'
        self.sound.sound('bump')

    def up(self, level):  # 更新坐标
        self.rect.y += self.y_vel
        self.y_vel += self.g

        if self.rect.y > self.y:
            self.y_vel = 0
            self.rect.y = self.y
            if self.brick_type == 0:
                self.state = 'rest'
            elif self.brick_type == 1:
                level.text_info_group.add(Textinfo(self.rect.x, self.rect.y, '+ 100'))
                level.game_info['score'] += 100
                level.game_info['coin'] += 1
                self.sound.sound('coin')
                self.group.add(Createcoin(self.rect.centerx, self.rect.centery))
                self.state = 'open'
            elif self.brick_type == 6:
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.brick_type, 2))
                self.state = 'open'
            else:
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.brick_type, 3))
                self.state = 'open'

    def open(self):
        self.frame_index = 1
        self.image = self.frames[self.frame_index]

    def smashed(self, group):
        self.sound.sound('brick_smash')
        # x,y,x_v,y_v
        fragments = [
            (self.rect.x, self.rect.y, -2, -10),
            (self.rect.x, self.rect.y, 2, -10),
            (self.rect.x, self.rect.y, -2, -5),
            (self.rect.x, self.rect.y, 2, -5)
        ]
        for fragment in fragments:
            group.add(Fragment(*fragment))
        self.kill()


class Fragment(pygame.sprite.Sprite):
    def __init__(self, x, y, x_vel, y_vel):
        pygame.sprite.Sprite.__init__(self)
        self.image = tools.get_image(setup.graphics['tile_set'], 68, 20, 8, 8, (0, 0, 0), consts.BG_MULTI_TIMES + 0.01)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.x_vel, self.y_vel = x_vel, y_vel
        self.g = consts.GRAVITY

    def update(self, *args):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.g
        if self.rect.y > consts.SCREEN_HEIGHT:
            self.kill()


class Createcoin(pygame.sprite.Sprite):
    def __init__(self, centerx, centery):
        pygame.sprite.Sprite.__init__(self)
        self.name = 'coin'
        frame_rects = [(0, 112, 16, 16), (16, 112, 16, 16), (32, 112, 16, 16), (48, 112, 16, 16)]
        self.frames = []
        self.frame_index = 0
        for frame_rect in frame_rects:
            self.frames.append(
                tools.get_image(setup.graphics['item_objects'], frame_rect[0], frame_rect[1], frame_rect[2],
                                frame_rect[3], (0, 0, 0), 2.5))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = centery
        self.ori_y = centery - self.rect.height / 2
        self.x_vel = 0
        self.y_vel = -6
        self.g = 0.25
        self.max_y_vel = 6
        self.state = 'grow'

        self.timer = 0  # 计时器

    def check_y_collisions(self, level):
        level.check_fall(self)

    def update(self, level):
        self.current_time = pygame.time.get_ticks()
        if self.timer == 0:
            self.timer = self.current_time
        elif self.current_time - self.timer > 200:
            self.frame_index += 1
            self.frame_index %= 4
            self.timer = self.current_time
        self.image = self.frames[self.frame_index]

        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.ori_y:
                self.state = 'fall'

        elif self.state == 'fall':
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.g

        self.rect.y += self.y_vel
        self.check_y_collisions(level)  # y方向碰撞检测
        if self.rect.y > self.ori_y:
            self.kill()
