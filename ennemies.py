import pygame
from sprite_map import tileset

def get_target_direction(self_rect:pygame.Rect,target:pygame.Rect):
    direction = [target.center[i] - self_rect.center[i] for i in range(2)]
    return direction

class Kappa:
    def __init__(self, pos):
        self.pos = [x for x in pos]
        self.speed = [0,0]
        self.rect = pygame.Rect(-100, -100, 15, 12)
        self.rect.center = self.pos
        self.sprite = tileset['kappa']
        self.OFFSET_X = 8
        self.OFFSET_Y = 16
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )
        self.solid = True

    def update(self):
        for i in range(2): self.pos[i] += self.speed[i]
        self.rect.center = (self.pos[0], self.pos[1])
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )
    
class Ogre:
    def __init__(self, pos):
        self.pos = [x for x in pos]
        self.speed = [0,0]
        self.rect = pygame.Rect(-100, -100, 22, 16)
        self.rect.center = self.pos
        self.sprite = tileset['ogre']
        self.OFFSET_X = 5
        self.OFFSET_Y = 14
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )
        self.solid = True

        # behaviour
        self.state = 'normal'
        self.MAX_SPEED = 0.5

    def update(self):
        for i in range(2): self.pos[i] += self.speed[i]
        self.rect.center = (self.pos[0], self.pos[1])
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )

    def move(self, target:pygame.Rect):
        # ACCEL = 2
        self.speed = [get_target_direction(self.rect, target)[i]/50 for i in (0,1)]
        for i,x in enumerate(self.speed):
            if x >= self.MAX_SPEED: self.speed[i] = self.MAX_SPEED
            if x <= -self.MAX_SPEED: self.speed[i] = -self.MAX_SPEED

    def damage(self):
        print('Ogre is damaged')