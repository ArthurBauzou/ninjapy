import pygame, random
from typing import List

import objects

from sprite_map import tileset
from conf import GAME_HEIGHT, GAME_WIDTH

class Bamboo:

    def __init__(self, pos):
        self.rect = pygame.Rect(0, 0, 58, 32)
        self.rect.center = (pos[0], pos[1])
        self.sprite = tileset['bamboo']
        self.OFFSET_X = 3
        self.OFFSET_Y = 24
        self.sprite_pos = [ self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y ]
        self.solid = True
        # self.bristle_timer = 0

    def get_dead_zone(self):
        rect = pygame.Rect(0, 0, 58, 50)
        rect.center = self.rect.center
        rect.bottom = self.rect.bottom
        if self.rect.top < GAME_HEIGHT/2: dir = (0,1)
        else : dir = (0,-1)
        dead_zone = { 'rect': rect, 'dir': dir }
        return dead_zone

    def bristle(self, timer, list):
        if timer %24 == 0 :
            list.append(objects.Leaf(self.rect.topleft, True))
            list.append(objects.Leaf(self.rect.topright))

        if timer %9 == 0 : self.sprite_pos[0] += 1
        elif timer %6 == 0 : pass
        elif timer %3 == 0 : self.sprite_pos[0] -= 1

class Plant:
    def __init__(self, pos):
        self.rect = pygame.Rect(0, 0, 32, 24)
        self.rect.center = (pos[0], pos[1])
        self.sprite = tileset[random.choice(['plant1','plant2','plant_flower','plant1','plant2','plant1'])]
        self.OFFSET_X = 0
        self.OFFSET_Y = 4
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )
        self.solid = False
    
class Shrine:
    def __init__(self, pos):
        self.rect = pygame.Rect(0, 0, 36, 14)
        self.rect.center = (pos[0], pos[1])
        self.sprite = tileset['shrine']
        self.OFFSET_X = 6
        self.OFFSET_Y = 28
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )
        self.solid = True

    def get_dead_zone(self):
        rect = pygame.Rect(0, 0, 28, 8)
        rect.center = self.rect.center
        rect.bottom = self.rect.top
        if self.rect.center[0] < GAME_WIDTH/2: dir = (1,0)
        else : dir = (-1,0)
        dead_zone = { 'rect': rect, 'dir': dir }
        return dead_zone
    
    
