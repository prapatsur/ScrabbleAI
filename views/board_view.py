import pygame
from gui import MASK_COLOR, BEIGE, PINK, RED, LBLUE, BLUE
from views.letter_prompt_view import LetterPromptView

class BoardView:
    def __init__(self, board):
        self.board = board
        pygame.init()
        self.DISPLAYSURF = pygame.display.set_mode((800, 600))
        self.ALPHASURF = self.DISPLAYSURF.convert_alpha()
        pygame.display.set_caption("Wordsmith - Prapat edition") 
        self.letter_prompt_view = LetterPromptView(self.DISPLAYSURF, self.ALPHASURF)      

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

    def draw_letter_prompt(self):
        """ Draws a letter prompt to ask for the blank letter """
        # delegate tasks to letter_prompt_view
        self.letter_prompt_view.draw()
