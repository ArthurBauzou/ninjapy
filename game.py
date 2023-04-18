import pygame, random
from typing import List

import structures as struct
import ennemies as ennemies
import objects as objects

from sprite_map import tileset
from conf import GAME_HEIGHT, GAME_WIDTH

class Game:
    def __init__(self, player, tiles):
        # score
        self.score = 0
        self.multi = 1
        self.multi_reset_timer = 0
        # lists
        self.object_list = []
        self.effect_list = []
        self.shuriken_list:List[objects.Shuriken] = []
        self.dead_zone_list = []
        # drawing background
        self.background = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        for x in range(15):
            for y in range(10):
                style = random.choice(['grass1','grass2'])
                self.background.blit(tiles, (32*x,32*y), tileset[style])
        # generating decor
        level1 = [(64,64),(84,84),(416,264),(396,244)]
        level2 = [(80,80),(400,80),(80,256),(400,256)]
        level3 = [(80,80),(240,64),(400,80),(240,264)]
        self.spawn_bamboos(random.choice([level1, level2, level3]))
        self.bamboos = [obj for obj in self.object_list if type(obj) == struct.Bamboo]
        self.spawn_plants(28)
        self.spawn_shrine()
        # additional dead zones : border
        self.dead_zone_list.append({ 'rect': pygame.Rect(-32,-32,40,GAME_HEIGHT+64), 'dir': (1,0) })
        self.dead_zone_list.append({ 'rect': pygame.Rect(GAME_WIDTH-8,-32,40,GAME_HEIGHT+64), 'dir': (-1,0) })
        self.dead_zone_list.append({ 'rect': pygame.Rect(-32,-32,GAME_WIDTH+64,40), 'dir': (0,1) })
        self.dead_zone_list.append({ 'rect': pygame.Rect(-32,GAME_HEIGHT-8,GAME_WIDTH+64,40), 'dir': (0,-1) })
        # additional dead zones : hud
        self.dead_zone_list.append({ 'rect': pygame.Rect(0,0,78,32), 'dir': (1,0) })
        self.dead_zone_list.append({ 'rect': pygame.Rect(GAME_WIDTH-90,0,90,28), 'dir': (-1,1) })
        #monsters
        self.kappa_count = 0
        self.ogre_count = 0
        self.kappa_spawn_timer = 96
        self.ogre_spawn_timer = 1600 + random.choice(range(360))
        self.kappa_spawn_bamboo = random.choice(self.bamboos)
        self.ogre_spawn_bamboo = random.choice(self.bamboos)

        #player
        self.object_list.append(player)

    def spawn_bamboos(self, list):
        for pos in (list):
            bamboo = struct.Bamboo(pos)
            self.object_list.append(bamboo)
            self.dead_zone_list.append(bamboo.get_dead_zone())

    def spawn_plants(self, number):
        random_plant_positions = [
            (random.choice(range(32,448,16)),random.choice(range(32,288,16)))
            for i in range(number)
        ]
        for pos in random_plant_positions:
            self.object_list.append(struct.Plant(pos))

    def spawn_shrine(self):
        shrine = struct.Shrine((240,160))
        self.object_list.append(shrine)
        self.dead_zone_list.append(shrine.get_dead_zone())

    def spawn_kappa(self):
        bristletime = 48
        hurryup = 11
        self.kappa_spawn_timer -= 1
        if self.kappa_count == 0 and self.kappa_spawn_timer > bristletime : self.kappa_spawn_timer -= hurryup
        if self.kappa_spawn_timer < bristletime :
            self.kappa_spawn_bamboo.bristle(self.kappa_spawn_timer, self.effect_list)
        if self.kappa_spawn_timer < 0 :
            self.object_list.append(ennemies.Kappa(self.kappa_spawn_bamboo.rect.center))
            self.kappa_spawn_timer = 750 - (self.score*4) + random.choice(range(360))
            self.kappa_spawn_bamboo = random.choice(self.bamboos)

    def spawn_ogre(self):
        bristletime = 72
        hurryup = 5
        self.ogre_spawn_timer -= 1
        if self.ogre_count == 0 and self.ogre_spawn_timer > bristletime : self.ogre_spawn_timer -= hurryup
        if self.ogre_spawn_timer < bristletime : 
            self.ogre_spawn_bamboo.bristle(self.ogre_spawn_timer, self.effect_list)
        if self.ogre_spawn_timer < 0 :
            self.object_list.append(ennemies.Ogre(self.ogre_spawn_bamboo.rect.center))
            self.ogre_spawn_timer = 1000 - (self.score*3) + random.choice(range(360))
            self.ogre_spawn_bamboo = random.choice(self.bamboos)