import pygame, os
from . import consts
from . import tools

pygame.init()  # pygame initialize
pygame.mixer.init()
pygame.display.set_caption('Super Mario Pure Edition')
screen = pygame.display.set_mode(consts.SCREEN_SIZE)  # create a game window
graphics = tools.load_graphics(os.path.join("resources", "graphics"))  # all pictures loaded
music = tools.load_music(os.path.join("resources", "music"))
sound = tools.load_sound(os.path.join("resources", "sound"))
