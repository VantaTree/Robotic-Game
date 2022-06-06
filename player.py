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

    def get_id_from_gid(self, gid):
        '''gets id of tile from gid (provided by pytmx)'''
        return self.tile_ids[gid-1]-1

    def get_rect_from_pos(self, x, y, gid):
        '''fetches the rect for each tile from saved data'''
        if gid != 0:
            index = self.get_id_from_gid(gid)
        else: return None # index is -1

        r_data = TILE_RECTS[index]
        return pygame.Rect(x*TILESIZE+r_data[0], y*TILESIZE+r_data[1], r_data[2], r_data[3])

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

    def movement(self):    

        self.on_ground = False # on_ground reset

        self.direction.y = min(self.direction.y, self.terminal_velocity) # clamp fall
        self.direction.y += self.gravity # direction y needs to be updated for step collision in the horizontal section
        move_pos_y = self.direction.y

        #apply x movt
        if self.moving: self.speed += self.acceleration
        else: self.speed -= self.deceleration
        self.speed = max(0, min(self.speed, self.max_speed)) # clamp speed
        self.move_pos_x = self.direction.x * self.speed
        self.pos.x += self.move_pos_x
        self.rect.x = self.pos.x if self.direction.x < 0 else ceil(self.pos.x) # rounding error fix
        self.collision('horizontal')

        #apply y pos
        self.pos.y += move_pos_y
        self.rect.y = round(self.pos.y)
        self.collision('vertical')

        if self.on_ground:
            self.coyote_jump_timer = pygame.time.get_ticks()
            self.coyote_jump = True

    def collision(self, direction):

        for x,y,gid in self.collision_layer:

            id_ = self.get_id_from_gid(gid)
            if id_ in STEPS:
                for r_data in STEP_RECT[id_]:
                    tile_rect = pygame.Rect(x*TILESIZE+r_data[0], y*TILESIZE+r_data[1], r_data[2], r_data[3])
                    self.tile_collision(direction, tile_rect, x, y)
            else:
                tile_rect = self.get_rect_from_pos(x,y, gid)
                if tile_rect is None: continue # no tile present
                # if self.get_id_from_gid(gid) in RAMPS: continue # ramp collision already handeled
                if self.tile_collision(direction, tile_rect, x, y, id_): return

    def tile_collision(self, direction, tile_rect:pygame.Rect, x, y, id_=0):

        if tile_rect.colliderect(self.rect):

            if direction == 'horizontal':

                if id_ in RAMPS:
                    # if tile_rect.colliderect(pygame.Rect(self.pos.x-self.move_pos_x, self.pos.y, self.rect.width, self.rect.height)):
                    #     self.pos.x = self.pos.x-self.move_pos_x + (self.move_pos_x*.7)
                    return

                #step collision
                if self.direction.y > 0:
                    y_movt = pygame.Vector2(0,-1)
                    if tile_rect.height <= self.step_size and (tile_rect.collidepoint(self.rect.bottomright+y_movt) or tile_rect.collidepoint(self.rect.bottomleft+y_movt)):
                        try: # only step up when space is there
                            if tile_rect.top-self.rect.height > self.get_rect_from_pos(x, y-1, (self.collision_layer.data[y-1][x])).bottom:
                                #space is there
                                return
                            #else tile is blocking
                        except AttributeError or IndexError: return # no tile is present
                        # ignore honizontal coll to act like steps
                
                #horizontal collision
                self.speed = 0
                if self.direction.x > 0:
                    self.rect.right = tile_rect.left
                    self.pos.x = self.rect.x
                elif self.direction.x < 0:
                    self.rect.left = tile_rect.right
                    self.pos.x = self.rect.x

            elif direction == 'vertical':

                if id_ in RAMPS:
                    if not self.slope_coll(tile_rect, id_): return

                #vertical collision
                if self.direction.y > 0:
                    self.rect.bottom = tile_rect.top
                    self.pos.y = self.rect.y
                    self.on_ground = True # on ground check
                    self.direction.y = 0
                elif self.direction.y < 0:
                    self.rect.top = tile_rect.bottom
                    self.pos.y = self.rect.y
                    self.direction.y = abs(self.direction.y)* -.2 # bounce player down

    def slope_coll(self, t_rect:pygame.Rect, id_):

        if id_ in (R1, R3):
            offset = self.rect.right - t_rect.left
        elif id_ in (R2, R4):
            offset = t_rect.right - self.rect.left

        if id_ in (R1, R2):
            if not 0 <= offset <= TILESIZE: return True
            target_pos = t_rect.bottom-offset
            self.rect.bottom = min(self.rect.bottom, target_pos)
            if self.rect.bottom == target_pos:
                self.pos.y = self.rect.y
                self.on_ground = True
                self.direction.y = 0
            
        elif id_ in (R3, R4):
            if 0 > offset > TILESIZE:
                self.tile_collision('horizontal', t_rect, t_rect.x, t_rect.y, id_)
                return
            target_pos = t_rect.top+offset
            self.rect.top = max(self.rect.top, target_pos)
            if self.rect.top == target_pos:
                self.pos.y = self.rect.y
                self.direction.y = 1

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
