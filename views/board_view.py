import pygame
from gui import MASK_COLOR

# Prompt Details
PROMPT_LEFT = 145
PROMPT_TOP = 200
PROMPT_WIDTH = 250
PROMPT_HEIGHT = 75
PROMPT_FONT = None

class BoardView:
    def __init__(self, board):
        self.board = board

        
def draw_letter_prompt(DISPLAYSURF, ALPHASURF):
    """
    Draws a letter prompt to ask for the blank letter
    """
    # Draw prompt shadow
    ALPHASURF.fill((0, 0, 0, 0))
    pygame.draw.rect(
        ALPHASURF,
        MASK_COLOR,
        (
            PROMPT_LEFT,
            PROMPT_TOP,
            PROMPT_WIDTH + 4,
            PROMPT_HEIGHT + 4,
        ),
    )

    # Draw prompt box
    pygame.draw.rect(
        ALPHASURF,
        (0, 0, 0, 200),
        (
            PROMPT_LEFT - 1,
            PROMPT_TOP - 1,
            PROMPT_WIDTH + 2,
            PROMPT_HEIGHT + 2,
        ),
    )
    pygame.draw.rect(
        ALPHASURF,
        (255, 255, 255, 200),
        (
            PROMPT_LEFT,
            PROMPT_TOP,
            PROMPT_WIDTH,
            PROMPT_HEIGHT,
        ),
    )

    DISPLAYSURF.blit(ALPHASURF, (0, 0))

    # Draw text
    PROMPT_FONT = pygame.font.Font("freesansbold.ttf", 20)
    promptText = PROMPT_FONT.render(
        "TYPE A LETTER A-Z", True, (0, 0, 0, 200), (255, 255, 255, 200)
    )
    promptRect = promptText.get_rect()
    promptRect.center = (
        PROMPT_LEFT + PROMPT_WIDTH / 2,
        PROMPT_TOP + PROMPT_HEIGHT / 2,
    )
    DISPLAYSURF.blit(promptText, promptRect)
