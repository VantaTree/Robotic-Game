import pygame
from pickle import load as p_load
from pickle import dump as p_dump

#window & game
W, H = 640, 360
FPS = 60
TILESIZE = 16
GRIDSIZE = 64

#each tile rect
TILE_RECTS = p_load(open('data/saved/tile_rect_list.PICKLE', 'rb'))

#Ramps
RAMPS = R1, R2, R3, R4 = 72, 73, 84, 85

#timers
JUMP_DELAY = 200
COYOTEJUMP_DELAY = 70
JUMP_BUFFER = 50

#Level
LEVEL_DATA = {
    'player pos': {
        0: (7, 58),
        1: (3, 60),
        2: (2, 61),
    },
    'bg color': {
        # 0: 'burlywood1',
        0: 'cornsilk3',
        1: 'lavenderblush3',
        2: 'beige',
    }
}

'''https://mike632t.wordpress.com/2018/02/10/displaying-a-list-of-the-named-colours-available-in-pygame/'''

# TILE_RECTS = []
# for r in p_load(open('data/saved/tile_rects.PICKLE', 'rb')):
#     r = (r.left, r.top, r.width, r.height)
#     TILE_RECTS.append(r)

# p_dump(TILE_RECTS, open('data/saved/tile_rect_list.PICKLE', 'wb'))



#Note:
'''
1) no placing THIN bottom tiles on top of THIN top tiles.
2) no exposed flat face of ramps, only the diagonal ones.
'''

# To-Do
'''
1) save tile index when player collides with them yo later check them for
   interactable objects like buttons, etc.
2) you can chnage the tile by changing the id in tmx_layer.data.
'''