import pygame
from pytmx.util_pygame import load_pygame
from csv import reader as csv_reader
from config import *
from player import Player
from math import ceil
from level_object import create_objects
# from pickle import load as p_load

class Level:

    def __init__(self, level_no:int):

        self.screen = pygame.display.get_surface()

        self.level_no = level_no
        self.level_tmx = load_pygame(f"data/..tiled/levels/level{level_no}.tmx", load_all_tiles=True)
        self.collision_layer = self.level_tmx.get_layer_by_name('collision_layer')
        self.tile_ids = list(self.level_tmx.gidmap)

        self.player = Player(*LEVEL_DATA['player pos'][level_no], self.level_tmx, self.tile_ids)
        self.cam = Camera(self.player)

        self.objects = create_objects(level_no)
        for obj in self.objects:
            try: obj.on_ready(self)
            except AttributeError: pass

    def get_gid_from_id(self, id):
        '''gets gid of tile from id (provided by pytmx)'''
        return self.tile_ids.index(id+1)+1

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

    
    def player_movement(self):    

        player = self.player

        player.on_ground = False # on_ground reset

        player.direction.y = min(player.direction.y, player.terminal_velocity) # clamp fall
        player.direction.y += player.gravity # direction y needs to be updated for step collision in the horizontal section
        move_pos_y = player.direction.y

        #apply x movt
        if player.moving: player.speed += player.acceleration
        else: player.speed -= player.deceleration
        player.speed = max(0, min(player.speed, player.max_speed)) # clamp speed
        player.move_pos_x = player.direction.x * player.speed
        player.pos.x += player.move_pos_x
        player.rect.x = player.pos.x if player.direction.x < 0 else ceil(player.pos.x) # rounding error fix
        self.player_collision('horizontal')

        #apply y pos
        player.pos.y += move_pos_y
        player.rect.y = round(player.pos.y)
        self.player_collision('vertical')

        if player.on_ground:
            player.coyote_jump_timer = pygame.time.get_ticks()
            player.coyote_jump = True

    def player_collision(self, direction):

        # player = self.player

        for x,y,gid in self.collision_layer:

            id_ = self.get_id_from_gid(gid)
            if id_ in STEPS:
                for r_data in STEP_RECT[id_]:
                    tile_rect = pygame.Rect(x*TILESIZE+r_data[0], y*TILESIZE+r_data[1], r_data[2], r_data[3])
                    self.player_tile_collision(direction, tile_rect, x, y)
            else:
                tile_rect = self.get_rect_from_pos(x,y, gid)
                if tile_rect is None: continue # no tile present
                # if self.get_id_from_gid(gid) in RAMPS: continue # ramp collision already handeled
                if self.player_tile_collision(direction, tile_rect, x, y, id_): return

    def player_tile_collision(self, direction, tile_rect:pygame.Rect, x, y, id_=0):

        player = self.player

        if tile_rect.colliderect(player.rect):

            if direction == 'horizontal':

                if id_ in RAMPS:
                    # if tile_rect.colliderect(pygame.Rect(self.pos.x-self.move_pos_x, self.pos.y, self.rect.width, self.rect.height)):
                    #     self.pos.x = self.pos.x-self.move_pos_x + (self.move_pos_x*.7)
                    return

                #step collision
                if player.direction.y > 0:
                    y_movt = pygame.Vector2(0,-1)
                    if tile_rect.height <= player.step_size and (tile_rect.collidepoint(player.rect.bottomright+y_movt) or tile_rect.collidepoint(player.rect.bottomleft+y_movt)):
                        try: # only step up when space is there
                            if tile_rect.top-player.rect.height > self.get_rect_from_pos(x, y-1, (self.collision_layer.data[y-1][x])).bottom:
                                #space is there
                                return
                            #else tile is blocking
                        except AttributeError or IndexError: return # no tile is present
                        # ignore honizontal coll to act like steps
                
                #horizontal collision
                player.speed = 0
                if player.direction.x > 0:
                    player.rect.right = tile_rect.left
                    player.pos.x = player.rect.x
                elif player.direction.x < 0:
                    player.rect.left = tile_rect.right
                    player.pos.x = player.rect.x

            elif direction == 'vertical':

                if id_ in RAMPS:
                    if not self.player_slope_coll(tile_rect, id_): return

                #vertical collision
                if player.direction.y > 0:
                    player.rect.bottom = tile_rect.top
                    player.pos.y = player.rect.y
                    player.on_ground = True # on ground check
                    player.direction.y = 0
                elif player.direction.y < 0:
                    player.rect.top = tile_rect.bottom
                    player.pos.y = player.rect.y
                    player.direction.y = abs(player.direction.y)* -.2 # bounce player down

    def player_slope_coll(self, t_rect:pygame.Rect, id_):

        player = self.player

        if id_ in (R1, R3):
            offset = player.rect.right - t_rect.left
        elif id_ in (R2, R4):
            offset = t_rect.right - player.rect.left

        if id_ in (R1, R2):
            if not 0 <= offset <= TILESIZE: return True
            target_pos = t_rect.bottom-offset
            player.rect.bottom = min(player.rect.bottom, target_pos)
            if player.rect.bottom == target_pos:
                player.pos.y = player.rect.y
                player.on_ground = True
                player.direction.y = 0
            
        elif id_ in (R3, R4):
            if 0 > offset > TILESIZE:
                self.player_tile_collision('horizontal', t_rect, t_rect.x, t_rect.y, id_)
                return
            target_pos = t_rect.top+offset
            player.rect.top = max(player.rect.top, target_pos)
            if player.rect.top == target_pos:
                player.pos.y = player.rect.y
                player.direction.y = 1


    def draw_visible_layers(self):

        for layer in self.level_tmx.visible_layers:
            for x, y, surf in layer.tiles():
                self.screen.blit(surf, (x*TILESIZE-self.cam.offset.x, y*TILESIZE-self.cam.offset.y))

    def draw(self):

        self.screen.fill(LEVEL_DATA['bg color'][self.level_no])
        self.draw_visible_layers()
        self.player.draw(self.cam.offset)

    def player_update(self):
        self.player.input()
        self.player_movement()
        self.player.cooldowns()
        self.player.animate()

    def run(self, EVENT):
        self.player_update()
        self.cam.update()
        for obj in self.objects.copy():
            if obj.run(self, EVENT):
                self.objects.remove(obj)

class Camera:

    def __init__(self, player:Player):

        self.player = player
        self.offset = pygame.Vector2()
        self.offset.x = self.player.rect.centerx - (W//2)
        self.offset.y = self.player.rect.centery - (H//2)

    def update(self):

        #update pos (gradually add to offset)
        self.offset.x -= round((self.offset.x - self.player.rect.centerx + (W//2))*.1)
        self.offset.y -= round((self.offset.y - self.player.rect.centery + (H//2))*.1)
        
        #clamp
        self.offset.x = max(0, min(self.offset.x, GRIDSIZE*TILESIZE-W))
        self.offset.y = max(0, min(self.offset.y, GRIDSIZE*TILESIZE-H))