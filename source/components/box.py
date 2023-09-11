# same as brick
import pygame
from .. import tools, setup, consts, sound
from .powerup import create_powerup


class Box(pygame.sprite.Sprite):
    def __init__(self, x, y, box_type, group, game_info, color=None, name='box'):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.game_info = game_info
        self.x = x
        self.y = y
        self.box_type = box_type
        self.group = group  # 箱子不同类型的奖品
        self.frame_rects = []

        bright = [
            (384, 0, 16, 16),
            (400, 0, 16, 16),
            (416, 0, 16, 16),
            (432, 0, 16, 16)
        ]
        dark = [
            (384, 32, 16, 16),
            (400, 32, 16, 16),
            (416, 32, 16, 16),
            (432, 32, 16, 16)
        ]

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
        self.g = consts.GRAVITY - 0.3
        self.state = 'rest'
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
        frame_durations = [375, 125, 125, 75]
        if self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index += 1
            self.frame_index %= 4
            self.timer = self.current_time
        self.image = self.frames[self.frame_index]

    def trigger_up(self):
        self.y_vel = -8
        self.state = 'up'

    def up(self, level):  # 更新坐标
        self.rect.y += self.y_vel
        self.y_vel += self.g
        self.frame_index = 3
        self.image = self.frames[self.frame_index]

        if self.rect.y > self.y:
            self.rect.y = self.y
            self.y_vel = 0
            self.state = 'open'

            # type 0,1,2,3->空,金币,星星,蘑菇
            if self.box_type == 1:
                self.sound.sound('coin')
                self.group.add(Createcoin(self.rect.centerx, self.rect.centery))
                self.group.add(Textinfo(self.rect.centerx, self.rect.centery, '+ 200'))
                self.game_info['score'] += 200
                self.game_info['coin'] += 1
            elif self.box_type == 3:
                if level.player.big:
                    self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.box_type, 1))
                else:
                    self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.box_type, 0))
            elif self.box_type == 5:
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.box_type, 2))
            else :
                self.group.add(create_powerup(self.rect.centerx, self.rect.centery, self.box_type, 3))

    def open(self):
        pass


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
        self.y_vel = -5
        self.g = 0.2
        self.max_y_vel = 5
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


class Textinfo(pygame.sprite.Sprite):
    def __init__(self, centerx, centery, text):
        pygame.sprite.Sprite.__init__(self)
        self.name = 'text_info'
        font = pygame.font.Font(consts.FONT, 40)  # 调用系统字体
        label_image = font.render(text, 1, (255, 255, 255))  # 把文字渲染成图片
        # mosaic process
        rect = label_image.get_rect()
        label_image = pygame.transform.scale(label_image, (int(rect.width * 1.5),
                                                           int(rect.height * 1.5)))

        self.image = label_image
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx + 15
        self.rect.centery = centery
        self.ori_y = centery - self.rect.height / 2
        self.x_vel = 0
        self.y_vel = -5
        self.g = 0.3
        self.max_y_vel = 8
        self.state = 'grow'

    def update_pos(self, level):
        self.rect.y += self.y_vel
        self.check_ycollisions(level)  # y方向碰撞检测
        if self.rect.y > self.rect.bottom:
            self.kill()

    def check_ycollisions(self, level):
        level.check_fall(self)

    def update(self, level):
        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.ori_y - 200:
                self.state = 'fall'
        elif self.state == 'fall':
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.g

        self.rect.y += self.y_vel
        self.check_ycollisions(level)  # y方向碰撞检测
        if self.rect.y > self.ori_y:
            self.kill()


class Princess(pygame.sprite.Sprite):
    def __init__(self, x, y, game_info, name='princess'):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.game_info = game_info
        self.x = x
        self.y = y
        self.frames = []  # 存帧
        self.frame_rect = (0, 0, 39, 53)
        for i in range(1, 9):
            self.frames.append(
                tools.get_image(setup.graphics['balancing{}'.format(i)], self.frame_rect[0], self.frame_rect[1],
                                self.frame_rect[2],
                                self.frame_rect[3], (0, 0, 0), consts.BG_MULTI_TIMES-0.5))

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.state = 'rest'
        self.timer = 0
        self.sound = sound.Sound()

    def update(self, level):
        self.current_time = pygame.time.get_ticks()
        self.handle_state(level)  # 状态机

    def handle_state(self, level):
        if self.state == 'rest':
            self.rest()
        elif self.state == 'up':
            self.up()

    def rest(self):
        frame_durations = [125, 125, 125, 125, 125, 125, 125, 125]
        if self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index += 1
            self.frame_index %= 8
            self.timer = self.current_time
        self.image = self.frames[self.frame_index]

    def trigger_up(self):
        self.state = 'up'
        self.frame_index = 0
        self.frames.clear()
        for i in range(1, 9):
            self.frames.append(
                tools.get_image(setup.graphics['skip{}'.format(i)], self.frame_rect[0], self.frame_rect[1],
                                self.frame_rect[2],
                                self.frame_rect[3], (0, 0, 0), consts.BG_MULTI_TIMES-0.5))

    def up(self):
        frame_durations = [100, 100, 100, 100, 100, 100, 100, 100]
        if self.current_time - self.timer > frame_durations[self.frame_index]:
            self.frame_index += 1
            self.frame_index %= 8
            self.timer = self.current_time
        self.image = self.frames[self.frame_index]
