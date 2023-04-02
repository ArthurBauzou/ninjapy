import pygame

from sprite_map import tileset
from conf import GAME_HEIGHT, GAME_WIDTH

class Shuriken:
    def __init__(self, pos, speed):
        self.pos = [x for x in pos]
        self.speed = speed
        self.rect = pygame.Rect(-100, -100, 8, 8)
        self.rect.center = self.pos
        self.sprite = tileset['shuriken1']
        self.active = False
        self.anim_timer = 0

    def move(self):
        for i in range(2): self.pos[i] += self.speed[i]
        self.rect.center = (self.pos[0], self.pos[1])

    def warp(self):
        if self.rect.center[0] > GAME_WIDTH: self.pos[0] = 0
        if self.rect.center[0] < 0: self.pos[0] = GAME_WIDTH
        if self.rect.center[1] < 0: self.pos[1] = GAME_HEIGHT
        if self.rect.center[1] > GAME_HEIGHT: self.pos[1] = 0

    def activate(self, h_rect) :
        if not self.active and self.rect.colliderect(h_rect) == False :
            self.active = True

    def animate(self) :
        ANIM_TIME = 4
        if self.anim_timer == 0 :
            self.anim_timer = ANIM_TIME
            if self.sprite == tileset['shuriken1'] :
                self.sprite = tileset['shuriken2']
            else :
                self.sprite = tileset['shuriken1']
        else:
            self.anim_timer -= 1


