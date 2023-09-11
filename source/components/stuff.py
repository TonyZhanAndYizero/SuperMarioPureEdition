import pygame
from .. import consts


class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((width, height)).convert()  # vanished veil to make collision detection
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.name = name


class Checkpoint(Item):
    def __init__(self, x, y, width, height, cp_type, name='checkpoint', enemyGroupId=None):
        Item.__init__(self, x, y, width, height, name)
        self.cp_type = cp_type
        self.enemyGroupId = enemyGroupId


class PureText(pygame.sprite.Sprite):
    def __init__(self, centerx, centery, text, color=0,scalex=2.2,scaley=1.8):
        pygame.sprite.Sprite.__init__(self)
        self.name = 'text_info'
        font = pygame.font.Font(consts.FONT, 40)  # 调用系统字体
        if color == 0:
            label_image = font.render(text, 1, (255, 255, 255))  # 把文字渲染成图片
        elif color == 1:
            label_image = font.render(text, 1, (255, 0, 0))  # 把文字渲染成图片
        # mosaic process
        rect = label_image.get_rect()

        label_image = pygame.transform.scale(label_image, (int(rect.width * scalex),
                                                           int(rect.height * scaley)))
        self.image = label_image
        self.rect = self.image.get_rect()
        self.rect.centerx = centerx + 15
        self.rect.centery = centery
        self.ori_y = centery - self.rect.height / 2
        self.x_vel = 0
        self.y_vel = -5
        self.g = 1
        self.state = 'grow'

    def update(self, *args):
        if self.state == 'grow':
            self.rect.y += self.y_vel
            if self.rect.bottom < self.ori_y - 110:
                self.state = 'stop'
        elif self.state == 'stop':
            self.y_vel = 0
