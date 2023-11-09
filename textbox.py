import pygame
from models.textbox_model import TextBoxModel
from gui import DISPLAYSURF


class TextBox:
    initialized = False
    MARGIN = 21

    @staticmethod
    def initialize():
        TextBox.FONT = pygame.font.Font("freesansbold.ttf", 18)
        TextBox.initialized = True

    def __init__(self, textLines, pos, highlight_color, normal_color, horzCenter=False):
        self.text = textLines
        self.pos = pos
        self.color = highlight_color
        self.width = 0
        self.backColor = normal_color
        self.horzCentered = horzCenter
        if not TextBox.initialized:
            TextBox.initialize()
        self.model = TextBoxModel(textLines, pos, highlight_color, normal_color, horzCenter)

    def draw(self):
        i = 0
        for line in self.text:
            left = self.pos[0]
            top = self.pos[1] + TextBox.MARGIN * i
            text = TextBox.FONT.render(line, True, self.color, self.backColor)
            rect = text.get_rect()
            if self.horzCentered:
                rect.centerx = left
            else:
                rect.left = left
            rect.top = top
            if rect.width > self.width:
                self.width = rect.width
            DISPLAYSURF.blit(text, rect)
            i += 1

    def undraw(self):
        height = TextBox.MARGIN * len(self.text)
        if self.horzCentered:
            rect = (self.pos[0] - self.width / 2, self.pos[1], self.width, height)
        else:
            rect = (self.pos[0], self.pos[1], self.width, height)
        pygame.draw.rect(DISPLAYSURF, self.backColor, rect)


class NullTextBox(TextBox):
    """NullTextBox is a TextBox that does nothing when drawn or undrawn."""

    def __init__(self):
        super().__init__([], (0, 0), (0, 0, 0), (0, 0, 0), False)

    def draw(self):
        pass

    def undraw(self):
        pass
