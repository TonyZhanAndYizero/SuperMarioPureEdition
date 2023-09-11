from ..components import info, player, stuff, brick, box, enemy, flagpole, coin
from ..components.box import Textinfo
import pygame, os, json
from .. import setup, consts, sound


class Level:
    def start(self, game_info, current_time):
        self.current_time = current_time
        self.game_info = game_info
        self.game_info['states'] = 'level'
        if self.game_info['player_state'] == 'big':
            self.player.big = True
        self.finished = False
        self.next = 'load_level2'  # for now
        self.info = info.Info('level2', game_info)
        self.addOnce = True
        self.onceWinText = True
        self.mouseOnce = True
        self.load_map_data()
        self.setup_checkpoint()
        self.setup_background()
        self.setup_spawnpoint()
        self.setup_player()
        self.setup_ground_items()
        self.setup_bricksAndboxes()  # 画bricks and boxes
        self.setup_enemies()
        self.setup_flag()
        self.setup_visibleCoin()
        self.sound = sound.Sound()

    def _skip(self, keys):
        if keys[pygame.K_TAB]:
            if self.player.big:
                self.game_info['player_state'] = 'big'
            else:
                self.game_info['player_state'] = 'small'
            self.sound.stop_music()
            self.sound.sound('one_up')
            self.finished = True
            self.next = 'load_level2'

    def load_map_data(self):
        file_name = 'level_1.json'
        file_path = os.path.join('source/data/maps', file_name)
        with open(file_path) as file:
            self.map_data = json.load(file)

    def setup_visibleCoin(self):
        self.visible_coin_group = pygame.sprite.Group()
        for data in self.map_data['coin']:
            x, y = data['x'], data['y']
            self.visible_coin_group.add(coin.Coin(x, y, self.game_info))

    def setup_checkpoint(self):
        self.cp_group = pygame.sprite.Group()
        for data in self.map_data['checkpoint']:
            cp_type = data['type']
            x, y, width, height = data['x'], data['y'], data['width'], data['height']
            enemyGroupId = data.get('enemy_groupid')  # an int. needed to transform str
            self.cp_group.add(stuff.Checkpoint(x, y, width, height, cp_type, enemyGroupId=enemyGroupId))

    def setup_background(self):  # initialize bg
        self.image_name = self.map_data['image_name']
        self.background = setup.graphics[self.image_name]
        rect = self.background.get_rect()
        self.background = pygame.transform.scale(self.background, (int(rect.width * consts.BG_MULTI_TIMES),
                                                                   int(rect.height * consts.BG_MULTI_TIMES)))
        self.background_rect = self.background.get_rect()
        self.game_window = setup.screen.get_rect()  # slide game window(rect)
        self.game_board = pygame.Surface((self.background_rect.width, self.background_rect.height))

    def setup_spawnpoint(self):
        self.positions = []
        for data in self.map_data['maps']:
            self.positions.append((data['start_x'], data['end_x'], data['player_x'], data['player_y']))
        self.start_x, self.end_x, self.player_x, self.player_y = self.positions[0]

    def setup_player(self):  # initialize player
        self.player = player.Player('mario', self.game_info)
        # spawnpoint
        self.player.rect.x = self.player_x + self.game_window.x
        self.player.rect.bottom = self.player_y

    def setup_ground_items(self):  # 碰撞箱设置
        self.ground_items_group = pygame.sprite.Group()  # create a sort of sprites
        for name in ['ground', 'step', 'pipe']:
            for item in self.map_data[name]:
                self.ground_items_group.add(
                    stuff.Item(item['x'], item['y'], item['width'], item['height'], name))  # like a list of sprites

    def update_game_info(self):  # 更新游戏信息
        if self.player.dead:
            self.game_info['lives'] -= 1
            if self.game_info['score'] > self.game_info['top_score']:
                self.game_info['top_score'] = self.game_info['score']
            self.reset_info()

        if self.game_info['states'] == 'game_win':
            if self.game_info['score'] > self.game_info['top_score']:
                self.game_info['top_score'] = self.game_info['score']
            self.reset_info()

        if self.game_info['lives'] <= 0:
            self.next = 'game_over'  # 死翘翘
        else:
            self.next = 'load_screen'  # 复活

    def reset_info(self):
        self.game_info['score'] = 0
        self.game_info['coin'] = 0
        self.game_info['player_state'] = 'small'
        self.game_info['states'] = 'main_menu'
        self.game_info['current_time'] = 0
        self.game_info['time'] = 401

    def setup_bricksAndboxes(self):  # 画bricks
        self.brick_group = pygame.sprite.Group()
        self.box_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()

        if 'brick' in self.map_data:
            for brick_data in self.map_data['brick']:
                x, y = brick_data['x'], brick_data['y']
                brick_type = brick_data['type']
                if brick_type == 0:
                    if 'brick_num' in brick_data:  # 批量创建,未完成
                        pass
                    else:
                        self.brick_group.add(brick.Brick(x, y, brick_type, None))
                elif brick_type == 1:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.coin_group))
                else:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.powerup_group))
        if 'box' in self.map_data:
            for box_data in self.map_data['box']:
                x, y = box_data['x'], box_data['y']
                box_type = box_data['type']
                if box_type == 1:
                    self.box_group.add(box.Box(x, y, box_type, self.coin_group, self.game_info, name='box'))
                else:
                    self.box_group.add(box.Box(x, y, box_type, self.powerup_group, self.game_info, name='box'))

    def setup_enemies(self):
        self.shell_group = pygame.sprite.Group()
        self.dead_group = pygame.sprite.Group()
        self.enemy_group_cp = pygame.sprite.Group()  # 为了后期检查点，排序出现
        self.text_info_group = pygame.sprite.Group()
        self.enemy_group = {}
        for enemy_groupdata in self.map_data['enemy']:
            group = pygame.sprite.Group()
            for id, list in enemy_groupdata.items():
                for data in list:
                    group.add(enemy.create_enemy(data))  # 根据一个个组创建不同怪
                self.enemy_group[id] = group

    def setup_flag(self):
        self.pole_group = pygame.sprite.Group()
        self.flag_group = pygame.sprite.Group()
        self.ball_group = pygame.sprite.Group()
        for item in self.map_data['flagpole']:
            x, y, type = item['x'], item['y'], item['type']
            if type == 0:
                self.flag_group.add(flagpole.Flag(x, y, 2.5))
            elif type == 1:
                self.pole_group.add(flagpole.Pole(x, y))
            elif type == 2:
                self.ball_group.add(flagpole.Ball(x, y))

    # 空图层、画画、取景
    def update_player_position(self):  # player move
        # x collision
        self.player.rect.x += self.player.x_vel
        if self.player.rect.x < self.start_x:  # map left edge
            self.player.rect.x = self.start_x
        elif self.player.rect.right > self.end_x:  # map right edge
            self.player.rect.right = self.end_x
        self.check_xcollision()
        # y collision
        if not self.player.dead:
            self.player.rect.y += self.player.y_vel
            self.check_ycollision()

    def adjust_player_xy_FLAG(self, sprite):
        self.player.x_vel = 0
        self.player.rect.top = sprite.rect.top - 10
        self.player.rect.right = sprite.rect.right  # right side stop

    def check_xcollision(self):
        check_group = pygame.sprite.Group(self.ground_items_group, self.brick_group, self.box_group)  # 多碰撞加和
        collision = pygame.sprite.spritecollideany(self.player, check_group)  # collision detection
        if collision:  # collision is the first collide item
            self.adjust_player_x(collision)

        collide_flag = pygame.sprite.spritecollideany(self.player, self.flag_group)
        if collide_flag and self.addOnce:
            self.sound.music('flagpole', 0.5)
            self.addOnce = False
            self.player.embraceFlag = True
            collide_flag.down = True
            self.game_info['score'] += 2000
            self.text_info_group.add(Textinfo(collide_flag.rect.x + 100, collide_flag.rect.y + 150, '+ 2000'))
            self.adjust_player_xy_FLAG(collide_flag)

        if self.player.godlike:
            return

        coin = pygame.sprite.spritecollideany(self.player, self.visible_coin_group)
        if coin:
            coin.trigger_up()
            self.visible_coin_group.remove(coin)
            self.dead_group.add(coin)

        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group_cp)
        if enemy:
            if self.player.big:
                self.player.state = 'bigtosmall'
                if self.player.dingzhen:
                    self.sound.sound('dingzhen_bigtosmall')
                self.player.fire = False
                self.player.godlike = True
            else:
                self.player.trigger_die()

        shell = pygame.sprite.spritecollideany(self.player, self.shell_group)
        if shell:  # 撞龟壳了！
            if shell.state == 'slide':
                if self.player.big:
                    self.player.state = 'bigtosmall'
                    if self.player.dingzhen:
                        self.sound.sound('dingzhen_bigtosmall')
                    self.player.fire = False
                    self.player.godlike = True  # 伤害免疫
                else:
                    self.player.trigger_die()
            else:
                if self.player.rect.x < shell.rect.x:
                    shell.x_vel = 5  # 开始滑动
                    shell.rect.x += 40
                    shell.direct = 1
                else:
                    shell.x_vel = -5
                    shell.rect.x -= 40
                    shell.direct = 0
                shell.state = 'slide'

        powerup = pygame.sprite.spritecollideany(self.player, self.powerup_group)
        if powerup:
            if powerup.name == 'fireball':
                pass
            elif powerup.name == 'mushroom':
                self.game_info['score'] += 1000
                self.text_info_group.add(Textinfo(powerup.rect.centerx + 50, powerup.rect.centery, '+ 1000'))
                self.sound.sound('pipe')  # 变身
                self.player.state = 'smalltobig'
                powerup.kill()
            elif powerup.name == 'fireflower':
                self.game_info['score'] += 1000
                self.text_info_group.add(Textinfo(powerup.rect.centerx + 50, powerup.rect.centery, '+ 1000'))
                self.sound.sound('powerup')
                self.player.state = 'bigtofire'
                powerup.kill()
            elif powerup.name == 'lifemushroom':
                self.game_info['score'] += 1000
                self.text_info_group.add(Textinfo(powerup.rect.centerx + 50, powerup.rect.centery, '+ 1000'))
                self.sound.sound('smoke', 1.5)
                self.player.dingzhen = 'True'
                self.text_info_group.add(
                    stuff.PureText(powerup.rect.centerx, powerup.rect.centery, 'DingZhen,START!', 1))
                powerup.kill()
            elif powerup.name == 'star':
                self.game_info['score'] += 1000
                self.text_info_group.add(Textinfo(powerup.rect.centerx + 50, powerup.rect.centery, '+ 1000'))
                self.sound.sound('powerup')
                self.player.godlike = True  # 伤害免疫
                powerup.kill()

    def adjust_player_x(self, sprite):
        if self.player.rect.x < sprite.rect.x:
            self.player.rect.right = sprite.rect.x  # right side stop
        else:
            self.player.rect.x = sprite.rect.right
        self.player.x_vel = 0

    def check_ycollision(self):  # bug?
        ground_item = pygame.sprite.spritecollideany(self.player, self.ground_items_group)
        brick = pygame.sprite.spritecollideany(self.player, self.brick_group)
        box = pygame.sprite.spritecollideany(self.player, self.box_group)
        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group_cp)

        if brick and box:  # 多碰撞
            brick_len = abs(self.player.rect.centerx - brick.rect.centerx)
            box_len = abs(self.player.rect.centerx - box.rect.centerx)
            if brick_len > box_len:
                brick = None
            else:
                box = None

        if ground_item:
            self.adjust_player_y(ground_item)
            self.player.embraceFlag = False
        elif brick:
            self.adjust_player_y(brick)
            self.player.embraceFlag = False
        elif box:  # bug:box碰撞箱太少
            self.adjust_player_y(box)
            self.player.embraceFlag = False
        self.check_fall(self.player)

        if enemy and not self.is_frozen():
            if self.player.godlike:
                return
            self.text_info_group.add(Textinfo(enemy.rect.x, enemy.rect.y, '+ 100'))
            self.enemy_group_cp.remove(enemy)
            self.game_info['score'] += 100
            if enemy.name == 'turtle':
                self.shell_group.add(enemy)
            else:
                self.dead_group.add(enemy)  # 方便单独处理死亡图案
            if self.player.y_vel <= 0:
                how = 'up'
                self.sound.sound('kick')
            else:
                if enemy.name == 'mushroom' and self.player.dingzhen:
                    self.sound.sound('mushroom_dingzhen', 2.5)
                else:
                    self.sound.sound('stomp')  # 踩死小野怪的声音
                how = 'down'
                self.player.state = 'jump'
                self.player.rect.bottom = enemy.rect.top  # 踩头
                self.player.y_vel = self.player.jump_vel
            enemy.trigger_die(how, 1 if self.player.face_right else -1)

    def adjust_player_y(self, sprite):
        # 从上往下撞
        if self.player.rect.bottom < sprite.rect.bottom:
            self.player.y_vel = 0
            self.player.rect.bottom = sprite.rect.top
            self.player.state = 'walk'
            # 从下往上撞
        else:
            self.player.y_vel = 6
            self.player.rect.top = sprite.rect.bottom
            self.player.state = 'fall'
            if self.player.dingzhen:
                self.sound.sound('dingzhen_oh', 1.8)
            self.enemyOn(sprite)  # 判断怪物，然后一箭双雕！

            if sprite.name == 'box':
                if sprite.state == 'rest':
                    sprite.trigger_up()  # TODO sound?

            if sprite.name == 'brick':
                if sprite.state == 'rest':
                    sprite.trigger_up()
                if self.player.big and sprite.brick_type == 0:
                    sprite.smashed(self.dead_group)

    def enemyOn(self, sprite):
        sprite.rect.y -= 1
        enemy = pygame.sprite.spritecollideany(sprite, self.enemy_group_cp)
        if enemy:
            self.sound.sound('kick')
            self.game_info['score'] += 150
            self.text_info_group.add(Textinfo(enemy.rect.centerx, enemy.rect.centery, '+ 150'))
            self.enemy_group_cp.remove(enemy)
            self.dead_group.add(enemy)
            if sprite in self.ground_items_group or sprite in self.brick_group or sprite in self.box_group:
                if sprite.rect.centerx > enemy.rect.centerx:
                    enemy.trigger_die('up', -1)  # 左边飞
                else:
                    enemy.trigger_die('up')
            else:
                enemy.trigger_die('up')
            if enemy.name == 'mushroom' and self.player.dingzhen:
                self.sound.sound('mushroom_dingzhen')
        sprite.rect.y += 1

    def check_fall(self, sprite):
        sprite.rect.y += 1  # 测试
        check_group = pygame.sprite.Group(self.ground_items_group, self.brick_group, self.box_group)
        collide = pygame.sprite.spritecollideany(sprite, check_group)
        if not collide and sprite.state != 'jump' and not self.is_frozen():
            sprite.state = 'fall'
        sprite.rect.y -= 1  # 还原

    def update_game_window(self):  # if 1/3 window,window move
        one_third = self.game_window.x + self.game_window.width / 3
        if self.player.x_vel > 0 and self.player.rect.centerx > one_third and self.game_window.right < self.end_x:
            self.game_window.x += self.player.x_vel
            self.start_x = self.game_window.x  # updating the left,making mario stuck in site

    def check_cp(self, keys):
        check = pygame.sprite.spritecollideany(self.player, self.cp_group)  # return stuff.Checkpoint
        if check:
            if check.cp_type == 0:  # monsters
                self.enemy_group_cp.add(self.enemy_group[str(check.enemyGroupId)])  # 释放
                check.kill()
            if check.cp_type == 10:
                self.is_or_not_finished(keys)
            if check.cp_type == 10 and self.onceWinText:
                self.game_info['score'] += 1000
                self.text_info_group.add(Textinfo(check.rect.centerx, check.rect.centery, '+ 1000'))
                self.text_info_group.add(stuff.PureText(check.rect.centerx, check.rect.centery, "PRESS '9' TO WIN"))
                self.onceWinText = False

    def is_or_not_finished(self, keys):
        if keys[pygame.K_9]:
            if self.player.big:
                self.game_info['player_state'] = 'big'
            else:
                self.game_info['player_state'] = 'small'
            self.sound.music('stage_clear')
            self.finished = True
            self.next = 'load_level2'

    def mouse_put(self, mouse, mouse_xy):
        if mouse[0] and self.mouseOnce:
            self.brick_group.add(brick.Brick(mouse_xy[0]+self.game_window.x-20, mouse_xy[1]-20, 0, None))
            self.mouseOnce = False

    def update(self, surface: pygame.Surface, keys, current_time, mouse,mouse_xy):
        self.mouse_put(mouse,mouse_xy)
        if not mouse[0]:
            self.mouseOnce = True
        if not pygame.mixer.music.get_busy():
            self.sound.music('main_theme', 0.5)
        self.current_time = pygame.time.get_ticks()
        self.player.update(keys, self)
        self.info.update(self.game_info)

        if self.player.dead:  # 死了
            if self.current_time - self.player.death_timer > 3000:
                self.finished = True  # 游戏结束
                self.update_game_info()
        elif self.is_frozen():
            pass
        else:
            self.update_player_position()
            self.update_game_window()
            self.check_cp(keys)
            self.check_trigger_die()  # 检查是否死了:看是不是滚屏幕外面去了
            self.brick_group.update(self)  # 砖块更新，sprite的update方法
            self.box_group.update(self)
            self.enemy_group_cp.update(self)  # enemy为首要的类，它需要我们update时候传入level.即地图信息
            self.dead_group.update(self)
            self.shell_group.update(self)
            self.coin_group.update(self)
            self.powerup_group.update(self)  # ?pwu?
            self.pole_group.update()
            self.flag_group.update(self)
            self.ball_group.update()
            self.visible_coin_group.update(self)
            self.text_info_group.update(self)

            self.time_out()
            self._skip(keys)
        self.draw(surface)

    def time_out(self):
        if self.game_info['time'] <= 0:
            self.sound.music('out_of_time')
            self.game_info['lives'] = 0
            self.game_info['time'] = 0
            self.player.trigger_die()

    def is_frozen(self):
        return self.player.state in ['smalltobig', 'bigtosmall', 'bigtofire', 'firetosmall']

    def draw(self, surface: pygame.Surface):
        self.game_board.blit(self.background, self.game_window,
                             self.game_window)  # 将background中的gamewindow部分，画在gameboard上
        self.powerup_group.draw(self.game_board)
        self.brick_group.draw(self.game_board)  # 画bricks，pygame的Groupdraw方法
        self.box_group.draw(self.game_board)
        self.enemy_group_cp.draw(self.game_board)  # 一个个画怪物
        self.dead_group.draw(self.game_board)  # 一个个画怪物
        self.shell_group.draw(self.game_board)
        self.coin_group.draw(self.game_board)
        self.flag_group.draw(self.game_board)
        self.pole_group.draw(self.game_board)
        self.ball_group.draw(self.game_board)
        self.visible_coin_group.draw(self.game_board)
        self.text_info_group.draw(self.game_board)
        self.game_board.blit(self.player.image, self.player.rect)  # 将player画在gameboard上
        if self.player.dingzhen and self.player.big:
            self.game_board.blit(self.player.DINGZHEN_image, self.player.rect)
        elif self.player.dingzhen and not self.player.big:
            recting=(self.player.rect.x-4,self.player.rect.y-10)
            self.game_board.blit(self.player.DINGZHEN_image,recting)
        surface.blit(self.game_board, (0, 0), self.game_window)  # 将gameboard中的gamewindow部分（人和地图）画在surface输出
        self.info.update(self.game_info)  # 调用信息更新方法，调用金币类更新类更新方法,实现金币闪烁
        self.info.draw(surface)

    def check_trigger_die(self):  # 跑屏幕外了就是死了
        if self.player.rect.y > consts.SCREEN_HEIGHT:
            self.player.trigger_die()


class Level2(Level):
    def __init__(self):
        Level.__init__(self)

    def start(self, game_info, current_time):
        self.current_time = current_time
        self.game_info = game_info
        self.game_info['states'] = 'level2'
        self.finished = False
        self.next = 'load_level3'  # for now
        self.info = info.Info('level2', game_info)
        self.addOnce = True
        self.onceWinText = True
        self.mouseOnce = True
        self.load_map_data()
        self.setup_checkpoint()
        self.setup_background()
        self.setup_spawnpoint()
        self.setup_player()
        if self.game_info['player_state'] == 'big':
            self.player.big = True
        self.setup_ground_items()
        self.setup_bricksAndboxes()  # 画bricks and boxes
        self.setup_enemies()
        self.setup_flag()
        self.setup_visibleCoin()
        self.sound = sound.Sound()

    def _skip(self, keys):
        if keys[pygame.K_TAB]:
            if self.player.big:
                self.game_info['player_state'] = 'big'
            else:
                self.game_info['player_state'] = 'small'
            self.sound.stop_music()
            self.sound.sound('one_up')
            self.finished = True
            self.next = 'load_level3'

    def mouse_put(self, mouse, mouse_xy):
        if mouse[0] and self.mouseOnce:
            self.brick_group.add(brick.Brick(mouse_xy[0]+self.game_window.x-20, mouse_xy[1]-20, 1, None))
            self.mouseOnce = False

    def setup_bricksAndboxes(self):  # 画bricks
        self.brick_group = pygame.sprite.Group()
        self.box_group = pygame.sprite.Group()
        self.coin_group = pygame.sprite.Group()
        self.powerup_group = pygame.sprite.Group()

        if 'brick' in self.map_data:
            for brick_data in self.map_data['brick']:
                x, y = brick_data['x'], brick_data['y']
                brick_type, brick_color = brick_data['type'], brick_data['color']
                if brick_type == 0:
                    if 'brick_num' in brick_data:  # 批量创建,未完成
                        if brick_data['direction'] == 1:
                            for i in range(0, int(brick_data['brick_num'])):
                                self.brick_group.add(brick.Brick(x, y + i * 43, brick_type, None, brick_color))
                        else:
                            for i in range(0, int(brick_data['brick_num'])):
                                self.brick_group.add(brick.Brick(x + i * 43, y, brick_type, None, brick_color))
                            # 太多了呜呜呜卡炸了
                    else:
                        self.brick_group.add(brick.Brick(x, y, brick_type, None, brick_color))
                elif brick_type == 1:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.coin_group, brick_color))
                else:
                    self.brick_group.add(brick.Brick(x, y, brick_type, self.powerup_group, brick_color))
        if 'box' in self.map_data:
            for box_data in self.map_data['box']:
                x, y = box_data['x'], box_data['y']
                box_type, box_color = box_data['type'], box_data['color']
                if box_type == 1:
                    self.box_group.add(box.Box(x, y, box_type, self.coin_group, self.game_info, box_color, name='box'))
                else:
                    self.box_group.add(
                        box.Box(x, y, box_type, self.powerup_group, self.game_info, box_color, name='box'))

    def load_map_data(self):
        file_name = 'level_2.json'
        file_path = os.path.join('source/data/maps', file_name)
        with open(file_path) as f:
            self.map_data = json.load(f)

    def is_or_not_finished(self, keys):
        if keys[pygame.K_9]:
            if self.player.big:
                self.game_info['player_state'] = 'big'
            else:
                self.game_info['player_state'] = 'small'
            self.sound.music('stage_clear')
            self.finished = True
            self.next = 'load_level3'

    def clear_rubbish(self):
        list_of_sprites = self.brick_group.sprites()
        for item in list_of_sprites:
            if item.rect.right < self.game_window.x:
                self.brick_group.remove(item)
                list_of_sprites.remove(item)

    def mouse_put(self, mouse, mouse_xy):
        if mouse[0] and self.mouseOnce:
            self.brick_group.add(brick.Brick(mouse_xy[0]+self.game_window.x-20, mouse_xy[1]-20, 0, None))
            self.mouseOnce = False

    def update(self, surface: pygame.Surface, keys, current_time, mouse,mouse_xy):
        self.mouse_put(mouse, mouse_xy)
        if not mouse[0]:
            self.mouseOnce = True
        if not pygame.mixer.music.get_busy():
            self.sound.music('invincible')
        self.current_time = pygame.time.get_ticks()
        self.player.update(keys, self)
        self.info.update(self.game_info)

        if self.player.dead:  # 死了
            if self.current_time - self.player.death_timer > 2500:
                self.finished = True  # 游戏结束
                self.update_game_info()
        elif self.is_frozen():
            pass
        else:
            self.update_player_position()
            self.update_game_window()
            self.check_cp(keys)
            self.check_trigger_die()  # 检查是否死了:看是不是滚屏幕外面去了
            self.brick_group.update(self)  # 砖块更新，sprite的update方法
            self.box_group.update(self)
            self.enemy_group_cp.update(self)  # enemy为首要的类，它需要我们update时候传入level.即地图信息
            self.dead_group.update(self)
            self.shell_group.update(self)
            self.coin_group.update(self)
            self.powerup_group.update(self)  # ?pwu?
            self.pole_group.update()
            self.flag_group.update(self)
            self.ball_group.update()
            self.visible_coin_group.update(self)
            self.text_info_group.update(self)
            self.time_out()
            self.clear_rubbish()
            self._skip(keys)
        self.draw(surface)


class Level3(Level):
    def __init__(self):
        Level.__init__(self)

    def start(self, game_info, current_time):
        self.current_time = current_time
        self.game_info = game_info
        self.game_info['states'] = 'level3'
        self.finished = False
        self.next = 'load_level4'  # for now
        self.info = info.Info('level3', game_info)
        self.addOnce = True
        self.onceWinText = True
        self.mouseOnce = True
        self.load_map_data()
        self.setup_checkpoint()
        self.setup_background()
        self.setup_spawnpoint()
        self.setup_player()
        if self.game_info['player_state'] == 'big':
            self.player.big = True
        self.setup_ground_items()
        self.setup_bricksAndboxes()  # 画bricks and boxes
        self.setup_enemies()
        self.setup_flag()
        self.setup_visibleCoin()
        self.sound = sound.Sound()

    def load_map_data(self):
        file_name = 'level_3.json'
        file_path = os.path.join('source/data/maps', file_name)
        with open(file_path) as f:
            self.map_data = json.load(f)

    def _skip(self, keys):
        if keys[pygame.K_TAB]:
            if self.player.big:
                self.game_info['player_state'] = 'big'
            else:
                self.game_info['player_state'] = 'small'
            self.sound.stop_music()
            self.sound.sound('one_up')
            self.finished = True
            self.next = 'load_level4'

    def is_or_not_finished(self, keys):
        if keys[pygame.K_9]:
            if self.player.big:
                self.game_info['player_state'] = 'big'
            else:
                self.game_info['player_state'] = 'small'
            self.sound.music('stage_clear')
            self.finished = True
            self.next = 'load_level4'


class Level4(Level):
    def __init__(self):
        Level.__init__(self)

    def start(self, game_info, current_time):
        self.current_time = current_time
        self.game_info = game_info
        self.game_info['states'] = 'level4'
        self.finished = False
        self.next = 'game_over'  # for now
        self.info = info.Info('level4', game_info)
        self.addOnce = True
        self.onceWinText = True
        self.mouseOnce = True
        self.load_map_data()
        self.setup_checkpoint()
        self.setup_background()
        self.setup_spawnpoint()
        self.setup_player()
        if self.game_info['player_state'] == 'big':
            self.player.big = True
        self.setup_ground_items()
        self.setup_bricksAndboxes()  # 画bricks and boxes
        self.setup_enemies()
        self.setup_flag()
        self.setup_visibleCoin()
        self.setup_princess()
        self.sound = sound.Sound()

    def _skip(self, keys):
        if keys[pygame.K_TAB]:
            if self.player.big:
                self.game_info['player_state'] = 'big'
            else:
                self.game_info['player_state'] = 'small'
            self.sound.stop_music()
            self.sound.sound('one_up')
            self.finished = True
            self.next = 'game_win'

    def setup_princess(self):
        self.princess_group = pygame.sprite.Group()
        for data in self.map_data['princess']:
            x, y = data['x'], data['bottom']
            self.princess_group.add(box.Princess(x, y, self.game_info))

    def load_map_data(self):
        file_name = 'level_4.json'
        file_path = os.path.join('source/data/maps', file_name)
        with open(file_path) as f:
            self.map_data = json.load(f)

    def check_xcollision(self):
        check_group = pygame.sprite.Group(self.ground_items_group, self.brick_group, self.box_group)  # 多碰撞加和
        collision = pygame.sprite.spritecollideany(self.player, check_group)  # collision detection
        if collision:  # collision is the first collide item
            self.adjust_player_x(collision)

        collide_princess = pygame.sprite.spritecollideany(self.player, self.princess_group)
        if collide_princess and self.addOnce:
            self.sound.music('world_wanderer', 0.5)
            self.addOnce = False
            self.text_info_group.add(
                stuff.PureText(collide_princess.rect.x - 100, collide_princess.rect.y, "PRESS '9' TO WIN"))
            if self.player.dingzhen:
                self.text_info_group.add(
                    stuff.PureText(collide_princess.rect.x + 10, collide_princess.rect.y - 40, "-", 1, 23, 3),
                    stuff.PureText(collide_princess.rect.x + 13, collide_princess.rect.y - 90, "DINGZHEN!")
                )

                self.game_info['score'] += 40000
                self.text_info_group.add(
                    Textinfo(collide_princess.rect.x - 50, collide_princess.rect.y - 10, '+ 40000'))
            else:
                self.game_info['score'] += 20000
                self.text_info_group.add(
                    Textinfo(collide_princess.rect.x - 50, collide_princess.rect.y - 10, '+ 20000'))
            collide_princess.trigger_up()

        if self.player.godlike:
            return

        coin = pygame.sprite.spritecollideany(self.player, self.visible_coin_group)
        if coin:
            coin.trigger_up()
            self.visible_coin_group.remove(coin)
            self.dead_group.add(coin)

        enemy = pygame.sprite.spritecollideany(self.player, self.enemy_group_cp)
        if enemy:
            if self.player.big:
                self.player.state = 'bigtosmall'
                self.player.godlike = True
            else:
                self.player.trigger_die()

        shell = pygame.sprite.spritecollideany(self.player, self.shell_group)
        if shell:  # 撞龟壳了！
            if shell.state == 'slide':
                if self.player.big:
                    self.player.state = 'bigtosmall'
                    self.player.godlike = True  # 伤害免疫
                else:
                    self.player.trigger_die()
            else:
                if self.player.rect.x < shell.rect.x:
                    shell.x_vel = 6  # 开始滑动
                    shell.rect.x += 40
                    shell.direct = 1
                else:
                    shell.x_vel = -6
                    shell.rect.x -= 40
                    shell.direct = 0
                shell.state = 'slide'

        powerup = pygame.sprite.spritecollideany(self.player, self.powerup_group)
        if powerup:
            if powerup.name == 'fireball':
                pass
            elif powerup.name == 'mushroom':
                self.game_info['score'] += 1000
                self.text_info_group.add(Textinfo(powerup.rect.centerx + 50, powerup.rect.centery, '+ 1000'))
                self.sound.sound('pipe')  # 变身
                self.player.state = 'smalltobig'
                powerup.kill()
            elif powerup.name == 'fireflower':
                self.game_info['score'] += 1000
                self.text_info_group.add(Textinfo(powerup.rect.centerx + 50, powerup.rect.centery, '+ 1000'))
                self.sound.sound('powerup')
                self.player.state = 'bigtofire'
                powerup.kill()
            elif powerup.name == 'lifemushroom':
                self.game_info['score'] += 1000
                self.text_info_group.add(Textinfo(powerup.rect.centerx + 50, powerup.rect.centery, '+ 1000'))
                self.sound.sound('smoke', 1.5)
                self.player.dingzhen = 'True'
                self.text_info_group.add(
                    stuff.PureText(powerup.rect.centerx, powerup.rect.centery, 'DingZhen,START!', 1))
                powerup.kill()
            elif powerup.name == 'star':
                self.game_info['score'] += 1000
                self.text_info_group.add(Textinfo(powerup.rect.centerx + 50, powerup.rect.centery, '+ 1000'))
                self.sound.sound('powerup')
                self.player.godlike = True  # 伤害免疫
                powerup.kill()

    def check_cp(self, keys):
        check = pygame.sprite.spritecollideany(self.player, self.cp_group)  # return stuff.Checkpoint
        if check:
            if check.cp_type == 0:  # monsters
                self.enemy_group_cp.add(self.enemy_group[str(check.enemyGroupId)])  # 释放
                check.kill()
            if check.cp_type == 10:
                self.is_or_not_finished(keys)

    def is_or_not_finished(self, keys):
        # print(self.player.embraceFlag,self.player.rect.y)
        if keys[pygame.K_9]:
            self.sound.stop_music()
            self.finished = True
            self.next = 'game_win'

    def update(self, surface: pygame.Surface, keys, current_time, mouse,mouse_xy):
        self.mouse_put(mouse, mouse_xy)
        if not mouse[0]:
            self.mouseOnce = True
        if not pygame.mixer.music.get_busy():
            self.sound.music('invincible')
        self.current_time = pygame.time.get_ticks()
        self.player.update(keys, self)
        self.info.update(self.game_info)

        if self.player.dead:  # 死了
            if self.current_time - self.player.death_timer > 2500:
                self.finished = True  # 游戏结束
                self.update_game_info()
        elif self.is_frozen():
            pass
        else:
            self.update_player_position()
            self.update_game_window()
            self.check_cp(keys)
            self.check_trigger_die()  # 检查是否死了:看是不是滚屏幕外面去了
            self.brick_group.update(self)  # 砖块更新，sprite的update方法
            self.box_group.update(self)
            self.enemy_group_cp.update(self)  # enemy为首要的类，它需要我们update时候传入level.即地图信息
            self.dead_group.update(self)
            self.shell_group.update(self)
            self.coin_group.update(self)
            self.powerup_group.update(self)  # ?pwu?
            self.princess_group.update(self)
            self.pole_group.update()
            self.flag_group.update(self)
            self.ball_group.update()
            self.visible_coin_group.update(self)
            self.text_info_group.update(self)
            self.time_out()
            self._skip(keys)
        self.draw(surface)

    def draw(self, surface: pygame.Surface):
        self.game_board.blit(self.background, self.game_window,
                             self.game_window)  # 将background中的gamewindow部分，画在gameboard上
        self.powerup_group.draw(self.game_board)
        self.brick_group.draw(self.game_board)  # 画bricks，pygame的Groupdraw方法
        self.box_group.draw(self.game_board)
        self.enemy_group_cp.draw(self.game_board)  # 一个个画怪物
        self.dead_group.draw(self.game_board)  # 一个个画怪物
        self.shell_group.draw(self.game_board)
        self.coin_group.draw(self.game_board)
        self.flag_group.draw(self.game_board)
        self.pole_group.draw(self.game_board)
        self.princess_group.draw(self.game_board)
        self.ball_group.draw(self.game_board)
        self.visible_coin_group.draw(self.game_board)
        self.text_info_group.draw(self.game_board)
        self.game_board.blit(self.player.image, self.player.rect)  # 将player画在gameboard上
        if self.player.dingzhen and self.player.big:
            self.game_board.blit(self.player.DINGZHEN_image, self.player.rect)
        elif self.player.dingzhen and not self.player.big:
            recting = (self.player.rect.x - 4, self.player.rect.y - 10)
            self.game_board.blit(self.player.DINGZHEN_image, recting)
        surface.blit(self.game_board, (0, 0), self.game_window)  # 将gameboard中的gamewindow部分（人和地图）画在surface输出
        self.info.update(self.game_info)  # 调用信息更新方法，调用金币类更新类更新方法,实现金币闪烁
        self.info.draw(surface)
