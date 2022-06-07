import pygame
from config import *
from math import dist as math_dist
from debug import debug
from random import randint

class Support:

    @staticmethod
    def in_range(pos:tuple[int,int], player_pos:pygame.Vector2, radius:int):
        '''player in radius of pos check'''
        pos = pos*TILESIZE
        return math_dist((pos.x+TILESIZE//2, pos.y+TILESIZE//2), player_pos) <= radius

    @staticmethod
    def on_top(rect:pygame.Rect, player_rect:pygame.Rect):
        '''player on pressure-pad check
        called after collision handling'''
        return player_rect.bottom == rect.top

class ObjectInfo:

    def __init__(self, lvl:int, id:int, pos: tuple[int,int]):
        self.lvl = lvl
        self.id = id
        self.pos = pygame.Vector2(pos)

class Pad(ObjectInfo):

    def __init__(self, lvl:int, id:int, pos: tuple[int,int]):
        super().__init__(lvl, id, pos)

        self.pressed = False
        
        self.animation_ids = 127, 139, 151
        self.anim_index = 0
        self.anim_speed = 0.15

    def trigger(self, lvl_obj):

        tile_gid = lvl_obj.collision_layer.data[int(self.pos.y)][int(self.pos.x)]
        tile_rect = lvl_obj.get_rect_from_pos(self.pos.x, self.pos.y, tile_gid)

        return Support.on_top(tile_rect, lvl_obj.player.rect)

class Button(ObjectInfo):
    
        def __init__(self, lvl:int, id:int, pos:tuple[int,int]):
            super().__init__(lvl, id, pos)

            self.pressed = False

            self.animation_ids = 34, 46, 58
            self.anim_index = 0
            self.anim_speed = 0.15
        
        def trigger(self, lvl_obj, EVENT, radius=TILESIZE):
            if not self.pressed and Support.in_range(self.pos, lvl_obj.player.rect.center, radius):
                for event in EVENT:
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        return True

class level_4_id_0(Button):

    def __init__(self):
        super().__init__(4, 0, (4, 59))

    def run(self, lvl_obj, EVENT):

        if self.trigger(lvl_obj, EVENT):
            coll_data = lvl_obj.level_tmx.get_layer_by_name('collision_layer').data
            coll_data[59][11] = lvl_obj.get_gid_from_id(163)
            coll_data[60][11] = 0
            lvl_obj.level_tmx.get_layer_by_name('other_tiles').data[60][11] = 0
            self.pressed = True

        elif self.pressed:
            try:
                self.anim_index += self.anim_speed
                lvl_obj.level_tmx.get_layer_by_name('other_tiles').data[int(self.pos.y)][int(self.pos.x)] = lvl_obj.get_gid_from_id(self.animation_ids[int(self.anim_index)])
            except IndexError:
                return True

class level_4_id_1(Pad):

    def __init__(self):
        super().__init__(4, 1, (22, 60))

    def run(self, lvl_obj, EVENT):

        if self.trigger(lvl_obj):
            self.anim_index += self.anim_speed
        else: self.anim_index -= self.anim_speed/10

        self.anim_index = max(0, min(self.anim_index, 2))
        lvl_obj.collision_layer.data[int(self.pos.y)][int(self.pos.x)] = lvl_obj.get_gid_from_id(self.animation_ids[round(self.anim_index)])

        if not self.pressed and self.anim_index >= 1:
            self.pressed = True
            lvl_obj.collision_layer.data[57][28] = lvl_obj.get_gid_from_id(163)
            lvl_obj.collision_layer.data[61][28] = lvl_obj.get_gid_from_id(163)
            for y in range(58, 61):
                lvl_obj.collision_layer.data[y][28] = 0
        elif self.pressed and self.anim_index == 0:
            self.pressed = False
            lvl_obj.collision_layer.data[57][28] = lvl_obj.get_gid_from_id(164)
            lvl_obj.collision_layer.data[61][28] = lvl_obj.get_gid_from_id(164)

        if not self.pressed:
            for y in range(58, 61):
                lvl_obj.collision_layer.data[y][28] = lvl_obj.get_gid_from_id(randint(96,98))

class level_4_id_2(Button):

    def __init__(self):
        super().__init__(4, 2, (34, 59))

    def run(self, lvl_obj, EVENT):

        if self.trigger(lvl_obj, EVENT, TILESIZE*2):
            lvl_obj.level_tmx.get_layer_by_name('other_tiles').data[int(self.pos.y)][int(self.pos.x)] = lvl_obj.get_gid_from_id(155)
            return True