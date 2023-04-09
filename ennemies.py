import pygame
from sprite_map import tileset

# cette fonction renvoie un vecteur type (a,b) ou a et b ne peuvent avoir que les valeurs -1, 0 ou 1.
def get_target_direction(self_rect:pygame.Rect,target_rect:pygame.Rect):
    direction = [target_rect.center[i] - self_rect.center[i] for i in range(2)]
    if abs(direction[0]) < 1/3 * abs(direction[1]) : direction[0] = 0
    if abs(direction[1]) < 1/3 * abs(direction[0]) : direction[1] = 0
    for i in (0,1) :
        if direction[i] == 0 : continue
        else : direction[i] = direction[i] / abs(direction[i])
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
        self.hurt_timer = 0

    def update(self):
        for i in range(2): self.pos[i] += self.speed[i]
        self.rect.center = (self.pos[0], self.pos[1])
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )

        # reset state
        if self.hurt_timer == 0 : 
            self.state = 'normal'
            self.sprite = tileset['ogre']
        # damage
        elif self.hurt_timer > 0 :
            self.hurt_timer -= 1
            if self.hurt_timer %6==0 : self.pos[1] -=2
            elif self.hurt_timer %3==0: self.pos[1] +=2


    def move_random(self):
        pass

    def move(self, target):
        ACCEL = 0.5
        MAX_SPEED = 0.8
        dir = get_target_direction(self.rect,target.rect)
        for i in range(2): self.speed[i] += ACCEL*dir[i]
        for i,x in enumerate(self.speed):
            if x >= MAX_SPEED: self.speed[i] = MAX_SPEED
            if x <= -MAX_SPEED: self.speed[i] = -MAX_SPEED

    def damage(self):
        self.state = 'hurting'
        self.hurt_timer = 24
        self.sprite = tileset['ogre_hit']
        self.speed = [x/10 for x in self.speed]
        print('Ogre is damaged')