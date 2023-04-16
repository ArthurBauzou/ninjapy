import pygame
import random
from pygame import mixer

from sprite_map import tileset
import objects as objects
from conf import GAME_WIDTH, GAME_HEIGHT

## SOUNDS
mixer.init()
dash_sound = pygame.mixer.Sound("assets/sounds2/dash2.ogg")
shoot_sound = pygame.mixer.Sound("assets/sounds2/shuriken.ogg")
hurt_sound = pygame.mixer.Sound("assets/sounds2/AnyConv.com__hurt.ogg")
bounce_sound = pygame.mixer.Sound("assets/sounds2/AnyConv.com__bounce.ogg")
dash_sound.set_volume(0.3)
shoot_sound.set_volume(0.3)
hurt_sound.set_volume(0.8)
bounce_sound.set_volume(0.2)


## FUNCTIONS
def isNear(a,b,sensibility):
    return a-b >= -sensibility and a-b <= sensibility

global_directions = {
    pygame.K_RIGHT: (1,0),
    pygame.K_LEFT: (-1,0),
    pygame.K_DOWN: (0,1),
    pygame.K_UP: (0,-1),
}

PLAYER_HURT = pygame.USEREVENT + 0

## CLASS
class Player:
    def __init__(self, pos) -> None:
        # INI
        self.pos = [x for x in pos]
        self.rect = pygame.Rect(-100, -100, 16, 16)
        self.rect.center = self.pos
        self.sprite = tileset['ninja']
        self.OFFSET_X = 8
        self.OFFSET_Y = 12
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )
        self.state = 'normal'
        self.solid = True
        # HEALTH
        self.health = 3
        self.hurt_timer = 0
        # MOVEMENT
        self.speed = [0,0]
        self.ACCEL = 0.35
        self.BRAKE = 0.15
        self.MAX_SPEED = 2.3
        self.STOP = 0.3
        # DASH
        self.input_dash_timer, self.dash_cooldown_timer, self.dash_timer = 0,0,0
        self.DASH_DOUBLE_TAP_WINDOW = 9
        self.DASH_ACCELERATION = 3
        # SHOOTING
        self.clumsy = 4
        self.strenght = 4
        self.ammo = 5

    def check_arrows(self):
        keys = pygame.key.get_pressed()
        r = [0,0]
        if keys[pygame.K_LEFT] : r[0] -= 1
        if keys[pygame.K_RIGHT] : r[0] += 1
        if keys[pygame.K_DOWN] : r[1] += 1
        if keys[pygame.K_UP] : r[1] -= 1
        return r

    def control_movement(self):
        # acceleration
        for i in range(2): self.speed[i] += self.ACCEL*self.check_arrows()[i]
        # braking
        for i,x in enumerate(self.speed):
            if x >= self.MAX_SPEED: self.speed[i] = self.MAX_SPEED
            if x <= -self.MAX_SPEED: self.speed[i] = -self.MAX_SPEED
            if x <= self.STOP and x >= -self.STOP :
                self.speed[i] = 0
            elif x > self.STOP:
                self.speed[i] -= self.BRAKE
            else:
                self.speed[i] += self.BRAKE

    def warp(self):
        if self.rect.center[0] > GAME_WIDTH: self.pos[0] = 0
        if self.rect.center[0] < 0: self.pos[0] = GAME_WIDTH
        if self.rect.center[1] < 0: self.pos[1] = GAME_HEIGHT
        if self.rect.center[1] > GAME_HEIGHT: self.pos[1] = 0

    def shoot(self, list):
        direction = self.check_arrows()
        if self.ammo > 0 and direction != [0,0] :
            speed = [ self.strenght*direction[i] + 
                random.choice(range(-self.clumsy,self.clumsy))/10
                for i in range(2)
                ]
            shuriken = objects.Shuriken(self.rect.center, speed)
            list.append(shuriken)
            self.ammo -= 1
            pygame.mixer.Sound.play(shoot_sound)

    def dash(self, key):
        DASH_DURATION = 24
        DASH_COOLDOWN = 64 
        if self.dash_cooldown_timer == 0 :
            self.dash_cooldown_timer = DASH_COOLDOWN
            self.dash_timer = DASH_DURATION
            self.state = 'dashing'
            self.sprite = tileset['ninja_dash']
            for i in range(2): self.speed[i] += self.DASH_ACCELERATION*global_directions[key][i]
            pygame.mixer.Sound.play(dash_sound)
    
    def update(self):
        # damage
        if self.hurt_timer > 0 :
            self.hurt_timer -= 1
            if self.hurt_timer %6==0 : self.pos[1] -=2
            elif self.hurt_timer %3==0: self.pos[1] +=2
            if self.hurt_timer == 1: self.health -= 1
        # dash
        if self.dash_timer > 0: self.dash_timer -= 1
        if self.dash_cooldown_timer > 0: self.dash_cooldown_timer -= 1
        # reset state
        if self.hurt_timer == 0 and self.dash_timer == 0: 
            self.state = 'normal'
            self.sprite = tileset['ninja']
            
        #update position
        for i in range(2): self.pos[i] += self.speed[i]
        self.rect.center = (self.pos[0], self.pos[1])
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )

    def bounce(self, list):
        BOUNCE = 4
        ACCELBOUNCE = 2
        for obj in list:
            if self.rect.colliderect(obj):
                if isNear(self.rect.left, obj.right, 3): 
                    pygame.mixer.Sound.play(bounce_sound)
                    self.speed[0] = ACCELBOUNCE
                    self.pos[0] += BOUNCE
                elif isNear(self.rect.right, obj.left, 3): 
                    pygame.mixer.Sound.play(bounce_sound)
                    self.speed[0] = - ACCELBOUNCE
                    self.pos[0] -= BOUNCE
                elif isNear(self.rect.bottom, obj.top, 3): 
                    pygame.mixer.Sound.play(bounce_sound)
                    self.speed[1] = -ACCELBOUNCE
                    self.pos[1] -= BOUNCE
                elif isNear(self.rect.top, obj.bottom, 3): 
                    pygame.mixer.Sound.play(bounce_sound)
                    self.speed[1] = ACCELBOUNCE
                    self.pos[1] += BOUNCE

    def collide(self, list):
        for obj in list:
            if self.rect.colliderect(obj):
                if isNear(self.rect.left, obj.right, 3) and self.speed[0] < 0: self.speed[0] = 0
                elif isNear(self.rect.right, obj.left, 3) and self.speed[0] > 0: self.speed[0] = 0 
                elif isNear(self.rect.bottom, obj.top, 3) and self.speed[1] > 0: self.speed[1] = 0 
                elif isNear(self.rect.top, obj.bottom, 3) and self.speed[1] < 0: self.speed[1] = 0 

    def damage(self, direction):
        HURT_COOLDOWN = 24
        self.state = 'hurting'
        self.speed = [x for x in direction]
        self.sprite = tileset['ninja_hurt']
        self.hurt_timer = HURT_COOLDOWN
        pygame.event.post(pygame.event.Event(PLAYER_HURT))
        pygame.mixer.Sound.play(hurt_sound)
