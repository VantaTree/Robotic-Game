import pygame
from pytmx.util_pygame import load_pygame
from csv import reader as csv_reader
from config import *
from player import Player
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
        self.player.movement()
        self.player.cooldowns()
        self.player.animate()

    def run(self):
        self.player_update()
        self.cam.update()


class Camera:

    def __init__(self, player:Player):

        self.player = player
        self.offset = pygame.Vector2()
        self.offset.x = self.player.rect.centerx - (W//2)
        self.offset.y = self.player.rect.centery - (H//2)

    def update(self):

        #update pos (gradually add to offset)
        self.offset.x -= (self.offset.x - self.player.rect.centerx + (W//2))*.1
        self.offset.y -= (self.offset.y - self.player.rect.centery + (H//2))*.1
        
        #clamp
        self.offset.x = max(0, min(self.offset.x, GRIDSIZE*TILESIZE-W))
        self.offset.y = max(0, min(self.offset.y, GRIDSIZE*TILESIZE-H))