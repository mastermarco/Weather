from debug import *
from config import *
import pygame
import os


class Loading(pygame.sprite.Sprite):
    def __init__(self):
        global DEBUG
        super(Loading, self).__init__()

        if DEBUG:
            url = "C:\\Users\\marco\\PycharmProjects\\Weather\\img\\loading\\frame-"
        else:
            mypath = os.path.dirname(os.path.realpath(__file__))
            url = os.path.join(mypath, 'img/loading/frame-')

        self.images = []
        for x in range(30):
            self.images.append(pygame.image.load(url + str(x) + ".png"))

        self.index = 0
        self.image = self.images[self.index]
        self.rect = pygame.Rect(0, 0, 46, 46)

    def set_position(self, x, y):
        self.rect.center = (x, y)

    def update(self):
        self.index += 1

        if self.index >= len(self.images):
            self.index = 0

        self.image = self.images[self.index]

