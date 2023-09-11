import pygame
from . import setup, consts


class Sound(object):
    """Handles all sound for the game"""

    def __init__(self):
        """Initialize the class"""
        self.sound_dict = setup.sound
        self.music_dict = setup.music

    def play_music(self, key, volume):
        """Plays new music"""
        pygame.mixer.music.load(self.music_dict[key])
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play()

    def stop_music(self):
        """Stops playback"""
        pygame.mixer.music.stop()

    def music(self, key, volume=1):
        self.stop_music()
        self.play_music(key, volume)

    def sound(self, key, volume=1):
        sound = pygame.mixer.Sound(self.sound_dict[key])
        sound.set_volume(volume)
        sound.play()
