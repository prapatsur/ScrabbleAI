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
        self.draw_game_board()

    def draw_game_board(self):
        """ Draws the game board """
        self.draw_each_square()
        self.draw_lock_shading()

    def draw_lock_shading(self):
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

    def calculate_position(self, x, y):
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
        return left, top

    def determine_color(self, bonus):
        if bonus == self.board.NORMAL:
            return BEIGE
        elif bonus == self.board.DOUBLEWORD:
            return PINK
        elif bonus == self.board.TRIPLEWORD:
            return RED
        elif bonus == self.board.DOUBLELETTER:
            return LBLUE
        elif bonus == self.board.TRIPLELETTER:
            return BLUE
        else:
            assert False

    def draw_each_square(self):
        for x in range(self.board.GRID_SIZE):
            for y in range(self.board.GRID_SIZE):
                left, top = self.calculate_position(x, y)
                tile = self.board.get_tile(x, y)
                color = self.determine_color(self.board.get_bonus(x, y))
                pygame.draw.rect(
                    self.DISPLAYSURF,
                    color,
                    (left, top, self.board.SQUARE_SIZE, self.board.SQUARE_SIZE),
                )

                if tile is not None:
                    highlight = not tile.locked
                    tile.draw(left, top, self.DISPLAYSURF, highlight)

    def draw_letter_prompt(self):
        """ Draws a letter prompt to ask for the blank letter """
        # delegate tasks to letter_prompt_view
        self.letter_prompt_view.draw()
