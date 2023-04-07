import pygame
import random
from sys import exit
import ctypes
ctypes.windll.user32.SetProcessDPIAware()

from sprite_map import tileset
from conf import GAME_HEIGHT, GAME_SCALE, GAME_SPEED, GAME_WIDTH
import player as player
import structures as struct
import ennemies as ennemies
import objects as objects

def get_z(obj):
    return obj.rect.bottom

def isNear(a,b,sensibility):
    return a-b >= -sensibility and a-b <= sensibility

def get_solid_objects(list) -> list:
    solid_objects = [obj.rect for obj in list if obj.solid]
    return solid_objects

def game_reset(hero, list):
    hero.ammo = 5
    hero.health = 3
    list = []


#–––––––––––––––––––––#
### INITIALISATIONS ###
#–––––––––––––––––––––#

pygame.init()
pygame.display.set_caption('Ninjapy')
clock = pygame.time.Clock()
win = pygame.display.set_mode((GAME_WIDTH * GAME_SCALE,GAME_HEIGHT * GAME_SCALE))
screen = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
last_arrow = pygame.K_SPACE
screen_position = [0,0]
game_frames = 0
# sprite_id = 0
screenshake_timer = 0

## GRAPHICS
tiles = pygame.image.load('assets/tiles.png').convert()
game_over_splash = pygame.image.load('assets/gameover.png').convert()

## INTERFACE
score = 0
myfont = pygame.font.Font('assets/kloudt.regular.otf', 24)
score_rect = pygame.Rect(0,0,96,32)
score_rect.topright = (480,0)

health_rect = pygame.Rect(0,0,80,16)
flower_rects = [ pygame.Rect(16 + x*16, 0, 16, 16) for x in range(4) ]

belt_rect = pygame.Rect(0,16,80,16)
ammo_rects = [ pygame.Rect(12 + x*11, 16, 16, 16) for x in range(5) ]

## SCREENSHAKE
screenshake_frequency = 2
screenshake_intensity = 4
screenshake_duration = 4
SCREENSHAKE = pygame.USEREVENT + 0
CREATE_PICKUP = pygame.USEREVENT + 1


#––––––––––––––––––––––#
### GENERATING LEVEL ###
#––––––––––––––––––––––#

## BACKGROUND
background = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
for x in range(15):
    for y in range(10):
        style = random.choice(['grass1','grass2'])
        background.blit(tiles, (32*x,32*y), tileset[style])

## ACTORS
shuriken_list = []
object_list = []
ogres =  []

# generating player
hero = player.Player([240,180])
object_list.append(hero)

# generating bamboos
bamboo_positions = [(64,64),(84,84),(416,264),(396,244)]
for pos in (bamboo_positions):
    bamboo = struct.Bamboo(pos)
    object_list.append(bamboo)

# generating plants
random_plant_positions = [
    (random.choice(range(32,448,16)),random.choice(range(32,288,16)))
    for i in range(28)
]
for pos in random_plant_positions:
    plant = struct.Plant(pos)
    object_list.append(plant)

# generating rock
rock = struct.Rock((240,160))
object_list.append(rock)

# generating ennemies
bads_coords = [ (96,112),(380,112),(380,212),(96,212) ]
for i in range(len(bads_coords)) :
    if i%2==0 : bad = ennemies.Kappa(bads_coords[i])
    else : bad = ennemies.Ogre(bads_coords[i])
    object_list.append(bad)


#–––––––––––––––#
### MAIN LOOP ###
#–––––––––––––––#

while True:
## GAME OVER
    if hero.health == 0 :
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game_reset(hero, shuriken_list)
        screen.blit( game_over_splash, (0,0))
## MAIN GAME
    else:
    ## EVENTS
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == SCREENSHAKE:
                screenshake_timer = 8
            if event.type == CREATE_PICKUP:
                object_list.append(objects.Pickup(event.pos, event.style))
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    hero.shoot(shuriken_list)
                if event.key == pygame.K_r:
                    game_reset(hero, shuriken_list)              
                if event.key == pygame.K_t:
                    # use for debug
                    print(shuriken_list)
                    pass
                if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                    if last_arrow == event.key \
                    and game_frames - hero.input_dash_timer <= hero.DASH_DOUBLE_TAP_WINDOW:
                        hero.dash(event.key)
                    last_arrow = event.key
                    hero.input_dash_timer = game_frames

    ## ENTITIES BEHAVIOUR

        # player
        sol_obj = get_solid_objects(object_list)
        if hero.state == 'normal': hero.control_movement()
        if hero.state == 'dashing': hero.bounce(sol_obj)
        else : hero.collide(sol_obj)
        hero.warp()
        hero.update()

        # ogres
        # ogres = [obj for obj in object_list if type(obj) == ennemies.Ogre]
        for pickup in [obj for obj in object_list if type(obj) == objects.Pickup]:
            if pickup.rect.colliderect(hero.rect):
                pickup.get_pickedup(hero)
            if pickup.removable : object_list.remove(pickup)


        # shuriken
        for shuriken in shuriken_list:
            shuriken.activate(hero.rect)
            shuriken.warp()
            if shuriken.state != 'pickup' : shuriken.animate()
            for obj in object_list:
                if shuriken.rect.colliderect(obj.rect) and shuriken.state == 'active' :
                    shuriken.collide(obj, shuriken_list)
            shuriken.update()
            if shuriken.state == 'removed' : shuriken_list.remove(shuriken)


    ## DRAWING BACKGROUND
        screen.blit(background, (0,0))

    ## DRAWING ENTITIES

        object_list.sort(key=get_z)
        for obj in object_list:
            screen.blit(tiles, obj.sprite_pos, obj.sprite)

        for shuriken in shuriken_list:
            screen.blit(tiles, shuriken.rect, shuriken.sprite)

    ## DRAWING DEBUG INFO
        # SHOW HITBOXES
        # for o in solid_objects :
        #     pygame.draw.rect(screen, 'white', o, 1)
        # pygame.draw.rect(screen, 'white', hero.rect, 1)

    ## DRAWING EFFECTS
        #screenshake
        if screenshake_timer > 0:
            if screenshake_timer % screenshake_frequency == 0 : screen_position[0] += screenshake_intensity
            else : screen_position[0] -= screenshake_intensity
            screenshake_timer -= 1
        else : screen_position = [0,0]

    ## DRAWING INTERFACE
        #score
        screen.blit(tiles, score_rect, tileset['score_back'])
        score_message = myfont.render(str(score), False, 'orangered3')
        score_message_rect = score_message.get_rect()
        score_message_rect.topright = (score_rect.topright[0]-10,score_rect.topright[1]-1)
        screen.blit(score_message, score_message_rect)
        #health
        screen.blit(tiles, health_rect, tileset['branch'])
        for n in range(hero.health):
            if n%2 == 0:
                screen.blit(tiles, flower_rects[n], tileset['health2'])
            else:
                screen.blit(tiles, flower_rects[n], tileset['health1'])
        #ammo
        screen.blit(tiles, belt_rect, tileset['belt'])
        for n in range(hero.ammo):
            screen.blit(tiles, ammo_rects[n], tileset['shuriken1'])

#apply scale, update, control framerate
    win.blit(pygame.transform.scale(screen, win.get_rect().size), screen_position)
    pygame.display.update()
    clock.tick(GAME_SPEED)
    game_frames += 1

