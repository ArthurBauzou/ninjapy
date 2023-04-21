import pygame, random
from pygame import mixer

from sprite_map import tileset
from conf import GAME_HEIGHT, GAME_WIDTH

import ennemies
import structures
import player

mixer.init()
catch_sound = pygame.mixer.Sound("assets/sounds2/shuriken_grab_3.ogg")
pickup_sound = pygame.mixer.Sound("assets/sounds2/AnyConv.com__step.ogg")
catch_sound.set_volume(0.4)
pickup_sound.set_volume(0.3)

ITEM_DROP = pygame.USEREVENT + 1
SCORE = pygame.USEREVENT + 2


class Shuriken:
    def __init__(self, pos, speed):
        self.pos = [x for x in pos]
        self.speed = speed
        self.rect = pygame.Rect(-100, -100, 12, 12)
        self.rect.center = self.pos
        self.sprite = tileset['shuriken1']
        self.OFFSET_X = 2
        self.OFFSET_Y = 2
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )
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
            if self.sprite == tileset['shuriken1']: self.sprite = tileset['shuriken2']
            else: self.sprite = tileset['shuriken1']
        else:
            self.anim_timer -= 1

    def update(self):
        if self.state == 'bouncing':
            if self.speed[1] < 1 : self.speed[1] +=0.1
            else : self.become_pickup()
            
        for i in range(2): self.pos[i] += self.speed[i]
        self.rect.center = (self.pos[0], self.pos[1])
        self.sprite_pos = ( self.rect.left - self.OFFSET_X, self.rect.top - self.OFFSET_Y )

    def collide(self, target):
        if type(target) == player.Player:

            if target.state == 'dashing' :
                if self.state == 'active' :
                    pygame.event.post(pygame.event.Event(SCORE,{'value': 1, 'style': 'multi'}))
                    pygame.mixer.Sound.play(catch_sound)
                self.state = 'removed'
                if target.ammo < 5 : target.ammo += 1

            if target.state == 'normal' and self.state == 'active':
                target.damage([x/3 for x in self.speed])
                self.bounce(target)

        if type(target) == ennemies.Ogre and target.state != 'hurting' and self.state == 'active':
            target.damage(self.speed)
            self.bounce(target)

        if type(target) == ennemies.Kappa and target.state != 'dying' and self.state == 'active':
            target.kill()
            self.bounce(target)

        if type(target) == structures.Shrine and self.state == 'active':
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
        pygame.event.post(pygame.event.Event(ITEM_DROP,{'pos': self.pos, 'style': 'shuriken'}))
        self.state = 'removed'

class Pickup:
    def __init__(self, pos, style):
        self.pos = [x for x in pos]
        self.rect = pygame.Rect(-100, -100, 16, 16)
        self.rect.center = self.pos
        self.style = style
        if self.style == 'shuriken':
            self.sprite = random.choice([tileset['shuriken_sol_1'],tileset['shuriken_sol_2']])
        if self.style == 'rice':
            self.sprite = tileset['rice_nice']
        self.solid = False
        self.sprite_pos = [x-8 for x in self.pos]
        self.removable = False

    def get_pickedup(self, hero):
        if self.style == 'shuriken':
            pygame.mixer.Sound.play(pickup_sound)
            if hero.ammo < 5 : hero.ammo += 1
        if self.style == 'rice':
            pygame.mixer.Sound.play(pickup_sound)
            if hero.health < 4 : hero.health += 1
        self.removable = True

    def get_out_dead_zone(self, list):
        SPEED = 3
        for dz in list:
            if self.rect.colliderect(dz['rect']): 
                self.pos = [self.pos[i] + SPEED*dz['dir'][i] for i in (0,1)]
                self.rect.center = self.pos
                self.sprite_pos = [x-8 for x in self.pos]

## EFFECTS

class OgreSlam:
    def __init__(self, pos):
        self.pos = [x for x in pos]
        self.rect = pygame.Rect(-100, -100, 32, 32)
        self.rect.midtop = self.pos
        self.sprite = tileset['slam1']
        self.timer = 16
        self.remove = False
        self.on_bottom = True
        self.stay_on_background = False

    def update(self):
        self.timer -= 1
        if self.timer == 8 : self.sprite = tileset['slam2']
        if self.timer <= 0 : self.remove = True


class Petal:
    def __init__(self, pos, go_left:bool = False):
        self.pos = [x for x in pos]
        self.rect = pygame.Rect(-100, -100, 8, 8)
        self.rect.center = self.pos
        self.frame_list = ['petal1', 'petal2', 'petal3', 'petal4']
        self.frame = random.choice(range(4))
        self.sprite = tileset[self.frame_list[self.frame]]
        self.timer = 32
        self.remove = False
        self.on_bottom = False
        self.stay_on_background = False
        self.falling = False
        self.speed = [
            0.5 + random.choice(range(8))/10,
            -1.5 - random.choice(range(8))/10
        ]
        if go_left : self.speed[0] = -self.speed[0]
    
    def update(self):
        self.timer -= 1
        #rise and fall
        if self.speed[1] > 0 : self.falling = True
        if not self.falling : self.speed[1] += 0.1
        else : 
            self.speed[0] = 0
            self.speed[1] += 0.01
        #animate 
        if self.timer %8 ==0 : self.animate()
        #update pos
        self.pos = [self.pos[i] + self.speed[i] for i in (0,1)]
        self.rect.center = self.pos
        #end of effect
        if self.timer == 0: 
            self.stay_on_background = True
            self.remove = True
        
    def animate(self):
        if self.frame < len(self.frame_list) - 1 : self.frame += 1
        else : self.frame = 0
        self.sprite = tileset[self.frame_list[self.frame]]


class Leaf:
    def __init__(self, pos, go_left:bool = False):
        self.pos = [x for x in pos]
        self.rect = pygame.Rect(-100, -100, 8, 8)
        self.rect.center = self.pos
        self.frame_list = ['leaf1','leaf2','leaf3','leaf4']
        self.frame = random.choice(range(4))
        self.sprite = tileset[self.frame_list[self.frame]]
        self.timer = 48
        self.remove = False
        self.on_bottom = False
        self.stay_on_background = False
        self.falling = False
        self.speed = [
            0.5 + random.choice(range(8))/10,
            -1.5 - random.choice(range(8))/10
        ]
        if go_left : self.speed[0] = -self.speed[0]
    
    def update(self):
        self.timer -= 1
        #rise and fall
        if self.speed[1] > 0 : self.falling = True
        if not self.falling : self.speed[1] += 0.1
        else : 
            self.speed[0] = 0
            self.speed[1] += 0.01
        #animate 
        if self.timer %8 ==0 : self.animate()
        #update pos
        self.pos = [self.pos[i] + self.speed[i] for i in (0,1)]
        self.rect.center = self.pos
        #end of effect
        if self.timer == 0: 
            self.remove = True
        
    def animate(self):
        if self.frame < len(self.frame_list) - 1 : self.frame += 1
        else : self.frame = 0
        self.sprite = tileset[self.frame_list[self.frame]]