import pygame
from config import *
from level import Level

#Initialize
pygame.init()
screen = pygame.display.set_mode((W,H), pygame.FULLSCREEN|pygame.SCALED)
pygame.display.set_caption('Robot Platformer')
clock = pygame.time.Clock()

#level
level = Level(1) #available levels: 0,1,2,3

#Game Loop
while True:

    pygame.display.update()
    clock.tick(FPS)

    # EVENT = pygame.event.get().copy()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                raise SystemExit

    level.draw()
    level.run()