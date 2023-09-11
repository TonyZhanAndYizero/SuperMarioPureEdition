# tools and main functions
import pygame
import random
import os, sys


# from . import sound


class Game:
    def __init__(self, state_dictionary, start_state):
        self.screen = pygame.display.get_surface()  # get canvas(Surface)
        self.clock = pygame.time.Clock()  # game time countdown
        self.keys = pygame.key.get_pressed()  # key pressed
        self.mouse = pygame.mouse.get_pressed()
        self.mouse_xy = pygame.mouse.get_pos()
        self.state_dictionary = state_dictionary  # import dictionart storing states
        self.state = self.state_dictionary[start_state]  # initialize certion stage(different class)
        self.current_time = 0
        self.fps = 1
        self.fps_check = [45, 60, 90]
        self.fps_lock = False

    def update(self):
        if self.keys[pygame.K_ESCAPE]:
            pygame.display.quit()
            pygame.quit()
            sys.exit()
        if self.keys[pygame.K_f] and not self.fps_lock:
            self.fps += 1
            self.fps %= 3
            self.fps_lock = True
        if self.fps_lock and not self.keys[pygame.K_f]:
            self.fps_lock = False
        if self.state.finished:  # 检查每一阶段是否完毕
            self.state.finished = False
            game_info = self.state.game_info
            next_state = self.state.next
            self.state = self.state_dictionary[next_state]
            self.state.start(game_info, self.current_time)  # 可重生，死亡再开始循环
        self.state.update(self.screen, self.keys, self.current_time, self.mouse,self.mouse_xy)

    def run(self):
        # game starts
        while True:  # update <-> draw loop
            for event in pygame.event.get():  # event takes place(keyboard, mouse and etc.)
                if event.type == pygame.QUIT:
                    pygame.display.quit()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:  # press down a key
                    self.keys = pygame.key.get_pressed()
                elif event.type == pygame.KEYUP:  # eject up a key
                    self.keys = pygame.key.get_pressed()

                if event.type == pygame.MOUSEBUTTONUP:
                    self.mouse = pygame.mouse.get_pressed()
                    self.mouse_xy = pygame.mouse.get_pos()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse = pygame.mouse.get_pressed()
                    self.mouse_xy = pygame.mouse.get_pos()

            self.update()  # state updating __init__ Surface
            pygame.display.update()
            self.clock.tick(self.fps_check[self.fps])  # FPS:high 120;mid 60;low 30


def load_graphics(path, accept=(
        '.jpg', '.png', '.bmp', '.gif')):  # dir-path and file accepted; function:loading all graphics that i need
    graphics = {}  # a dictionary storing all pictures' info
    for picture in os.listdir(path):  # travel the whole dir
        name, extern = os.path.splitext(picture)  # such as 'file.txt' into 'file' and '.txt'
        if extern.lower() in accept:
            image = pygame.image.load(os.path.join(path, picture))  # loading picture(Surface)
            if image.get_alpha():  # mosaic_background picture process
                image = image.convert_alpha()
            else:  # normal picture process
                image = image.convert()
            # not necessary. just a way to accelerate the game
            graphics[name] = image
    return graphics  # str -> Surface


def load_music(dir, accept=('.wav', '.mp3', '.ogg', '.mdi')):
    songs = {}
    for song in os.listdir(dir):
        name, ext = os.path.splitext(song)
        if ext.lower() in accept:
            songs[name] = os.path.join(dir, song)
    return songs


def load_sound(dir, accept=('.wav', '.mp3', '.ogg', '.mdi')):
    effects = {}
    for fx in os.listdir(dir):
        name, ext = os.path.splitext(fx)
        if ext.lower() in accept:
            effects[name] = os.path.join(dir, fx)
    return effects


def get_image(picture, x, y, width, height, colorkey, scale):
    # (x,y) is the nw location
    # size is a dimension storing the needed (width,height)
    # colorkey can help us photoshop the very color we don't expect to use
    # scale is the zooming times
    size = (width, height)
    image = pygame.Surface(size)  # a blank canvas
    image.blit(picture, (0, 0),
               (x, y, size[0], size[1]))  # (从哪开始画)start with (0,0)-nw, (要图片的哪)using picture's (x,y)-nw's(width,height)
    image.set_colorkey(colorkey, 200)  # fast photoshop
    image = pygame.transform.scale(image,
                                   (int(size[0] * scale), int(size[1] * scale)))  # zooming the image for scale times
    return image
