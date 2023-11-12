import pygame
from gui import MASK_COLOR, BEIGE, PINK, RED, LBLUE, BLUE

# Prompt Details
PROMPT_LEFT = 145
PROMPT_TOP = 200
PROMPT_WIDTH = 250
PROMPT_HEIGHT = 75
PROMPT_FONT = None

class BoardView:
    def __init__(self, board):
        self.board = board
        pygame.init()
        self.DISPLAYSURF = pygame.display.set_mode((800, 600))
        self.ALPHASURF = self.DISPLAYSURF.convert_alpha()
        pygame.display.set_caption("Wordsmith - Prapat edition")       

    def draw(self):
        # draw each square
        for x in range(self.board.GRID_SIZE):
            for y in range(self.board.GRID_SIZE):
                # draw position
                left = (
                    x * (self.board.SQUARE_SIZE + self.board.SQUARE_BORDER)
                    + self.board.SQUARE_BORDER
                    + self.board.BOARD_LEFT
                )
                top = (
                    y * (self.board.SQUARE_SIZE + self.board.SQUARE_BORDER)
                    + self.board.SQUARE_BORDER
                    + self.board.BOARD_TOP
                )

                tile = self.board.get_tile(x, y)
                bonus = self.board.get_bonus(x, y)
                if bonus == self.board.NORMAL:
                    color = BEIGE
                elif bonus == self.board.DOUBLEWORD:
                    color = PINK
                elif bonus == self.board.TRIPLEWORD:
                    color = RED
                elif bonus == self.board.DOUBLELETTER:
                    color = LBLUE
                elif bonus == self.board.TRIPLELETTER:
                    color = BLUE
                else:
                    assert False
                pygame.draw.rect(
                    self.DISPLAYSURF,
                    color,
                    (left, top, self.board.SQUARE_SIZE, self.board.SQUARE_SIZE),
                )

                if tile is not None:
                    if tile.locked:
                        highlight = False
                    else:
                        highlight = True
                    tile.draw(left, top, self.DISPLAYSURF, highlight)

        # =======DRAW LOCK SHADING==========
        self.ALPHASURF.fill((0, 0, 0, 0))
        top = self.board.BOARD_TOP
        left = self.board.BOARD_LEFT
        right = (
            self.board.GRID_SIZE * (self.board.SQUARE_BORDER + self.board.SQUARE_SIZE)
            + self.board.SQUARE_BORDER
        )
        bottom = (
            self.board.GRID_SIZE * (self.board.SQUARE_BORDER + self.board.SQUARE_SIZE)
            + self.board.SQUARE_BORDER
        )
        x1 = (
            self.board.columnLock * (self.board.SQUARE_SIZE + self.board.SQUARE_BORDER)
            + self.board.BOARD_LEFT
        )
        x2 = x1 + (self.board.SQUARE_SIZE + self.board.SQUARE_BORDER) + \
            self.board.SQUARE_BORDER
        y1 = self.board.rowLock * (self.board.SQUARE_SIZE +
                             self.board.SQUARE_BORDER) + self.board.BOARD_LEFT
        y2 = y1 + (self.board.SQUARE_SIZE + self.board.SQUARE_BORDER) + \
            self.board.SQUARE_BORDER
        if self.board.rowLock >= 0 and self.board.columnLock >= 0:
            pygame.draw.rect(self.ALPHASURF, MASK_COLOR,
                             (left, top, x1 - left, y1 - top))
            pygame.draw.rect(self.ALPHASURF, MASK_COLOR,
                             (left, y2, x1 - left, bottom - y2))
            pygame.draw.rect(self.ALPHASURF, MASK_COLOR,
                             (x2, top, right - x2, y1 - top))
            pygame.draw.rect(self.ALPHASURF, MASK_COLOR,
                             (x2, y2, right - x2, bottom - y2))
        elif self.board.rowLock >= 0:
            pygame.draw.rect(self.ALPHASURF, MASK_COLOR,
                             (left, top, right - left, y1 - top))
            pygame.draw.rect(
                self.ALPHASURF, MASK_COLOR, (left, y2, right - left, bottom - y2)
            )
        elif self.board.columnLock >= 0:
            pygame.draw.rect(
                self.ALPHASURF, MASK_COLOR, (left, top, x1 - left, bottom - top)
            )
            pygame.draw.rect(self.ALPHASURF, MASK_COLOR,
                             (x2, top, right - x2, bottom - top))

        self.DISPLAYSURF.blit(self.ALPHASURF, (0, 0))

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
