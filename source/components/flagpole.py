import pygame
from .. import setup, tools, consts


class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y, player_y_vel):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []
        self.frame_index = 0
        frame_rects = [(128, 32, 16, 16)]
        for frame_rect in frame_rects:
            self.frames.append(
                tools.get_image(setup.graphics['item_objects'], frame_rect[0], frame_rect[1], frame_rect[2],
                                frame_rect[3], (0, 0, 0), consts.BG_MULTI_TIMES))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.y_vel = player_y_vel
        self.down = False

    def drop_down(self, level):
        self.rect.y += self.y_vel
        collide = pygame.sprite.spritecollideany(self, level.ground_items_group)
        if collide:
            self.y_vel = 0
            self.down = False

    def update(self, level):
        if self.down:
            self.drop_down(level)


class Pole(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []
        self.frame_index = 0
        frame_rects = [(263, 144, 2, 16)]
        for frame_rect in frame_rects:
            self.frames.append(
                tools.get_image(setup.graphics['tile_set'], frame_rect[0], frame_rect[1], frame_rect[2], frame_rect[3],
                                (0, 0, 0), consts.BG_MULTI_TIMES))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []
        self.frame_index = 0
        frame_rects = [(228, 120, 8, 8)]
        for frame_rect in frame_rects:
            self.frames.append(
                tools.get_image(setup.graphics['tile_set'], frame_rect[0], frame_rect[1], frame_rect[2], frame_rect[3],
                                (0, 0, 0), consts.BG_MULTI_TIMES))
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
