import pygame, random
from pygame import mixer
from sprite_map import tileset

mixer.init()
outch_sound = pygame.mixer.Sound("assets\sounds\sm64_whomp.wav")
death_sound = pygame.mixer.Sound("assets\sounds\ogre_destroyy.wav")
outch_sound.set_volume(0.3)
death_sound.set_volume(0.4)

# cette fonction renvoie un vecteur type (a,b) ou a et b ne peuvent avoir que les valeurs -1, 0 ou 1.
def get_target_direction(self_rect:pygame.Rect,target_rect:pygame.Rect):
    direction = [target_rect.center[i] - self_rect.center[i] for i in range(2)]
    if abs(direction[0]) < 1/3 * abs(direction[1]) : direction[0] = 0
    if abs(direction[1]) < 1/3 * abs(direction[0]) : direction[1] = 0
    for i in (0,1) :
        if direction[i] == 0 : continue
        else : direction[i] = direction[i] / abs(direction[i])
    return direction

SCORE = pygame.USEREVENT + 2

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
        self.life = 3
        self.MAX_SPEED = 0.4 + random.choice(range(3))/10

        # behaviour
        self.charge_rect = pygame.Rect(-100, -100, 108, 108)
        self.slam_rect = pygame.Rect(-100, -100, 32, 32)
        self.state = 'normal'
        self.hurt_timer = 0
        self.charge_timer = 0
        self.slam_timer = 0
        self.max_speed = self.MAX_SPEED
        self.destroy = False
        self.wiggle = 2

    def update(self):
        for i in range(2): self.pos[i] += self.speed[i]
        self.rect.center = (self.pos[0], self.pos[1])
        self.charge_rect.center = (self.pos[0], self.pos[1])
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )

        # reset state
        if self.hurt_timer == 0 \
        and self.charge_timer == 0 \
        and self.slam_timer == 0 : 
            self.state = 'normal'
            self.sprite = tileset['ogre']
            self.max_speed = self.MAX_SPEED
        # damage
        elif self.hurt_timer > 0 :
            self.hurt_timer -= 1
            if self.hurt_timer %10==0 : self.pos[0] -= self.wiggle
            elif self.hurt_timer %5==0: self.pos[0] += self.wiggle
            # destroy
            if self.destroy and self.hurt_timer == 1 : self.state = 'removed'
            if self.destroy and self.hurt_timer %2==0:
                self.sprite[3] -= 1
        # slam
        elif self.slam_timer > 0 :
            self.slam_timer -= 1
            if self.slam_timer %10==0 : self.pos[1] -=2
            elif self.slam_timer %5==0: self.pos[1] +=2
        # charge
        elif self.charge_timer > 0 :
            self.charge_timer -= 1

    def move(self, target):
        ACCEL = 0.2
        dir = get_target_direction(self.rect,target.rect)
        for i in range(2): self.speed[i] += ACCEL*dir[i]
        for i,x in enumerate(self.speed):
            if x >= self.max_speed: self.speed[i] = self.max_speed
            if x <= -self.max_speed: self.speed[i] = -self.max_speed

    def charge(self):
        self.state = 'charging'
        self.sprite = tileset['ogre_charge']
        self.max_speed = 1.2
        self.charge_timer = 90

    def slam(self, target):
        self.charge_timer = 0
        self.speed = [0,0]
        self.state = 'slamming'
        self.sprite = tileset['ogre_slam']
        self.slam_timer = 24
        self.slam_rect.center = self.rect.center
        if self.slam_rect.colliderect(target.rect) :
            target.damage()

    def damage(self, dir):
        self.speed = [x/5 for x in dir]
        self.state = 'hurting'
        self.hurt_timer = 42
        self.charge_timer = 0
        self.sprite = tileset['ogre_hit']
        self.life -= 1
        pygame.event.post(pygame.event.Event(SCORE,{'value': 4-self.life, 'style': 'score'}))
        pygame.mixer.Sound.play(outch_sound)
        if self.life < 1 :
            pygame.mixer.Sound.play(death_sound)
            self.wiggle = 4
            self.speed = [0,0]
            self.sprite = [x for x in self.sprite]
            self.hurt_timer = 64
            self.destroy = True
            