import pygame
from .. import consts
from ..components import coin
from .. import setup, tools

pygame.font.init()


class Info:
    def __init__(self, state, game_info):
        self.state = state  # the infos needed to store in different states
        self.game_info = game_info
        self.coin = game_info['coin']
        self.lives = game_info['lives']
        self.top_score = game_info['top_score']
        self.score = game_info['score']
        self.lives_labels = []
        self.create_state_labels()  # create peculiar words in certain state
        self.create_info_labels()  # general info(score,time...) labels
        self.create_score_group(self.score)
        self.create_coin_counter(self.coin)
        self.flash_coin = coin.FlashingCoin()
        self.flash_text = coin.FlashingText(520, 150, 'DINGZHEN 1.0', 345, 1)

        self.TONYDANCE = coin.TonyDance()
        self.idx = 0
        self.click = True
        self.time = self.game_info['time']  # 倒计时400
        self.timer = 0  # 计时器
        self.current_time = 0
        self.lives = game_info['lives']

        self.time_labels = []
        self.create_countdown()
        self.TOBE_done = []

    def create_countdown(self):
        # create last time
        if self.game_info['states'] in ['load_screen', 'load_level2', 'load_level3', 'load_level4', 'game_over']:
            self.time_labels.append((self.create_label('LOAD'), (625, 55)))
        elif self.time == 401:
            self.time_labels.append((self.create_label('400'), (635, 55)))

        if self.game_info['states'] in ['level', 'level2', 'level3', 'level4']:
            # Creates the count down clock for the level
            self.current_time = pygame.time.get_ticks()  # 获取当前时间
            if self.current_time - self.timer > 1000:
                if self.time > 0:
                    self.time -= 1
                self.timer = self.current_time
                self.time_labels.clear()
                self.time_labels.append((self.create_label('{0}'.format(self.time)), (635, 55)))
                self.game_info['time'] = self.time

    def create_coin_counter(self, coin):
        self.coin_labels = []
        # Creates the info that tracks the number of coins Mario collects
        if coin == 0:
            self.coin_labels.append((self.create_label('X00'), (300, 55)))
        elif coin < 10:
            self.coin_labels.append((self.create_label('X0{0}'.format(coin)), (300, 55)))
        else:
            self.coin_labels.append((self.create_label('X{0}'.format(coin)), (300, 55)))

    def create_score_group(self, score):
        self.update_labels = []
        if score == 0:
            self.update_labels.append((self.create_label('000000'), (75, 55)))
        elif score < 1000:
            self.update_labels.append((self.create_label('000{0}'.format(score)), (75, 55)))
        elif score < 10000:
            self.update_labels.append((self.create_label('00{0}'.format(score)), (75, 55)))
        elif score < 100000:
            self.update_labels.append((self.create_label('0{0}'.format(score)), (75, 55)))
        else:
            self.update_labels.append((self.create_label('{0}'.format(score)), (75, 55)))

    def create_state_labels(self):
        self.state_labels = []
        if self.state == 'main_menu':
            self.state_labels.append((self.create_label('1 PLAYER GAME'), (272, 360)))
            self.state_labels.append((self.create_label('2 PLAYERS GAME(TO BE DONE)'), (120, 405)))
            self.state_labels.append((self.create_label('TOP-'), (300, 465)))
            if self.game_info['top_score'] == 0:
                self.state_labels.append((self.create_label('000000'), (400, 465)))
            elif self.game_info['top_score'] < 1000:
                self.state_labels.append((self.create_label('000{0}'.format(self.game_info['top_score'])), (400, 465)))
            elif self.game_info['top_score'] < 10000:
                self.state_labels.append((self.create_label('00{0}'.format(self.game_info['top_score'])), (400, 465)))
            elif self.game_info['top_score'] < 100000:
                self.state_labels.append((self.create_label('0{0}'.format(self.game_info['top_score'])), (400, 465)))
            else:
                self.state_labels.append((self.create_label('{0}'.format(self.game_info['top_score'])), (400, 465)))
        elif self.state == 'load_screen':
            self.state_labels.append((self.create_label('WORLD'), (280, 200)))
            self.state_labels.append((self.create_label('1-1'), (430, 200)))
            self.state_labels.append((self.create_label('X {}'.format(self.game_info['lives'])), (380, 280)))
            self.player_image = tools.get_image(setup.graphics['mario_bros'], 178, 32, 12, 16, (0, 0, 0),
                                                consts.BG_MULTI_TIMES)
        elif self.state == 'load_level2':
            self.state_labels.append((self.create_label('WORLD'), (280, 200)))
            self.state_labels.append((self.create_label('1-2'), (430, 200)))
            self.state_labels.append((self.create_label('X {}'.format(self.game_info['lives'])), (380, 280)))
            self.player_image = tools.get_image(setup.graphics['mario_bros'], 178, 32, 12, 16, (0, 0, 0),
                                                consts.BG_MULTI_TIMES)
        elif self.state == 'load_level3':
            self.state_labels.append((self.create_label('WORLD'), (280, 200)))
            self.state_labels.append((self.create_label('1-3'), (430, 200)))
            self.state_labels.append((self.create_label('X {}'.format(self.game_info['lives'])), (380, 280)))
            self.player_image = tools.get_image(setup.graphics['mario_bros'], 178, 32, 12, 16, (0, 0, 0),
                                                consts.BG_MULTI_TIMES)
        elif self.state == 'load_level4':
            self.state_labels.append((self.create_label('WORLD'), (280, 200)))
            self.state_labels.append((self.create_label('1-4'), (430, 200)))
            self.state_labels.append((self.create_label('X {}'.format(self.game_info['lives'])), (380, 280)))
            self.player_image = tools.get_image(setup.graphics['mario_bros'], 178, 32, 12, 16, (0, 0, 0),
                                                consts.BG_MULTI_TIMES)
        elif self.state == 'game_over':
            self.state_labels.append((self.create_label('GAME OVER'), (280, 300)))

    def create_info_labels(self):
        self.info_labels = []
        self.info_labels.append((self.create_label('MARIO'), (75, 30)))  # 可更改区域
        self.info_labels.append((self.create_label('WORLD'), (450, 30)))
        self.info_labels.append((self.create_label('TIME'), (625, 30)))
        if self.game_info['states'] in ['level', 'level2', 'level3', 'level4']:
            self.info_labels.append((self.create_label('1-{}'.format(change(self.game_info['states']))), (475, 55)))
        else:
            self.info_labels.append((self.create_label('LOAD'), (463, 55)))

    def create_label(self, label, size=40, width_scale=2.5, height_scale=1.8, color=None):  # create Mario font
        font = pygame.font.Font(consts.FONT, size)
        if color == None:
            label_image = font.render(label, 1, (255, 255, 255))  # get Surface
        elif color == 1:
            label_image = font.render(label, 1, (255, 0, 0))  # get Surface
        elif color == 2:
            label_image = font.render(label, 1, (255, 253, 85))  # get Surface
        # mosaic process
        rect = label_image.get_rect()
        label_image = pygame.transform.scale(label_image, (int(rect.width * width_scale),
                                                           int(rect.height * height_scale)))
        return label_image

    def update(self, level_info):
        self.create_countdown()
        self.flash_coin.update()
        self.flash_text.update()
        self.TONYDANCE.update()
        self.create_score_group(level_info['score'])
        self.create_coin_counter(level_info['coin'])

    def draw(self, surface: pygame.Surface, key=None):
        if self.state == 'TOBEDONE':
            self.TOBE_done.append((self.create_label('2 PLAYER MODE IS STILL', 40, 3, 2), (80, 80)))
            self.TOBE_done.append((self.create_label('UNDER DEVELOPMENT,', 40, 3, 2), (140, 170)))
            self.TOBE_done.append((self.create_label('PLEASE UNDERSTAND!', 40, 3, 2), (140, 260)))
            self.TOBE_done.append((self.create_label('-TONY', 40, 3, 2), (600, 350)))
            self.TOBE_done.append((self.create_label("PRESS 'K' TO RETURN", 40), (300, 440)))
            for label in self.TOBE_done:
                surface.blit(label[0], label[1])
            surface.blit(self.TONYDANCE.image, self.TONYDANCE.rect)

        elif self.state == 'game_win':
            surface.blit(self.create_label('PRESS "ENTER" TO READ', 40, 2, 1.5), (20, 20))
            self.TOBE_done.append((self.create_label('CONGRATS!', 40, 5, 3.7, 1), (180, 80)))
            self.TOBE_done.append((self.create_label("YOU'VE JUST SAVE", 40, 3, 2), (155, 180)))
            self.TOBE_done.append((self.create_label('THE PRINCESS!', 40, 3, 2, 2), (195, 240)))
            self.TOBE_done.append(
                (self.create_label('AND YOUR SCORE IS {}'.format(self.game_info['score']), 40, 3, 2), (55, 300)))
            self.TOBE_done.append((self.create_label("PRESS 'W' TO BACK", 40, 2, 1.5), (320, 420)))
            if key[pygame.K_RETURN] and self.click and self.idx < 5:
                self.click = False
                self.idx += 1
            for i in range(0, self.idx):
                surface.blit(self.TOBE_done[i][0], self.TOBE_done[i][1])
            surface.blit(self.TONYDANCE.image, self.TONYDANCE.rect)
            if not key[pygame.K_RETURN]:
                self.click = True
        else:
            for label in self.state_labels:
                surface.blit(label[0], label[1])
            for label in self.info_labels:
                surface.blit(label[0], label[1])
            for label in self.update_labels:  # 画出更新后分数的信息
                surface.blit(label[0], label[1])
            for label in self.coin_labels:  # 画出更新后的金币信息
                surface.blit(label[0], label[1])
            for label in self.time_labels:  # 画出更新后的时间信息
                surface.blit(label[0], label[1])
            if self.lives_labels:
                for label in self.lives_labels:
                    surface.blit(label[0], label[1])
                self.lives_labels.clear()
            surface.blit(self.flash_coin.image, self.flash_coin.rect)
            if self.state in ['load_screen', 'load_level2', 'load_level3', 'load_level4']:
                surface.blit(self.player_image, (320, 275))
        if self.state == 'main_menu':
            surface.blit(self.flash_text.image, self.flash_text.rect)


def change(str) -> int:
    if str == 'level':
        return 1
    if str == 'level2':
        return 2
    if str == 'level3':
        return 3
    if str == 'level4':
        return 4
