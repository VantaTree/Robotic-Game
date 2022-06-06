import pygame
import pickle

#InputClass

class Inputs:

    def __init__(self, x, y, name, grp, text='0'):

        self.x = x
        self.y = y
        self.name = name
        self.text = text # content of the input box
        self.font = pygame.font.SysFont('Arial', 20)
        self.name_surf = self.font.render(name, False, 'darkblue')
        self.name_rect = self.name_surf.get_rect(center = (x,y-30))
        grp[name] = self # it's like pygame's sprite grp

    def draw(self, screen, selected_name):

        #blit input heading
        screen.blit(self.name_surf, self.name_rect)

        color = 'gold' if selected_name == self.name else 'black'
        text = self.font.render(self.text, False, (0, 0, 0))
        text_rect = text.get_rect(center = (self.x, self.y))
        self.rect = text_rect.inflate(10, 10)
        screen.blit(text, text_rect) # blit text
        pygame.draw.rect(screen, color, self.rect, 3) #blit box outline
       
    def update(self):
        # yeah, this is a bit of a hack, but it works
        # github copilot is a bit of a jerk
        '''suggested by /\\ github copilot'''
        if not self.text:
            self.text = '0'

class InputManeger:

    def __init__(self):

        self.screen = pygame.display.get_surface()
        self.grp = {}
        self.input_selected = None

    def draw(self):

        #draw all input boxes
        for element in self.grp.values():
            element.draw(self.screen, self.input_selected)

    def get_selected(self):

        #select an input box

        if not pygame.mouse.get_pressed()[0]: return
        for element in self.grp.values():
            if element.rect.collidepoint(pygame.mouse.get_pos()) or element.name_rect.collidepoint(pygame.mouse.get_pos()):
                self.input_selected = element.name
                break
        else:
            self.input_selected = None

    def input(self, text=None, backspace=False):

        #update text for inout boxes
        if self.input_selected is None: return
        element = self.grp[self.input_selected]
        if backspace:
            element.text = element.text[:-1]
        elif text and len(element.text) < 5:
            element.text += text

        # update data like index, rect
        element.update()
        if element.name == 'Index':
            change_index(index=int(element.text))
        else:
            update_rect(element.name, int(element.text))

    def update(self):
        self.get_selected()
        self.draw()

#button class

class Button:

    def __init__(self, pos, name, group):

        self.name = name
        self.font = pygame.font.SysFont('Arial', 25)
        self.image = self.font.render(name, False, 'darkblue')
        self.rect = self.image.get_rect(center = pos)
        self.outline_rect = self.rect.inflate(10, 10)

        group[name] = (self, self.outline_rect) # it's like pygame's sprite grp

    def draw(self, screen):

        #draw button
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, 'black', self.outline_rect, 3)

#support
def get_rectI(index):

    #get tile x and y from index (not including offset)
    x = index % GRID_SIZE[0] * TILE_SIZE
    y = index // GRID_SIZE[0] * TILE_SIZE
    return(x, y, TILE_SIZE, TILE_SIZE)

def make_tile(index):

    #get tile from tile map surface
    rect = get_rectI(index)
    tile_img = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    tile_img.blit(tile_map, (0,0), rect) 

    tile_img = pygame.transform.scale(tile_img, (TILE_SIZE*TILESCALE, TILE_SIZE*TILESCALE))

    return tile_img

def update_rect(name, value):

    #update rects based on input boxes
    match name:
        case 'Left': tile_rects[tile_index].left = value
        case 'Top': tile_rects[tile_index].top = value
        case 'Width': tile_rects[tile_index].width = value
        case 'Height': tile_rects[tile_index].height = value

def change_index(increment=0, index = None):

    global tile_index, tile_img

    #change tile index
    if index is not None:
        tile_index = index
    tile_index += increment

    #clamp index
    if tile_index > (v:=GRID_SIZE[0]*GRID_SIZE[1] -1):
        tile_index = v
    if tile_index < 0: tile_index = 0

    #get tile from tile map surface
    tile_img = make_tile(tile_index)
    manager.grp['Index'].text = str(tile_index)

    rect = tile_rects[tile_index]
    manager.grp['Left'].text = str(rect.left)
    manager.grp['Top'].text = str(rect.top)
    manager.grp['Width'].text = str(rect.width)
    manager.grp['Height'].text = str(rect.height)

def draw_buttons():
    #draw buttons what do you except
    for button,_ in buttons.values():
        button.draw(screen)

def button_logic():

        global show_rect_overlay

        for key, (_, rect) in buttons.items():
            if rect.collidepoint(pygame.mouse.get_pos()):

                if key == 'Save':
                    with open(RECTSAVED, 'wb') as f:
                        pickle.dump(tile_rects, f)
                #pre-determined rects
                elif key == 'Full':
                    tile_rects[tile_index] = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
                elif key == 'Bottom Half':
                    tile_rects[tile_index] = pygame.Rect(0, TILE_SIZE//2, TILE_SIZE, TILE_SIZE//2)
                elif key == 'Top Half':
                    tile_rects[tile_index] = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE//2)
                elif key == 'Top Rail':
                    tile_rects[tile_index] = pygame.Rect(0, 0, TILE_SIZE, 3)
                elif key == 'Button Stand':
                    tile_rects[tile_index] = pygame.Rect(5, 3, 6, 13)
                elif key == 'Toggle Overlay':
                    show_rect_overlay = not show_rect_overlay
                elif key == 'None':
                    tile_rects[tile_index] = pygame.Rect(0,0,0,0)

                change_index() # save rects to input boxes

#init
pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN|pygame.SCALED)
clock = pygame.time.Clock()

#vars
tile_map = pygame.image.load('data/assets/world tileset16x16.png')
TILE_SIZE = 16 # tile size in pixels
TILESCALE = 6 # scale ur tiles to see each one better
GRID_SIZE = tile_map.get_width()//TILE_SIZE, tile_map.get_height()//TILE_SIZE
tile_index = 0
tile_img = make_tile(tile_index)

show_rect_overlay = True

RECTSAVED = "data/saved/tile_rects.PICKLE"

#load rects
try:
    with open(RECTSAVED, 'rb') as f:
        tile_rects = pickle.load(f)
        if len(tile_rects) < GRID_SIZE[0]*GRID_SIZE[1]:
            tile_rects += [pygame.Rect(0,0,TILE_SIZE,TILE_SIZE)]*(GRID_SIZE[0]*GRID_SIZE[1] - len(tile_rects))
except FileNotFoundError:
    tile_rects =  [ pygame.Rect(0,0,TILE_SIZE,TILE_SIZE) for _ in range(GRID_SIZE[0]*GRID_SIZE[1])]


#text inputs
manager = InputManeger()
Inputs(700, 500, 'Left', manager.grp)
Inputs(800, 500, 'Top', manager.grp)
Inputs(900, 500, 'Width', manager.grp)
Inputs(1000, 500, 'Height', manager.grp)
Inputs(850, 600, 'Index', manager.grp, '0')

#buttons
buttons = dict()
Button((700, 200), 'Full', buttons)
Button((760, 200), 'None', buttons)
Button((840, 200), 'Top Rail', buttons)
Button((940, 200), 'Top Half', buttons)
Button((1060, 200), 'Bottom Half', buttons)
Button((1190, 200), 'Button Stand', buttons)

Button((780, 260), 'Save', buttons)
Button((900, 260), 'Toggle Overlay', buttons)


#main loop
while True:

    pygame.display.update()
    clock.tick(60)

    for event in pygame.event.get():

        # <exit>
        if event.type == pygame.QUIT:
            with open(RECTSAVED, 'wb') as f:
                pickle.dump(tile_rects, f)
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                with open(RECTSAVED, 'wb') as f:
                    pickle.dump(tile_rects, f)
                pygame.quit()
                raise SystemExit
        # </exit>

            if event.key == pygame.K_BACKSPACE:
                manager.input(backspace=True)#backspace

            # chnage tile
            if event.key == pygame.K_RIGHT:
                change_index(1)
            if event.key == pygame.K_LEFT:
                change_index(-1)

        if event.type == pygame.TEXTINPUT:
            manager.input(text=event.text) #add text input
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            button_logic() # button press logic

    screen.fill('grey')
    screen.blit(tile_img, (128, 296+32)) # tile image
    
    if show_rect_overlay: # show rect overlay
        t_rect = tile_rects[tile_index]
        rect = (t_rect.x*TILESCALE, t_rect.y*TILESCALE, t_rect.width*TILESCALE, t_rect.height*TILESCALE)
        rect_overlay = pygame.Surface((256, 256), pygame.SRCALPHA)
        pygame.draw.rect(rect_overlay, (0, 0, 255, 80), rect)
        screen.blit(rect_overlay, (128, 296+32))

    draw_buttons()
    manager.update()
