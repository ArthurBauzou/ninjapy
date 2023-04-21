import pygame, random
from pygame import mixer

from sprite_map import menu_texts
from sprite_map import menu_ogre

menu_states = ['play', 'music', 'controls']

## sounds
menu_move = pygame.mixer.Sound("assets/sounds2/AnyConv.com__step.ogg")
menu_blocked = pygame.mixer.Sound("assets/sounds2/AnyConv.com__bounce.ogg")
menu_move.set_volume(0.2)
menu_blocked.set_volume(0.2)

class Menu:
    def __init__(self, music_on):
        self.state_index = 0
        self.state = 'play'
        
        # title
        self.title_back = pygame.Surface((480,80))
        self.title_back.fill('#2d3447')
        self.title_back.set_alpha(188)
        self.title_pos = [0,-64]
        self.title_sprites = [
            {'sprite':menu_texts['shuriken'], 'pos':(0,0), 'x_offset': 53},
            {'sprite':menu_texts['title'], 'pos':(0,0), 'x_offset': 133},
            {'sprite':menu_texts['shuriken'], 'pos':(0,0), 'x_offset': 357}
        ]

        # ogre
        self.ogre_sprite = menu_ogre['ogre']
        self.ogre_pos = [0,320]
        self.ogre_speed = [1+random.choice(range(5))/10,2]
        self.ogre_timer = 0
        self.blink_timer = 0
        self.ogre_direction = [1,-1]

        # menu
        self.menu_pos = [240,224]
        self.menu_sprites = [
            {'sprite':menu_texts['play'], 
             'rect': pygame.Rect(0,0,menu_texts['play'][2],menu_texts['play'][3]),
             'y_offset': 0},
            {'sprite':menu_texts['music'], 
             'rect': pygame.Rect(0,0,menu_texts['music'][2],menu_texts['music'][3]),
             'y_offset': 32},
            {'sprite':menu_texts['controls'], 
             'rect': pygame.Rect(0,0,menu_texts['controls'][2],menu_texts['controls'][3]),
             'y_offset': 64}
        ]
        for spr in self.menu_sprites :
            spr['rect'].center = (self.menu_pos[0],self.menu_pos[1]+spr['y_offset'])
        self.arrow_sprite = menu_texts['arrow']
        self.arrow_pos = (0,0)
        self.on_off_pos = (self.menu_sprites[1]['rect'].right, self.menu_sprites[1]['rect'].top)

        self.music_volume = 0.5
        self.music_on = music_on
        if music_on : self.on_off_sprite = menu_texts['on']
        else : self.on_off_sprite = menu_texts['off']

        # instructions
        self.controls_pos = (0,0)
        self.show_controls = False


    def update(self):
        self.arrow_pos = (self.menu_sprites[self.state_index]['rect'].left - 48, self.menu_sprites[self.state_index]['rect'].top)
        for spr in self.title_sprites :
            spr['pos'] = (self.title_pos[0]+spr['x_offset'],self.title_pos[1]+8)
        if self.state != 'controls' : self.show_controls == False


    def go_up(self):
        if self.state == 'play':
            pygame.mixer.Sound.play(menu_blocked)
        else : 
            pygame.mixer.Sound.play(menu_move)
            self.state_index -= 1
            if self.state == 'controls': self.show_controls = False
            self.state = menu_states[self.state_index]

    def go_down(self):
        if self.state == 'controls':
            pygame.mixer.Sound.play(menu_blocked)
        else : 
            pygame.mixer.Sound.play(menu_move)
            self.state_index += 1
            self.state = menu_states[self.state_index]

    def ogre_peek(self):
        BRAKE_POS = 120
        for i in (0,1) : 
            self.ogre_pos[i] += self.ogre_speed[i]*self.ogre_direction[i]
            if self.ogre_speed[i] < 0 : self.ogre_speed[i] = 0
            elif self.ogre_pos[1] < BRAKE_POS : 
                self.ogre_speed[i] -= 0.05

    def ogre_blink(self):
        if self.ogre_timer > 0 : self.ogre_timer -= 1
        if self.blink_timer > 0 : self.blink_timer -= 1
        if self.ogre_timer == 0 :
            self.ogre_sprite = menu_ogre['blink']
            self.blink_timer = 4
            self.ogre_timer = random.choice([12,30,120,220,320,440])
        if self.blink_timer == 0 :
            self.ogre_sprite = menu_ogre['ogre']

    def switch_music_on(self):
        if self.music_on : self.on_off_sprite = menu_texts['off']
        else : self.on_off_sprite = menu_texts['on']
        self.music_on = not self.music_on

    def play_music(self, song):
        mixer.music.stop()
        if self.music_on :
            pygame.mixer.music.load(song)
            mixer.music.set_volume(self.music_volume)
            mixer.music.play(-1)