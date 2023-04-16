import pygame, random
import asyncio 
from pygame import mixer
from sys import exit
# import ctypes
# ctypes.windll.user32.SetProcessDPIAware()

from sprite_map import tileset
from conf import GAME_HEIGHT, GAME_SCALE, GAME_SPEED, GAME_WIDTH, MULTI_RESET
import player as player
import structures as struct
import ennemies as ennemies
import objects as objects
import menu as menu


#–––––––––––––––––––––#
### FONCTIONS ###
#–––––––––––––––––––––#

def get_z(obj):
    return obj.rect.bottom

def isNear(a,b,sensibility):
    return a-b >= -sensibility and a-b <= sensibility

def get_solid_objects(list) -> list:
    solid_objects = [obj.rect for obj in list if obj.solid]
    return solid_objects


class Game:
    def __init__(self, player, tiles):
        #score
        self.score = 0
        self.multi = 1
        self.multi_reset_timer = 0
        #ogres
        self.object_list = []
        self.effect_list = []
        self.shuriken_list = []
        #background
        self.background = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
        for x in range(15):
            for y in range(10):
                style = random.choice(['grass1','grass2'])
                self.background.blit(tiles, (32*x,32*y), tileset[style])
        #decor
        self.spawn_bamboos()
        self.spawn_plants(28)
        self.object_list.append(struct.Shrine((240,160)))
        #actors
        self.spawn_locations = [(96,112),(380,212)]
        self.object_list.append(ennemies.Ogre(random.choice(self.spawn_locations)))
        self.spawn_timer = 250 + random.choice(range(500))
        self.object_list.append(player)

    def spawn_bamboos(self):
        bamboo_positions = [(64,64),(84,84),(416,264),(396,244)]
        for pos in (bamboo_positions):
            bamboo = struct.Bamboo(pos)
            self.object_list.append(bamboo)

    def spawn_plants(self, number):
        random_plant_positions = [
            (random.choice(range(32,448,16)),random.choice(range(32,288,16)))
            for i in range(number)
        ]
        for pos in random_plant_positions:
            self.object_list.append(struct.Plant(pos))


async def main() :

    #–––––––––––––––––––––#
    ### INITIALISATIONS ###
    #–––––––––––––––––––––#

    pygame.init()
    mixer.init()
    pygame.display.set_caption('Ninjapy')
    clock = pygame.time.Clock()
    win = pygame.display.set_mode((GAME_WIDTH * GAME_SCALE,GAME_HEIGHT * GAME_SCALE))
    screen = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    last_arrow = None
    screen_position = [0,0]
    game_frames = 0
    screenshake_timer = 0
    screenshake_frequency = 2
    screenshake_intensity = 4

    ## MENU
    menu_background = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    menu_background.fill('#323c39')
    game_over_bg = pygame.Surface((GAME_WIDTH, GAME_HEIGHT-128))
    game_over_bg.fill('burlywood4')
    game_over_bg.set_alpha(1)

    ## SOUNDS
    menu_confirm = pygame.mixer.Sound("assets/sounds2/dash2.ogg")
    menu_confirm.set_volume(0.4)

    ## MUSICS
    menu_music = 'assets/sounds2/AnyConv.com__menu_music.ogg'
    game_music = 'assets/sounds2/I_Want_To_Be_Neenja.ogg'

    ## GRAPHICS
    menu_title_art = pygame.image.load('assets/title_back.png').convert_alpha()
    menu_ogre = pygame.image.load('assets/title_ogre.png').convert_alpha()
    menu_texts = pygame.image.load('assets/title_texts.png').convert_alpha()
    menu_contols = pygame.image.load('assets/controls.png').convert_alpha()
    tiles = pygame.image.load('assets/tiles.png').convert_alpha()
    game_over_splash = pygame.image.load('assets/game_over.png').convert_alpha()

    ## INTERFACE
    # score
    score_font = pygame.font.Font('assets/kloudt.regular.otf', 24)
    multi_font = pygame.font.Font('assets/kloudt.regular.otf', 16)
    score_back_rect = pygame.Rect(0,0,96,32)
    score_back_rect.topright = (480,0)
    # health
    health_rect = pygame.Rect(0,0,80,16)
    flower_rects = [ pygame.Rect(16 + x*16, 0, 16, 16) for x in range(4) ]
    # ammo
    belt_rect = pygame.Rect(0,16,80,16)
    ammo_rects = [ pygame.Rect(12 + x*11, 16, 16, 16) for x in range(5) ]

    ## SIGNALS
    PLAYER_HURT = pygame.USEREVENT + 0
    CREATE_PICKUP = pygame.USEREVENT + 1
    SCORE = pygame.USEREVENT + 2

    ## Generating menu
    is_in_menu = True
    is_in_game_over = False
    main_menu = menu.Menu(True)

    ## Launch Music
    main_menu.play_music(menu_music)


    #–––––––––––––––#
    ### MAIN LOOP ###
    #–––––––––––––––#

    while True:
    ## MENU
        if is_in_menu :
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP: main_menu.go_up()
                        
                    if event.key == pygame.K_DOWN: main_menu.go_down()
                    if event.key in [pygame.K_RETURN,pygame.K_x]  :
                        if main_menu.state == 'play':
                            main_menu.play_music(game_music)
                            pygame.mixer.Sound.play(menu_confirm)
                            hero = player.Player([240,180])
                            game = Game(hero, tiles)
                            is_in_menu = False
                        if main_menu.state == 'music':
                            main_menu.switch_music_on()
                            main_menu.play_music(menu_music)
                        if main_menu.state == 'controls':
                            main_menu.show_controls = not main_menu.show_controls

            # menu behavior
            if main_menu.title_pos[1] < 5 : main_menu.title_pos[1] += 3
            main_menu.ogre_peek()
            main_menu.ogre_blink()
            main_menu.update()

            # draw menu
            screen.blit(menu_background, (0,0))
            screen.blit(menu_ogre, main_menu.ogre_pos, main_menu.ogre_sprite)
            screen.blit(menu_title_art, (0,0))
            screen.blit(main_menu.title_back, main_menu.title_pos)
            for spr in main_menu.title_sprites :
                screen.blit(menu_texts, spr['pos'], spr['sprite'])
            for spr in main_menu.menu_sprites :
                screen.blit(menu_texts, spr['rect'], spr['sprite'])
            screen.blit(menu_texts, main_menu.arrow_pos, main_menu.arrow_sprite)
            screen.blit(menu_texts, main_menu.on_off_pos, main_menu.on_off_sprite)
            if main_menu.show_controls : 
                screen.blit(menu_contols, main_menu.controls_pos)

    ## GAME OVER
        elif is_in_game_over :
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        # del game, hero
                        hero = player.Player([240,180])
                        game = Game(hero, tiles)
                        is_in_game_over = False
                    if event.key == pygame.K_m:
                        main_menu = menu.Menu(main_menu.music_on)
                        main_menu.play_music(menu_music)
                        is_in_game_over = False
                        is_in_menu = True
            screen.blit(game_over_bg, (0,64))
            screen.blit(game_over_splash, (116,48))

    ## MAIN GAME
        else:
        ## EVENTS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == PLAYER_HURT:
                    screenshake_timer = 8
                    game.effect_list.append(objects.Petal(hero.rect.center))
                    game.effect_list.append(objects.Petal(hero.rect.center, True))
                if event.type == SCORE:
                    if event.style == 'multi':
                        game.multi += event.value
                        game.multi_reset_timer = MULTI_RESET
                    else : game.score += event.value * game.multi
                if event.type == CREATE_PICKUP:
                    game.object_list.append(objects.Pickup(event.pos, event.style))
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        hero.shoot(game.shuriken_list)       
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        if last_arrow == event.key \
                        and game_frames - hero.input_dash_timer <= hero.DASH_DOUBLE_TAP_WINDOW:
                            hero.dash(event.key)
                            
                        last_arrow = event.key
                        hero.input_dash_timer = game_frames

        ## ENTITIES BEHAVIOUR

            # player
            if hero.health == 0 : is_in_game_over = True
            sol_obj = get_solid_objects(game.object_list)
            if hero.state == 'normal': hero.control_movement()
            if hero.state == 'dashing': hero.bounce(sol_obj)
            else : hero.collide(sol_obj)
            hero.warp()
            hero.update()

            # ogres
            ogres = [obj for obj in game.object_list if type(obj) == ennemies.Ogre]
            for ogre in ogres:

                if ogre.charge_rect.colliderect(hero.rect) and ogre.state == 'normal': 
                    ogre.charge()
                if ogre.state == 'charging' and ogre.rect.colliderect(hero.rect) \
                or ogre.charge_timer == 1:
                    ogre.slam(hero)
                    game.effect_list.append(objects.OgreSlam(ogre.rect.midbottom))
                if ogre.state not in ['hurting', 'slamming'] : ogre.move(hero)

                ogre.update()
                if ogre.state == 'removed' : game.object_list.remove(ogre)

            # spawn
            if len(ogres) == 0 : game.spawn_timer -= 10
            else : game.spawn_timer -= 1
            if len(ogres) < 5 and game.spawn_timer < 0 :
                game.object_list.append(ennemies.Ogre(random.choice(game.spawn_locations)))
                game.spawn_timer = 750 - (game.score*3) + random.choice(range(500))

            #pickups
            for pickup in [obj for obj in game.object_list if type(obj) == objects.Pickup]:
                if pickup.rect.colliderect(hero.rect):
                    pickup.get_pickedup(hero)
                if pickup.removable : game.object_list.remove(pickup)

            # shuriken
            for shuriken in game.shuriken_list:
                shuriken.activate(hero.rect)
                shuriken.warp()
                if shuriken.state != 'pickup' : shuriken.animate()
                for obj in game.object_list:
                    if shuriken.rect.colliderect(obj.rect) and shuriken.state == 'active' :
                        shuriken.collide(obj)
                shuriken.update()
                if shuriken.state == 'removed' : game.shuriken_list.remove(shuriken)

            # effects
            for effect in game.effect_list :
                effect.update()
                if effect.stay_on_background : game.background.blit(tiles, effect.rect, effect.sprite)
                if effect.remove : game.effect_list.remove(effect)


        ## DRAWING BACKGROUND
            screen.blit(game.background, (0,0))

        # effects on bottom
            for effect in game.effect_list:
                if effect.on_bottom : screen.blit(tiles, effect.rect, effect.sprite)

        ## DRAWING ENTITIES
            game.object_list.sort(key=get_z)
            for obj in game.object_list:
                screen.blit(tiles, obj.sprite_pos, obj.sprite)

            for shuriken in game.shuriken_list:
                screen.blit(tiles, shuriken.sprite_pos, shuriken.sprite)

            # effects on bottom
            for effect in game.effect_list:
                if not effect.on_bottom : screen.blit(tiles, effect.rect, effect.sprite)

        ## DRAWING DEBUG INFO
            ## SHOW HITBOXES
            # for o in game.object_list :
            #     if type(o) == ennemies.Ogre : pygame.draw.rect(screen, 'white', o, 1)
            # for s in game.shuriken_list :
            #     pygame.draw.rect(screen, 'white', s, 1)
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
            screen.blit(tiles, score_back_rect, tileset['score_back'])
            score_message = score_font.render(str(game.score), False, 'orangered3')
            score_message_rect = score_message.get_rect()
            score_message_rect.topright = (score_back_rect.topright[0]-10,score_back_rect.topright[1]-1)
            screen.blit(score_message, score_message_rect)
            #multiplier
            if game.multi > 1 :
                game.multi_reset_timer -= 1
                if game.multi_reset_timer == 0 : game.multi = 1
                multi_message = multi_font.render(str(f'x{game.multi}'), False, 'orangered3')
                multi_message_rect = multi_message.get_rect()
                multi_message_rect.topleft = (400,4)
                screen.blit(multi_message, multi_message_rect)
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
        await asyncio.sleep(0)

asyncio.run(main())

