import pygame
import asyncio 
from pygame import mixer
from sys import exit
# import ctypes
# ctypes.windll.user32.SetProcessDPIAware()

from sprite_map import tileset
from conf import GAME_HEIGHT, GAME_SCALE, GAME_SPEED, GAME_WIDTH, MULTI_RESET, MAX_KAPPAS, MAX_OGRES
import player as player
import structures as struct
import ennemies as ennemies
import objects as objects
import menu as menu
import game as level


#–––––––––––––––––––––#
### FONCTIONS ###
#–––––––––––––––––––––#

def get_z(obj):
    return obj.rect.bottom

def isNear(a,b,sensibility):
    return a-b >= -sensibility and a-b <= sensibility

def get_solid_objects(list, minus_bamboos = False) -> list[pygame.Rect]:
    if minus_bamboos : solid_objects = [obj.rect for obj in list if obj.solid and type(obj)!=struct.Bamboo]
    else : solid_objects = [obj.rect for obj in list if obj.solid]
    return solid_objects


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
    screenshake_intensity = 0

    ## MENU
    menu_background = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    menu_background.fill('#323c39')
    menu_transition = pygame.Surface((GAME_WIDTH,GAME_HEIGHT))
    menu_transition.fill('black')

    ## SOUNDS
    menu_confirm = pygame.mixer.Sound("assets/sounds2/letsgo.ogg")
    menu_confirm.set_volume(0.4)

    ## MUSICS
    menu_music = 'assets/sounds2/AnyConv.com__menu_music.ogg'
    game_music = 'assets/sounds2/I_Want_To_Be_Neenja_2.ogg'

    ## GRAPHICS
    menu_title_art = pygame.image.load('assets/title_back.png').convert_alpha()
    menu_ogre = pygame.image.load('assets/title_ogre.png').convert_alpha()
    menu_texts = pygame.image.load('assets/title_texts.png').convert_alpha()
    menu_contols = pygame.image.load('assets/controls.png').convert_alpha()
    tiles = pygame.image.load('assets/tiles.png').convert_alpha()
    game_over_splash = pygame.image.load('assets/game_over.png').convert_alpha()
    game_over_shuriken = pygame.image.load('assets/game_over_shuriken.png').convert_alpha()
    fond_score = pygame.image.load('assets/fond_score.png').convert_alpha()

    ## INTERFACE
    # score
    score_font = pygame.font.Font('assets/kloudt.regular.otf', 24)
    big_score_font = pygame.font.Font('assets/kloudt.regular.otf', 48)
    multi_font = pygame.font.Font('assets/kloudt.regular.otf', 16)
    score_back_rect = pygame.Rect(0,0,96,32)
    score_back_rect.topright = (480,0)
    multi_timer_rect = pygame.Rect(390,20,32,4)
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
    go_menu = menu.GameOverMenu(0)

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
                if event.type == pygame.KEYDOWN and main_menu.active:
                    if event.key == pygame.K_UP: main_menu.go_up()
                    if event.key == pygame.K_DOWN: main_menu.go_down()
                    if event.key in [pygame.K_RETURN,pygame.K_x]  :
                        if main_menu.state == 'play':
                            main_menu.start_transition()
                            main_menu.active = False
                            pygame.mixer.Sound.play(menu_confirm)
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

            if main_menu.transition == 'done' and main_menu.state == 'play' :
                main_menu.play_music(game_music)
                hero = player.Player([240,180])
                game = level.Game(hero, tiles)
                is_in_menu = False

            # DRAW MENU
            #back
            screen.blit(menu_background, (0,0))
            screen.blit(menu_ogre, main_menu.ogre_pos, main_menu.ogre_sprite)
            screen.blit(menu_title_art, (0,0))
            #title
            screen.blit(main_menu.title_back, main_menu.title_pos)
            for spr in main_menu.title_sprites :
                screen.blit(menu_texts, spr['pos'], spr['sprite'])
            #menu
            for spr in main_menu.menu_sprites :
                screen.blit(menu_texts, spr['rect'], spr['sprite'])
            screen.blit(menu_texts, main_menu.arrow_pos, main_menu.arrow_sprite)
            screen.blit(menu_texts, main_menu.on_off_pos, main_menu.on_off_sprite)
            if main_menu.show_controls : 
                screen.blit(menu_contols, main_menu.controls_pos)
            
            if main_menu.transition == 'fading' :
                    menu_transition.set_alpha(255-(main_menu.timer*255/main_menu.FADE_TIME))
                    screen.blit(menu_transition, (0,0))

    ## GAME OVER
        elif is_in_game_over :
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN :
                    if (event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT) and go_menu.score_is_loaded:
                        go_menu.switch_choice()
                    if event.key == pygame.K_x and not go_menu.score_is_loaded :
                        go_menu.score = go_menu.MAX_SCORE-2
                        go_menu.rank_index = int(go_menu.score/80)
                        if go_menu.rank_index > 6 : go_menu.rank_index = 6
                    if event.key == pygame.K_x and go_menu.score_is_loaded :
                        if go_menu.choice == 'retry' :
                            # retry
                            hero = player.Player([240,180])
                            game = level.Game(hero, tiles)
                            is_in_game_over = False
                        else : 
                            # return to menu
                            main_menu = menu.Menu(main_menu.music_on)
                            main_menu.play_music(menu_music)
                            is_in_game_over = False
                            is_in_menu = True

            #UPDATE
            go_menu.update()

            # DRAW
            screen.blit(go_menu.bg, (0, 0))
            screen.blit(tiles, go_menu.hero['pos'], go_menu.hero['sprite'])
            if go_menu.active :
                screen.blit(game_over_splash, go_menu.head_pos['text'])
                screen.blit(game_over_shuriken, go_menu.head_pos['shuriken'])
                screen.blit(fond_score, go_menu.score_pos)
                #score
                score_message = big_score_font.render(str(go_menu.score), False, 'firebrick')
                score_message_rect = score_message.get_rect()
                score_message_rect.center = (240,go_menu.score_pos[1]+50)
                #rank
                rank_message = score_font.render(go_menu.rank_list[go_menu.rank_index], False, 'firebrick')
                rank_message_rect = rank_message.get_rect()
                rank_message_rect.center = (240,go_menu.score_pos[1]+96)
                screen.blit(score_message, score_message_rect)
                screen.blit(rank_message, rank_message_rect)
            #menu
            if go_menu.score_is_loaded :
                pygame.draw.rect(screen, 'firebrick', go_menu.menu_rect, 0, 3)
                screen.blit(menu_texts, (148,go_menu.MENU_Y), go_menu.retry_sprite)
                screen.blit(menu_texts, (288,go_menu.MENU_Y), go_menu.menu_sprite)
                if go_menu.choice == 'retry' : screen.blit(menu_texts, (116, go_menu.MENU_Y), go_menu.arrow_sprite)
                else : screen.blit(menu_texts, (256, go_menu.MENU_Y), go_menu.arrow_sprite)

    ## MAIN GAME
        else:
        ## EVENTS
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == PLAYER_HURT:

                        screenshake_timer = event.timer
                        screenshake_intensity = event.intensity
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

            sol_obj = get_solid_objects(game.object_list)

            # player
            if hero.health == 0 : 
                go_menu = menu.GameOverMenu(game.score, hero)
                is_in_game_over = True
            if hero.state == 'normal': hero.control_movement()
            if hero.state == 'dashing': hero.bounce(sol_obj)
            else : hero.collide(sol_obj)
            hero.warp()
            hero.update()

            # objects
            game.kappa_count = 0
            game.ogre_count = 0

            for o in game.object_list :
                if type(o) == ennemies.Ogre:
                    game.ogre_count += 1
                    ogre = o
                    if ogre.state in ['normal', 'charging'] : ogre.follow_target(hero)
                    if ogre.charge_rect.colliderect(hero.rect) and ogre.state == 'normal': ogre.charge()
                    if ogre.state == 'charging' and ( ogre.rect.colliderect(hero.rect) or ogre.timer == 0 ): 
                        ogre.slam(game.object_list)
                        game.effect_list.append(objects.OgreSlam(ogre.rect.midbottom))
                    ogre.collide(game.shrine.rect)
                    ogre.update()
                    if ogre.state == 'removed' : game.object_list.remove(o)

                if type(o) == ennemies.Kappa :
                    game.kappa_count += 1
                    kappa = o
                    if kappa.attack_rect.colliderect(hero.rect) and kappa.state == 'normal': kappa.attack(hero)
                    if kappa.rect.colliderect(hero.rect) and kappa.state == 'attacking':
                        hero.damage(kappa.speed)
                        kappa.chill()
                        kappa.max_speed -= 0.05
                    kappa.collide(game.shrine.rect)
                    kappa.update()
                    kappa.warp()
                    if kappa.state == 'removed' : game.object_list.remove(o)

                if type(o) == objects.Pickup :
                    pickup = o
                    if pickup.rect.colliderect(hero.rect): pickup.get_pickedup(hero)
                    pickup.get_out_dead_zone(game.dead_zone_list)
                    if pickup.removable : game.object_list.remove(pickup)
        
            # shuriken
            for shuriken in game.shuriken_list:
                shuriken.activate(hero.rect)
                shuriken.warp()
                if shuriken.state != 'pickup' : shuriken.animate()
                for obj in game.object_list:
                    if shuriken.rect.colliderect(obj.rect) :
                        shuriken.collide(obj)
                shuriken.update()
                if shuriken.state == 'removed' : game.shuriken_list.remove(shuriken)

            # effects
            for effect in game.effect_list :
                effect.update()
                if effect.stay_on_background : game.background.blit(tiles, effect.rect, effect.sprite)
                if effect.remove : game.effect_list.remove(effect)

            # monster spawn
            if game.kappa_count < MAX_KAPPAS : game.spawn_kappa()
            if game.ogre_count < MAX_OGRES : game.spawn_ogre()

        ## DRAW GAME
            #background
            screen.blit(game.background, (0,0))
            #effects on bottom
            for effect in game.effect_list:
                if effect.on_bottom : screen.blit(tiles, effect.rect, effect.sprite)
            #objects
            game.object_list.sort(key=get_z)
            for obj in game.object_list:
                screen.blit(tiles, obj.sprite_pos, obj.sprite)
            for shuriken in game.shuriken_list:
                screen.blit(tiles, shuriken.sprite_pos, shuriken.sprite)
            #effects on top
            for effect in game.effect_list:
                if not effect.on_bottom : screen.blit(tiles, effect.rect, effect.sprite)

        ## DRAWING DEBUG INFO
            ## SHOW HITBOXES
            # for o in game.object_list :
            #     if type(o) == ennemies.Ogre : pygame.draw.rect(screen, 'white', o, 1)
            # for s in game.shuriken_list :
            #     pygame.draw.rect(screen, 'white', s, 1)
            # pygame.draw.rect(screen, 'white', hero.rect, 1)
            # for o in game.object_list :
            #     if type(o) == struct.Bamboo : pygame.draw.rect(screen, 'white', o, 1)
            #     if type(o) == struct.Shrine : pygame.draw.rect(screen, 'white', o, 1)
            # for s in game.dead_zone_list :
            #     pygame.draw.rect(screen, 'red', s['rect'], 1)

        ## DRAW INTERFACE
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
                # multi timer
                if game.multi_reset_timer > 0 :
                    multi_timer_rect.width = game.multi_reset_timer * 32/MULTI_RESET
                pygame.draw.rect(screen, 'orangered3', multi_timer_rect)
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

        #screenshake
        if screenshake_timer > 0:
            if screenshake_timer % screenshake_frequency == 0 : screen_position[0] += screenshake_intensity
            else : screen_position[0] -= screenshake_intensity
            screenshake_timer -= 1
        else : screen_position = [0,0]

    ## FINALISE DRAW : apply scale, update, control framerate
        win.blit(pygame.transform.scale(screen, win.get_rect().size), screen_position)
        pygame.display.update()
        clock.tick(GAME_SPEED)
        game_frames += 1
        await asyncio.sleep(0)

asyncio.run(main())

