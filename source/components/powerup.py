import pygame
from .. import setup, tools, consts,sound


def create_powerup(centerx, centery, type, flag):
    # based on player's state
    if flag == 0:
        return Mushroom(centerx, centery)
    elif flag == 1:
        return Fireflower(centerx, centery)
    elif flag == 2:
        return LifeMushroom(centerx, centery)
    elif flag == 3:
        return Star(centerx, centery)


class Powerup(pygame.sprite.Sprite):
    def __init__(self, centerx, centery, frame_rects):
        pygame.sprite.Sprite.__init__(self)

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
        self.direct = 1  # right
        self.y_vel = -1
        self.g = 1
        self.max_y_vel = 8

    def update_pos(self, level):
        self.rect.x += self.x_vel
        self.check_xcollision(level)
        self.rect.y += self.y_vel
        self.check_ycollision(level)

        if self.rect.x < 0 or self.rect.y > consts.SCREEN_HEIGHT:
            self.kill()

    def check_xcollision(self, level):
        collide = pygame.sprite.spritecollideany(self, level.ground_items_group)  # 碰到了
        if collide:  # 准备反弹
            if self.direct == 0:
                self.direct = 1
                self.rect.left = collide.rect.right
            else:
                self.direct = 0
                self.rect.right = collide.rect.left
            self.x_vel *= -1

    def check_ycollision(self, level):  # bug?
        checkGroup = pygame.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
        collide = pygame.sprite.spritecollideany(self, checkGroup)
        if collide:
            if self.rect.top < collide.rect.top:  # 从上往下掉
                self.rect.bottom = collide.rect.top
                self.y_vel = 0
                self.state = 'walk'
        level.check_fall(self)


class Mushroom(Powerup):
    def __init__(self, centerx, centery):
        Powerup.__init__(self, centerx, centery, [(0, 0, 16, 16)])
        self.x_vel = 2
        self.state = 'grow'
        self.name = 'mushroom'

    def update(self, level):
        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.ori_y:
                self.state = 'walk'
        elif self.state == 'walk':
            pass
        elif self.state == 'fall':
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.g

        if self.state != 'grow':
            self.update_pos(level)


class Fireflower(Powerup):
    def __init__(self, centerx, centery):
        frame_rects = [(0, 32, 16, 16), (16, 32, 16, 16), (32, 32, 16, 16), (48, 32, 16, 16)]
        Powerup.__init__(self, centerx, centery, frame_rects)
        self.x_vel = 2
        self.state = 'grow'
        self.name = 'fireflower'
        self.timer = 0

    def update(self, level):
        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.ori_y:
                self.state = 'rest'

        self.current_time = pygame.time.get_ticks()

        if self.timer == 0:
            self.timer = self.current_time
        if self.current_time - self.timer > 30:
            self.frame_index += 1
            self.frame_index %= 4
            self.timer = self.current_time
            self.image = self.frames[self.frame_index]


class Fireball(Powerup):
    def __init__(self, centerx, centery, direction, game_info):
        # self.game_info=game_info
        frame_rects = [(96, 144, 8, 8), (104, 144, 8, 7), (96, 152, 8, 8), (104, 152, 8, 8),  # 旋转
                       (112, 144, 16, 16), (112, 160, 16, 16), (112, 176, 16, 16)]  # 爆炸
        Powerup.__init__(self, centerx, centery, frame_rects)
        self.name = 'fireball'
        self.state = 'fly'
        self.direction = direction
        self.x_vel = 8 if self.direction else -8
        self.y_vel = 8
        self.gravity = 1
        self.timer = 0
        self.game_info = game_info
        self.sound=sound.Sound()

    def update(self, level):
        self.current_time = pygame.time.get_ticks()
        if self.state == 'fly':
            self.y_vel += self.gravity
            if self.current_time - self.timer > 200:
                self.frame_index += 1
                self.frame_index %= 4
                self.timer = self.current_time
                self.image = self.frames[self.frame_index]  # 旋转子弹
            self.update_pos(level)
        elif self.state == 'boom':
            if self.current_time - self.timer > 50:
                if self.frame_index < 6:
                    self.frame_index += 1
                    self.timer = self.current_time
                    self.image = self.frames[self.frame_index]  # 爆炸特效
                else:
                    self.kill()

    def update_pos(self, level):
        self.rect.x += self.x_vel
        self.check_xcollision(level)
        self.rect.y += self.y_vel
        self.check_ycollision(level)

        if self.rect.x < 0 or self.rect.y > consts.SCREEN_HEIGHT:
            self.kill()

    def check_xcollision(self, level):
        collide = pygame.sprite.spritecollideany(self, level.ground_items_group)  # 碰到了
        if collide:  # 准备反弹
            self.frame_index = 4  # 爆炸
            self.state = 'boom'
        enemy = pygame.sprite.spritecollideany(self, level.enemy_group_cp)
        if enemy:
            if enemy.name=='glass':
                self.sound.sound('amagi',3)
            enemy.rotate_kill()
            level.text_info_group.add(Textinfo(enemy.rect.centerx, enemy.rect.centery, '+50'))
            self.game_info['score'] += 50
            self.frames_index = 4
            self.state = 'boom'

    def check_ycollision(self, level):  # bug?
        checkGroup = pygame.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
        collide = pygame.sprite.spritecollideany(self, checkGroup)
        if collide:
            if self.rect.top < collide.rect.top:  # 从上往下掉
                self.rect.bottom = collide.rect.top
                self.y_vel = -10


class LifeMushroom(Powerup):
    def __init__(self, centerx, centery):
        Powerup.__init__(self, centerx, centery, [(0, 0, 44, 92)])
        frame_rects = [(0, 0, 44, 92)]
        self.frames = []
        self.frame_index = 0
        for frame_rect in frame_rects:
            self.frames.append(
                tools.get_image(setup.graphics['smoke'], frame_rect[0], frame_rect[1], frame_rect[2],
                                frame_rect[3], (0, 0, 0), 0.8))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx
        self.rect.centery = centery-20
        self.ori_y = centery - self.rect.height / 2

        self.x_vel = 0
        self.state = 'grow'
        self.name = 'lifemushroom'

    def update(self, level):  # 目的是在自己的更新方法中完成对物体的碰撞检测
        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.ori_y-20:
                self.state = 'walk'

        elif self.state == 'walk':
            pass
        elif self.state == 'fall':
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.g

        if self.state != 'grow':
            self.update_pos(level)


class Star(Powerup):
    def __init__(self, centerx, centery):
        Powerup.__init__(self, centerx, centery, [(0, 48, 16, 16), (16, 48, 16, 16), (32, 48, 16, 16), (0, 48, 16, 16)])
        self.state = 'walk'
        self.x_vel = 2
        self.y_vel = 0
        self.gravity = 1
        self.name = 'star'
        self.timer = 0

    def update(self, level):  # 目的是在自己的更新方法中完成对物体的碰撞检测
        self.current_time = pygame.time.get_ticks()
        if self.state == 'walk':
            self.y_vel += self.gravity
            if self.current_time - self.timer > 200:
                self.frame_index += 1
                self.frame_index %= 4
                self.timer = self.current_time
                self.image = self.frames[self.frame_index]
            if self.y_vel > 0:
                self.y_vel = -5
            self.update_position(level)
        elif self.state == 'fall':
            if self.y_vel < self.max_y_vel:
                self.y_vel += self.gravity
            self.update_position(level)

    def update_position(self, level):
        self.rect.x += self.x_vel
        self.check_xcollision(level)  # x方向碰撞检测
        self.rect.y += self.y_vel
        self.check_ycollision(level)  # y方向碰撞检测
        if self.rect.x < 0 or self.rect.y > consts.SCREEN_HEIGHT:
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
