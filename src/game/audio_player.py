import os

import pygame


class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = self.load_sounds()

    def load_sounds(self):
        sounds = {}
        base_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "assets", "sounds"
        )

        sound_files = {"knock": "knock.mp3", "take": "take.mp3"}

        for name, filename in sound_files.items():
            path = os.path.join(base_path, filename)
            sounds[name] = pygame.mixer.Sound(path)

        return sounds

    def play(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()
