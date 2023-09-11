import pygame
from .. import setup, tools, consts, sound
from .box import Textinfo
import random


def create_enemy(enemy_data):
    enemy_type = enemy_data['type']
    x, bottom, direct, color = enemy_data['x'], enemy_data['y'], enemy_data['direction'], enemy_data['color']
    if enemy_type == 0:  # 蘑菇
        enemy = Mushroom(x, bottom, direct, 'mushroom', color)
    elif enemy_type == 1:  # 乌龟
        enemy = Turtle(x, bottom, direct, 'turtle', color)
    elif enemy_type == 3:  # 眼睛
        # print('99')
        enemy = Glass(x, bottom, direct, 'glass', color)
    return enemy


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, bottom, direct, name, frame_rects):
        pygame.sprite.Sprite.__init__(self)
        self.direct = direct
        self.name = name  # 基本名字，方向
        self.sound = sound.Sound()
        self.left_frames = []
        self.right_frames = []
        self.load_frames(frame_rects)  # 基本形状

        self.frame_index = 0
        if self.direct == 0:
            self.frames = self.left_frames
        else:
            self.frames = self.right_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = bottom  # 基本方位和形状
        self.timer = 0  # 计时器，令其变化
        self.Once = 0
        if self.direct == 0:
            self.x_vel = -consts.ENEMY_SPEED
        else:
            self.x_vel = consts.ENEMY_SPEED
        self.y_vel = 0
        self.g = consts.GRAVITY
        self.state = 'walk'  # 怪物的速度，状态=行走

    def load_frames(self, frame_rects):
        for frame_rect in frame_rects:
            left_frame = tools.get_image(setup.graphics['enemies'], *frame_rect, (0, 0, 0), 2.5)
            right_frame = pygame.transform.flip(left_frame, True, False)
            self.left_frames.append(left_frame)
            self.right_frames.append(right_frame)

    def update(self, level):
        self.current_time = pygame.time.get_ticks()
        # 状态机判断当前状态，类似player处理
        self.process_state(level)  # such as walk and etc.
        self.update_pos(level)  # 走路之后 更改位置

    def process_state(self, level):
        if self.state == 'rotate':
            self.rotate()
        else:
            if self.state == 'walk':
                self.walk()
            elif self.state == 'fall':
                self.fall()
            elif self.state == 'die':
                self.die(level)
            elif self.state == 'down':  # 被踩
                self.down(level)
            elif self.state == 'slide':
                self.slide()
            if self.direct:
                self.image = self.right_frames[self.frame_index]
            else:
                self.image = self.left_frames[self.frame_index]

    def walk(self):
        if self.current_time - self.timer > 100:
            self.frame_index += 1
            self.frame_index %= 2
            self.timer = self.current_time
            self.image = self.frames[self.frame_index]

    def fall(self):
        if self.y_vel < 10:
            self.y_vel += self.g

    def die(self,level):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.g
        if self.rect.y > consts.SCREEN_HEIGHT or pygame.sprite.spritecollideany(self,level.ground_items_group):
            self.kill()

    def rotate_kill(self):
        self.state = 'rotate'
        self.x_vel = 0
        self.y_vel = 0
        self.deathTimer = self.current_time

    def rotate(self):
        if (self.current_time - self.deathTimer) > 20:
            self.Once += 1
            self.deathTimer = self.current_time
            self.image = pygame.transform.rotate(self.image, 9)
        if self.Once == 9:
            self.kill()

    def update_pos(self, level):
        self.rect.x += self.x_vel
        self.check_xcollision(level)
        self.rect.y += self.y_vel
        if self.state != 'die':
            choice = random.randint(0, 3)
            if choice == 1 or self.state == 'fall' or self.state == 'slide':  # 1/3概率掉下去,且如果掉落不出现bug
                self.check_ycollision(level)
                level.check_fall(self)
            else:
                self.check_fall(level)

    def check_xcollision(self, level):
        check_group=pygame.sprite.Group(level.ground_items_group,level.brick_group,level.box_group)
        collide = pygame.sprite.spritecollideany(self, check_group)  # 碰到了
        if collide:  # 准备反弹
            if self.direct == 0:
                self.direct = 1
                self.rect.left = collide.rect.right
            else:
                self.direct = 0
                self.rect.right = collide.rect.left
            self.x_vel *= -1

        if self.state == 'slide':
            enemy = pygame.sprite.spritecollideany(self, level.enemy_group_cp)
            if enemy:
                level.game_info['score'] += 50
                level.text_info_group.add(Textinfo(enemy.rect.centerx, enemy.rect.centery, '+ 50'))
                enemy.trigger_die(how='slide', direct=self.direct)
                level.enemy_group_cp.remove(enemy)
                level.dead_group.add(enemy)

    def check_ycollision(self, level):  # bug?
        checkGroup = pygame.sprite.Group(level.ground_items_group, level.box_group, level.brick_group)
        collide = pygame.sprite.spritecollideany(self, checkGroup)
        if collide:
            if self.rect.top < collide.rect.top:  # 从上往下掉
                self.rect.bottom = collide.rect.top
                self.y_vel = 0
                self.state = 'walk'

    def check_fall(self, level):  # 多玩法
        self.rect.y += 1  # 测试
        check_group = pygame.sprite.Group(level.ground_items_group, level.brick_group, level.box_group)
        collide = pygame.sprite.spritecollideany(self, check_group)
        if not collide:
            if self.direct == 0:
                self.direct = 1
            else:
                self.direct = 0
            self.x_vel *= -1
        self.rect.y -= 1  # 还原

    def trigger_die(self, how, direct=1):
        self.deathTimer = self.current_time
        if how == 'up' or how == 'slide':
            self.x_vel = consts.ENEMY_SPEED * direct
            self.y_vel = -8  # 向上飞
            self.g = 0.5
            self.state = 'die'
            self.frame_index = 2
        elif how == 'down':
            self.state = 'down'
        if self.name == 'glass':
            self.sound.sound('amagi',3)


class Mushroom(Enemy):
    def __init__(self, x, y, direct, name, color):
        bright = [(0, 16, 16, 16), (16, 16, 16, 16), (32, 16, 16, 16)]
        dark = [(0, 48, 16, 16), (16, 48, 16, 16), (32, 48, 16, 16)]
        if not color:
            frame_rects = bright
        else:
            frame_rects = dark
        Enemy.__init__(self, x, y, direct, name, frame_rects)

    def down(self, level):
        self.x_vel = 0  # 停下来
        self.frame_index = 2
        if self.deathTimer == 0:
            self.deathTimer = self.current_time
        if self.current_time - self.deathTimer > 500:
            self.kill()


class Glass(Enemy):
    def __init__(self, x, y, direct, name, color):
        bright = [(48, 16, 16, 16), (64, 16, 16, 16), (80, 16, 16, 16)]
        dark = [(48, 48, 16, 16), (64, 48, 16, 16), (80, 48, 16, 16)]
        if not color:
            frame_rects = bright
        else:
            frame_rects = dark
        Enemy.__init__(self, x, y, direct, name, frame_rects)

    def down(self, level):
        self.x_vel = 0  # 停下来
        self.frame_index = 2
        if self.deathTimer == 0:
            self.deathTimer = self.current_time
        if self.current_time - self.deathTimer > 500:
            self.kill()


class Turtle(Enemy):
    def __init__(self, x, y, direct, name, color):
        bright = [(96, 9, 16, 22), (112, 9, 16, 22), (160, 9, 16, 22)]
        dark = [(96, 72, 16, 22), (112, 72, 16, 22), (160, 72, 16, 22)]
        if not color:
            frame_rects = bright
        else:
            frame_rects = dark
        Enemy.__init__(self, x, y, direct, name, frame_rects)
        # 龟壳钻出
        self.shell_timer = 0

    def down(self, level):  # in case the turtle double_hurted
        self.x_vel = 0
        self.frame_index = 2

        if self.shell_timer == 0:
            self.shell_timer = self.current_time
        if self.current_time - self.shell_timer > 5000:
            self.state = 'walk'
            if self.direct == 0:
                self.x_vel = -consts.ENEMY_SPEED
            else:
                self.x_vel = consts.ENEMY_SPEED
            self.shell_timer = 0  # my update to cater new time
            level.enemy_group_cp.add(self)
            level.shell_group.remove(self)

    def slide(self):
        pass
