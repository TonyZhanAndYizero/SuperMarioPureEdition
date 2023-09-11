import pygame
from .. import tools, setup, consts, sound
from . import powerup
import json, os


class Player(pygame.sprite.Sprite):  # a moving player, the same as flashing coin
    def __init__(self, name, game_info):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.game_info = game_info
        self.sound = sound.Sound()
        self.load_data()
        self.setup_states()
        self.setup_velocities()
        self.setup_timers()
        self.load_images()

    def load_data(self):  # the player's state data
        file_name = self.name + '.json'  # choose the very player(mario or luigi)
        file_path = os.path.join('source/data/player', file_name)
        with open(file_path) as file:
            self.player_data = json.load(file)  # data used in load_images

    def setup_states(self):  # the player's buff, debuff and stuff
        self.state = 'stand'
        self.face_right = True
        self.dead = False
        if self.game_info['player_state'] == 'big':
            self.big = True
        else:
            self.big = False
        self.fire = False
        self.godlike = False
        self.embraceFlag = False
        self.canshoot = True
        self.canjump = True
        self.dingzhen = False

    def setup_velocities(self):  # the player's speed
        speed = self.player_data['speed']  # dictionary
        self.x_vel = 0
        self.y_vel = 0

        self.max_walk_vel = speed['max_walk_speed']
        self.max_run_vel = speed['max_run_speed']
        self.max_y_vel = speed['max_y_velocity']
        self.walk_acc = speed['walk_accel']
        self.run_acc = speed['run_accel']
        self.turn_acc = speed['turn_accel']
        self.jump_vel = speed['jump_velocity']
        self.g = consts.GRAVITY
        self.anti_g = consts.ANTI_GRAVITY

        self.max_x_vel = self.max_walk_vel
        self.x_acc = self.walk_acc

    def setup_timers(self):  # the player's state duration
        self.walking_timer = 0
        self.death_timer = 0
        self.transition_timer = 0
        self.godlike_timer = 0
        self.shoot_dur = 0

    def load_images(self):  # the player's different image in different stages
        sheet = setup.graphics['mario_bros']
        frame_rects = self.player_data['image_frames']  # dictionary:str->list;list:dictionary[]
        self.DINGZHEN_image = tools.get_image(setup.graphics['DINGZHEN'],0 ,0 , 40, 40, (0, 0, 0), 1.05)

        self.right_small_normal_frames = []
        self.right_big_normal_frames = []
        self.right_big_fire_frames = []
        self.left_small_normal_frames = []
        self.left_big_normal_frames = []
        self.left_big_fire_frames = []

        self.small_normal_frames = [self.right_small_normal_frames, self.left_small_normal_frames]
        self.big_normal_frames = [self.right_big_normal_frames, self.left_big_normal_frames]
        self.big_fire_frames = [self.right_big_fire_frames, self.left_big_fire_frames]

        self.all_frames = [
            self.right_small_normal_frames,
            self.right_big_normal_frames,
            self.right_big_fire_frames,
            self.left_small_normal_frames,
            self.left_big_normal_frames,
            self.left_big_fire_frames
        ]

        if not self.big:
            self.right_frames = self.right_small_normal_frames
            self.left_frames = self.left_small_normal_frames
        else:
            self.right_frames = self.right_big_normal_frames
            self.left_frames = self.left_big_normal_frames

        for setName, set_frame_rects in frame_rects.items():  # fill in the lists of different stages image
            for frame_rect in set_frame_rects:
                right_image = tools.get_image(sheet, frame_rect['x'], frame_rect['y'], frame_rect['width'],
                                              frame_rect['height'], (0, 0, 0), consts.BG_PLAYER_CURSOR_TIMES)
                left_image = pygame.transform.flip(right_image, True, False)
                if setName == 'right_small_normal':
                    self.right_small_normal_frames.append(right_image)
                    self.left_small_normal_frames.append(left_image)
                if setName == 'right_big_normal':
                    self.right_big_normal_frames.append(right_image)
                    self.left_big_normal_frames.append(left_image)
                if setName == 'right_big_fire':
                    self.right_big_fire_frames.append(right_image)
                    self.left_big_fire_frames.append(left_image)

        self.frame_index = 0
        self.frames = self.right_frames  # all the needed frames
        self.image = self.frames[self.frame_index]  # simple image

        self.rect = self.image.get_rect()  # player's location

    def update(self, keys, level):
        self.current_time = pygame.time.get_ticks()
        self.process_state(keys, level)  # such as walk,run and etc.
        self.is_godlike()

    def process_state(self, keys, level):
        self.canshootOrnot(keys)
        self.canjumpOrnot(keys)
        if self.state == 'stand':
            self.stand(keys, level)
        elif self.state == 'walk':
            self.walk(keys, level)
        elif self.state == 'jump':
            self.jump(keys, level)
        elif self.state == 'fall':
            self.fall(keys, level)
        elif self.state == 'die':
            self.die(keys)
        elif self.state == 'smalltobig':
            self.smalltobig(keys)
        elif self.state == 'bigtosmall':
            self.bigtosmall(keys)
        elif self.state == 'bigtofire':
            self.bigtofire(keys)

        if self.face_right:
            self.image = self.right_frames[self.frame_index]
        else:
            self.image = self.left_frames[self.frame_index]

    def canshootOrnot(self, keys):
        if not keys[pygame.K_s]:
            self.canshoot = True

    def canjumpOrnot(self, keys):
        if not keys[pygame.K_SPACE]:
            self.canjump = True

    def stand(self, keys, level):
        self.frame_index = 0  # stand pose
        self.x_vel = self.y_vel = 0  # silent
        if keys[pygame.K_d] and not keys[pygame.K_a]:  # make both botton stop
            self.face_right = True
            self.state = 'walk'  # press and walk
        elif keys[pygame.K_a] and not keys[pygame.K_d]:
            self.face_right = False
            self.state = 'walk'  # press and walk
        if keys[pygame.K_SPACE] and self.canjump:
            if self.big:
                self.sound.sound('big_jump', 0.4)
            else:
                self.sound.sound('small_jump', 0.4)
            self.state = 'jump'
            self.y_vel = self.jump_vel
        if keys[pygame.K_s] and self.fire and self.canshoot:
            self.shoot_fireball(level)

    def walk(self, keys, level):
        if keys[pygame.K_SPACE] and self.canjump:
            if self.big:
                self.sound.sound('big_jump', 0.4)
            else:
                self.sound.sound('small_jump', 0.4)
            self.state = 'jump'
            self.y_vel = self.jump_vel
        if keys[pygame.K_s] and self.fire and self.canshoot:
            self.shoot_fireball(level)
        if keys[pygame.K_w]:  # run or walk
            self.max_x_vel = self.max_run_vel
            self.x_acc = self.run_acc
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_acc = self.walk_acc  # physics knowledge

        if self.current_time - self.walking_timer > self.cal_frame_duration():
            self.frame_index = self.frame_index % 3 + 1
            self.walking_timer = self.current_time
        if keys[pygame.K_d] and not keys[pygame.K_a]:
            self.face_right = True
            if self.x_vel < 0:  # facing left has velocity, so needs to brake
                self.frame_index = 5  # brake frame
                self.x_acc = self.turn_acc
            self.x_vel = self.cal_vel(self.x_vel, self.x_acc, self.max_x_vel, True)
        elif keys[pygame.K_a] and not keys[pygame.K_d]:
            self.face_right = False
            if self.x_vel > 0:
                self.frame_index = 5
                self.x_acc = self.turn_acc
            self.x_vel = self.cal_vel(self.x_vel, self.x_acc, self.max_x_vel, False)
        else:  # didn't push <- or ->
            self.x_acc = self.walk_acc
            if self.x_vel > 0:
                self.x_vel -= self.x_acc  # slow down
                if self.x_vel < 0:  # stand position
                    self.x_vel = 0
                    self.state = 'stand'
            else:
                self.x_vel += self.x_acc  # slow down
                if self.x_vel > 0:
                    self.x_vel = 0
                    self.state = 'stand'

    def jump(self, keys, level):
        self.canjump = False
        self.frame_index = 4
        self.y_vel += self.anti_g  # 上升减速
        if self.y_vel >= 0 or not keys[pygame.K_SPACE]:
            self.state = 'fall'

        if keys[pygame.K_s] and self.fire and self.canshoot:
            self.shoot_fireball(level)

        if keys[pygame.K_w]:  # run or walk
            self.max_x_vel = self.max_run_vel
            self.x_acc = self.run_acc
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_acc = self.walk_acc  # physics knowledge

        if keys[pygame.K_d] and not keys[pygame.K_a]:
            self.face_right = True
            if self.x_vel < 0:  # facing left has velocity, so needs to brake
                self.x_acc = self.turn_acc
            self.x_vel = self.cal_vel(self.x_vel, self.x_acc, self.max_x_vel, True)
        elif keys[pygame.K_a] and not keys[pygame.K_d]:
            self.face_right = False
            if self.x_vel > 0:
                self.x_acc = self.turn_acc
            self.x_vel = self.cal_vel(self.x_vel, self.x_acc, self.max_x_vel, False)
        else:  # didn't push <- or ->
            if self.x_vel > 0:
                self.x_vel -= self.x_acc  # slow down
                if self.x_vel < 0:  # stand position
                    self.x_vel = 0
            else:
                self.x_vel += self.x_acc  # slow down
                if self.x_vel > 0:
                    self.x_vel = 0

    def fall(self, keys, level):
        if self.embraceFlag == True:
            self.y_vel = 2.5
            self.frame_index = 10
            return

        self.y_vel = self.cal_vel(self.y_vel, self.g, self.max_y_vel, True)
        if keys[pygame.K_s] and self.fire and self.canshoot:
            self.shoot_fireball(level)

        if keys[pygame.K_w]:  # run or walk
            self.max_x_vel = self.max_run_vel
            self.x_acc = self.run_acc
        else:
            self.max_x_vel = self.max_walk_vel
            self.x_acc = self.walk_acc  # physics knowledge

        if keys[pygame.K_d] and not keys[pygame.K_a]:
            self.face_right = True
            if self.x_vel < 0:  # facing left has velocity, so needs to brake
                self.x_acc = self.turn_acc
            self.x_vel = self.cal_vel(self.x_vel, self.x_acc, self.max_x_vel, True)
        elif keys[pygame.K_a] and not keys[pygame.K_d]:
            self.face_right = False
            if self.x_vel > 0:
                self.x_acc = self.turn_acc
            self.x_vel = self.cal_vel(self.x_vel, self.x_acc, self.max_x_vel, False)
        else:  # didn't push <- or ->
            self.x_acc = self.walk_acc
            if self.face_right:
                self.x_vel -= self.x_acc  # slow down
                if self.x_vel < 0:  # stand position
                    self.x_vel = 0
                    self.state = 'stand'
            else:
                self.x_vel += self.x_acc  # slow down
                if self.x_vel > 0:
                    self.x_vel = 0
                    self.state = 'stand'

    def die(self, keys):
        self.rect.y += self.y_vel
        self.y_vel += self.anti_g

    def trigger_die(self):
        self.dead = True
        self.y_vel = self.jump_vel  # dead vel向上飞
        self.frame_index = 6  # dead face
        self.state = 'die'
        self.death_timer = self.current_time  # dead time
        if self.dingzhen:
            self.sound.music('dingzhen_death')
        else:
            self.sound.music('death')

    def smalltobig(self, keys):
        frame_dur = 70
        sizes = [1, 0, 1, 0, 1, 2, 0, 1, 2, 0, 2]
        frames_and_index = [(self.small_normal_frames, 0), (self.small_normal_frames, 7), (self.big_normal_frames, 0)]
        if self.transition_timer == 0:
            self.big = True
            self.transition_timer = self.current_time
            self.transindex = 0
        elif self.current_time - self.transition_timer > frame_dur:
            self.transition_timer = self.current_time
            frames, index = frames_and_index[sizes[self.transindex]]
            self.trans_player_image(frames, index)
            self.transindex += 1
            if self.transindex == len(sizes):
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_normal_frames
                self.left_frames = self.left_big_normal_frames

    def bigtosmall(self, keys):
        frame_dur = 70
        sizes = [2, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        frames_and_index = [(self.small_normal_frames, 8), (self.big_normal_frames, 8), (self.big_normal_frames, 4)]
        if self.transition_timer == 0:
            self.big = False
            self.transition_timer = self.current_time
            self.transindex = 0
        elif self.current_time - self.transition_timer > frame_dur:
            self.transition_timer = self.current_time
            frames, index = frames_and_index[sizes[self.transindex]]
            self.trans_player_image(frames, index)
            self.transindex += 1
            if self.transindex >= len(sizes):
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_small_normal_frames
                self.left_frames = self.left_small_normal_frames

    def bigtofire(self, keys):
        frame_dur = 70
        sizes = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        frames_and_index = [(self.big_fire_frames, 3), (self.big_normal_frames, 3)]
        if self.transition_timer == 0:
            self.fire = True
            self.big = True
            self.transition_timer = self.current_time
            self.transindex = 0
        elif self.current_time - self.transition_timer > frame_dur:
            self.transition_timer = self.current_time
            frames, index = frames_and_index[sizes[self.transindex]]
            self.trans_player_image(frames, index)
            self.transindex += 1
            if self.transindex == len(sizes):
                self.transition_timer = 0
                self.state = 'walk'
                self.right_frames = self.right_big_fire_frames
                self.left_frames = self.left_big_fire_frames

    def trans_player_image(self, frames, idx):
        self.frame_index = idx
        if self.face_right:
            self.right_frames = frames[0]
            self.image = self.right_frames[self.frame_index]
        else:
            self.left_frames = frames[1]
            self.image = self.left_frames[self.frame_index]
        last_frame_bottom = self.rect.bottom
        last_frame_centerx = self.rect.centerx
        self.rect = self.image.get_rect()
        self.rect.bottom = last_frame_bottom
        self.rect.centerx = last_frame_centerx

    def cal_vel(self, vel, acc, max_vel, is_right):
        if is_right:
            return min(vel + acc, max_vel)
        else:
            return max(vel - acc, -max_vel)

    def cal_frame_duration(self):
        duration = -80 / self.max_run_vel * abs(self.x_vel) + 100  # making shake hands good
        return duration

    def is_godlike(self):
        if self.godlike:
            if self.godlike_timer == 0:
                self.godlike_timer = self.current_time
                self.blank_image = pygame.Surface((0, 0))
            elif self.current_time - self.godlike_timer < 3000:
                if (self.current_time - self.godlike_timer) % 100 < 50:
                    self.image = self.blank_image
            else:
                self.godlike = False
                self.godlike_timer = 0

    def shoot_fireball(self, level):
        self.frame_index = 6
        if self.current_time - self.shoot_dur > 1000:
            self.frame_index = 6
            self.sound.sound('fireball')
            fireball = powerup.Fireball(self.rect.centerx, self.rect.centery, self.face_right, level.game_info)
            level.powerup_group.add(fireball)  # 加入精灵组，在level里直接调用update和draw即可显示
            self.canshoot = False
            self.shoot_dur = self.current_time
