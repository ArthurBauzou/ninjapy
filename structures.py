import pygame
import random
from sprite_map import tileset

class Bamboo:

    def __init__(self, pos):
        self.rect = pygame.Rect(0, 0, 58, 32)
        self.rect.center = (pos[0], pos[1])
        self.sprite = tileset['bamboo']
        self.OFFSET_X = 3
        self.OFFSET_Y = 24
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )
        self.solid = True

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
    
    
