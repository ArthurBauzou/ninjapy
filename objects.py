import pygame, random
from pygame import mixer

from sprite_map import tileset
from conf import GAME_HEIGHT, GAME_WIDTH

import ennemies
import structures
import player

mixer.init()
catch_sound = pygame.mixer.Sound("assets/sounds/bling.wav")
pickup_sound = pygame.mixer.Sound("assets/sounds/step.wav")
catch_sound.set_volume(0.4)
pickup_sound.set_volume(0.3)

SHURIKEN_DROP = pygame.USEREVENT + 1
SCORE = pygame.USEREVENT + 2


class Shuriken:
    def __init__(self, pos, speed):
        self.pos = [x for x in pos]
        self.speed = speed
        self.rect = pygame.Rect(-100, -100, 8, 8)
        self.rect.center = self.pos
        self.sprite = tileset['shuriken1']
        self.state = 'inactive'
        self.anim_timer = 0

    def warp(self):
        if self.rect.center[0] > GAME_WIDTH: self.pos[0] = 0
        if self.rect.center[0] < 0: self.pos[0] = GAME_WIDTH
        if self.rect.center[1] < 0: self.pos[1] = GAME_HEIGHT
        if self.rect.center[1] > GAME_HEIGHT: self.pos[1] = 0

    def activate(self, h_rect) :
        if self.state == 'inactive' and self.rect.colliderect(h_rect) == False :
            self.state = 'active'

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

    def update(self):
        if self.state == 'bouncing':
            if self.speed[1] < 1 : self.speed[1] +=0.1
            else : self.become_pickup()
            
        for i in range(2): self.pos[i] += self.speed[i]
        self.rect.center = (self.pos[0], self.pos[1])

    def collide(self, target, list):
        if type(target) == player.Player:

            if target.state == 'dashing' :
                self.state = 'removed'
                pygame.event.post(pygame.event.Event(SCORE,{'value': 1, 'style': 'multi'}))
                pygame.mixer.Sound.play(catch_sound)
                if target.ammo <= 5 : target.ammo += 1

            if target.state == 'normal' :
                self.bounce(target)
                target.damage()

        if type(target) == ennemies.Ogre and target.state != 'hurting':
            target.damage(self.speed)
            self.bounce(target)

        if type(target) == structures.Shrine:
            self.bounce(target)

    def bounce(self, target):
        BOUNCE_X_SPEED = 0.5
        BOUNCE_Y_SPEED = -1.2
        self.state = 'bouncing'
        self.speed = [0,0]
        if self.rect.center[0] > target.rect.center[0] : self.speed[0] = BOUNCE_X_SPEED
        else : self.speed[0] = -BOUNCE_X_SPEED
        self.speed[1] = BOUNCE_Y_SPEED

    def become_pickup(self):
        pygame.event.post(pygame.event.Event(SHURIKEN_DROP,{'pos': self.pos, 'style': 'shuriken'}))
        self.state = 'removed'

class Pickup:
    def __init__(self, pos, style):
        self.pos = [x for x in pos]
        self.rect = pygame.Rect(-100, -100, 8, 8)
        self.rect.center = self.pos
        self.style = style
        if self.style == 'shuriken':
            self.sprite = random.choice([tileset['shuriken_sol_1'],tileset['shuriken_sol_2']])
        self.solid = False
        self.sprite_pos = self.pos
        self.removable = False

    def get_pickedup(self, hero):
        if self.style == 'shuriken':
            pygame.mixer.Sound.play(pickup_sound)
            if hero.ammo < 5 : hero.ammo += 1
        self.removable = True

class OgreSlam:
    def __init__(self, pos):
        self.pos = [x for x in pos]
        self.rect = pygame.Rect(-100, -100, 32, 32)
        self.rect.center = self.pos
        self.sprite = tileset('slam1')