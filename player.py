import pygame
from pytmx import TiledMap
from config import *
from math import ceil
from debug import debug

class Player:

    def __init__(self, x, y, level_tmx:TiledMap, tile_ids:list):

        #general
        self.rect = pygame.Rect(0,0, 10, 15)
        self.rect.midbottom=(x*TILESIZE+(TILESIZE//2), y*TILESIZE+TILESIZE)
        self.screen = pygame.display.get_surface()

        #animation
        self.animations = self.load_animation(6)
        self.state = 'idle'
        self.look_right = True
        self.anim_speed = 0.15
        self.frame_index = 0
        self.image = self.animations['idle'][0]

        #level
        self.level_tmx = level_tmx
        self.collision_layer = level_tmx.get_layer_by_name('collision_layer')
        self.tile_ids = tile_ids

        #movement
        self.moving = False
        self.pos = pygame.Vector2(self.rect.topleft)# use this instead of rect's pos
        self.direction = pygame.Vector2(1,0)
        self.speed = 0
        self.acceleration = .3
        self.deceleration = .5
        self.max_speed = 2.5

        self.step_size = 4 #put player above tile (no need to jump)

        self.max_jump_speed = 4.8
        self.gravity = .3
        self.terminal_velocity = 8
        self.on_ground = False
        self.can_jump = True
        self.coyote_jump = False

        self.jump_button_down = False
        self.should_jump = False
        self.jump_buffer = None

    def load_animation(self, c_num):

        character_map_surf = pygame.image.load('data/assets/characters/characters tileset 16x32.png').convert_alpha()
        
        animations = {}
        #load from single image
        for state in ('jump', 'fall'):
            animations[state] = [pygame.image.load(f'data/assets/characters/{state}/{state}{c_num}.png').convert_alpha()]

        #load from tile sheet
        animations['idle'], animations['moving'] = [], []
        for i in range(13):
            if i == 4: continue
            img = pygame.Surface((16, 32), pygame.SRCALPHA)
            img.blit(character_map_surf, (0,0), (i*16, c_num*32, 16, 32))
            state = 'idle' if i in range(4) else 'moving'
            animations[state].append(img)
        
        return animations

    def input(self):

        keys = pygame.key.get_pressed()

        if keys[pygame.K_d]:# right
            if self.direction.x == -1: self.speed =  0
            self.direction.x = 1
            self.moving = True
        if keys[pygame.K_a]:# left
            if self.direction.x == 1: self.speed = 0
            self.direction.x = -1
            self.moving = True
        if not(keys[pygame.K_d] or keys[pygame.K_a]) or keys[pygame.K_d] and keys[pygame.K_a]:
            self.moving = False

        if keys[pygame.K_SPACE]:
            if not self.jump_button_down:
                self.jump_button_down = True
                self.should_jump = True
                self.jump_buffer = pygame.time.get_ticks()
        else:
            self.jump_button_down = False
            # if self.direction.y < -self.max_jump_speed/2: #cancel jump only if player let button go early
            #     self.direction.y = self.direction.y/4

        # if keys[pygame.K_SPACE]:
        if self.should_jump and self.can_jump and (self.on_ground or self.coyote_jump):# jump
            self.direction.y = -self.max_jump_speed
            self.can_jump = False
            self.jump_timer = pygame.time.get_ticks()

    def animate(self):

        # snimation states
        if self.direction.y < 0: self.state = 'jump'
        elif self.direction.y > 1: self.state = 'fall'
        else: self.state = 'moving' if self.speed else 'idle'

        # progress animation
        self.frame_index += self.anim_speed
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0

        # select anim image
        self.image = self.animations[self.state][int(self.frame_index)]
        if self.direction.x == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def cooldowns(self):
        '''coll downs'''
        current_time = pygame.time.get_ticks()

        if not self.can_jump and current_time - self.jump_timer > JUMP_DELAY: # jump timer
            self.can_jump = True

        if self.coyote_jump and current_time - self.coyote_jump_timer > COYOTEJUMP_DELAY:
            self.coyote_jump = False

        if self.should_jump and current_time - self.jump_buffer > JUMP_BUFFER:
            self.should_jump = False

    def draw(self, offset):

        self.screen.blit(self.image, (self.rect.centerx-offset.x-8, self.rect.bottom-offset.y-32))
