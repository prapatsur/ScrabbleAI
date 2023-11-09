import pygame

pygame.init()

# window setup
DISPLAYSURF = pygame.display.set_mode((800, 600))
ALPHASURF = DISPLAYSURF.convert_alpha()
pygame.display.set_caption('Wordsmith - Prapat edition')

# Simple sound effects
TIC = pygame.mixer.Sound('media/tic.ogg')
TICTIC = pygame.mixer.Sound('media/tictic.ogg')
DINGDING = pygame.mixer.Sound('media/dingding.ogg')
SCRIFFLE = pygame.mixer.Sound('media/scriffle.ogg')
CLICK = pygame.mixer.Sound('media/click.ogg')

# const color
DARK_BROWN = (55, 46, 40)
WHITE = (255, 255, 255)
LIGHT_LAVENDOR = (200, 200, 255)
DARK_LAVENDOR = (125, 125, 170)