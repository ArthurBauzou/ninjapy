import pygame
from sprite_map import tileset

class Kappa:
    def __init__(self, pos, id):
        self.pos = [x for x in pos]
        self.speed = [0,0]
        self.rect = pygame.Rect(-100, -100, 15, 12)
        self.rect.center = self.pos
        self.sprite = tileset['kappa']
        self.id = id
        self.OFFSET_X = 8
        self.OFFSET_Y = 16

    def sprite_info(self):
        return {
            'id': self.id,
            'pos': ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y ),
            'sprite': self.sprite,
            'z-index': self.rect.bottom
        }
    
class Ogre:
    def __init__(self, pos, id):
        self.pos = [x for x in pos]
        self.speed = [0,0]
        self.rect = pygame.Rect(-100, -100, 22, 16)
        self.rect.center = self.pos
        self.sprite = tileset['ogre']
        self.id = id
        self.OFFSET_X = 5
        self.OFFSET_Y = 14

    def sprite_info(self):
        return {
            'id': self.id,
            'pos': ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y ),
            'sprite': self.sprite,
            'z-index': self.rect.bottom
        }