import pygame
import random
from sprite_map import tileset

class Bamboo:
    def __init__(self, pos, id):
        self.rect = pygame.Rect(0, 0, 58, 32)
        self.rect.center = (pos[0], pos[1])
        self.sprite = tileset['bamboo']
        self.OFFSET_X = 3
        self.OFFSET_Y = 24
        self.id = id

    def sprite_info(self):
        return {
            'id': self.id,
            'pos': ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y ),
            'sprite': self.sprite,
            'z-index': self.rect.bottom
        }

class Plant:
    def __init__(self, pos, id):
        self.rect = pygame.Rect(0, 0, 32, 24)
        self.rect.center = (pos[0], pos[1])
        self.sprite = tileset[random.choice(['plant1','plant2'])]
        self.id = id
        self.OFFSET_X = 0
        self.OFFSET_Y = 4
    
    def sprite_info(self):
        return {
            'id': self.id,
            'pos': ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y ),
            'sprite': self.sprite,
            'z-index': self.rect.bottom
        }
    
class Rock:
    def __init__(self, pos, id):
        self.rect = pygame.Rect(0, 0, 36, 14)
        self.rect.center = (pos[0], pos[1])
        self.sprite = tileset['rock_holy']
        self.id = id
        self.OFFSET_X = 6
        self.OFFSET_Y = 28
    
    def sprite_info(self):
        return {
            'id': self.id,
            'pos': ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y ),
            'sprite': self.sprite,
            'z-index': self.rect.bottom
        }
    
