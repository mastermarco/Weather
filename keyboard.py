# -*- coding: utf-8 -*-
from debug import *
from utils import *
from config import *
import pygame


class Keyboard:
    keyboard_keys = [["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", "a", "<-",
                      "s", "d", "f", "g", "h", "j", "k", "l", "z", "x", "c", "v",
                      "b", "n", "m", "<", ">", ")", "=", "?", "@", "!", "\"", "£",
                     "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "_",
                     "€", "$", "%", "&", "/", "(", "#", "*", ";", ".", "...", "^"],
                     [",", ":", "|", "+", "..."]]
    rects = [[], []]

    password = ""
    upper_case = False

    def __init__(self, screen, WIDTH, HEIGHT, w, h):
        self.index = 0
        self.rect = pygame.Rect(int((WIDTH-w)/2), 120, w, HEIGHT-120)
        self.screen = screen
        for ks in range(0, 2):
            for k in self.keyboard_keys[ks]:
                self.rects[ks].append(None)

    def set_position(self, x, y):
        self.rect.center = (x, y)

    def switch(self):
        self.index = self.index + 1
        if self.index > 1:
            self.index = 0
            self.upper_case = False

    def get_password(self):
        return self.password

    def clean_password(self):
        self.password = ""

    def check_hit(self, x, y):
        index = 0
        for r in self.rects[self.index]:
            if r.collidepoint(x, y):
                key = self.keyboard_keys[self.index][index]
                if key == "^":
                    self.upper_case = not self.upper_case
                elif key == "...":
                    self.switch()
                elif key == "<-":
                    if len(self.password) > 0:
                        self.password = self.password[:-1]
                else:
                    if self.upper_case:
                        if key.islower():
                            key = key.upper()
                    self.password = self.password + key
                break
            index = index + 1

    def draw_keyboard_surface(self):
        global DEBUG
        image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        image.fill((183, 183, 183))
        x, y = 0, 0
        w_button = 66
        h_button = 64
        i = 0
        j = 0
        index = 0
        for k in self.keyboard_keys[self.index]:
            button_rect = pygame.Rect(w_button*i, h_button*j, w_button, h_button)
            pygame.draw.rect(image, (255, 255, 255), button_rect)
            r = pygame.Rect(w_button*i + 1, h_button*j + 1, w_button - 2, h_button - 2)
            pygame.draw.rect(image, (197, 197, 197), r)
            if DEBUG:
                font = pygame.font.Font('C:\\Windows\\Fonts\\MyriadPro-Light.ttf', 30)
            else:
                font = pygame.font.Font('MyriadPro-Light.ttf', 30)
            if self.upper_case:
                if k.islower():
                    k = k.upper()
            textSurface = font.render(k, True, (29, 29, 29))
            textRect = textSurface.get_rect()
            textRect.center = (w_button*i+int(w_button/2), int(h_button*j+h_button/2))
            image.blit(textSurface, (textRect.left, textRect.top))
            if self.rects[self.index][index] is None:
                self.rects[self.index][index] = pygame.Rect(self.rect.left+w_button*i, self.rect.top+h_button*j, w_button, h_button)
            x = x + w_button
            i = i + 1
            index = index + 1
            if i == 12:
                i = 0
                j = j + 1
            #if self.index == 1 and i == 5:
        self.screen.blit(image, (self.rect.left, self.rect.top))
