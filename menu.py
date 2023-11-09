"""
This will store any menus all inherited from a prototype with two functions
update and execute. Update will change display based on cursor position, while
execute will process button clicks.
"""

import pygame, ai
from pygame.locals import *
from gui import DISPLAYSURF, ALPHASURF, CLICK
from gui import DARK_BROWN, WHITE, LIGHT_LAVENDOR, DARK_LAVENDOR
from gui import MAIN_MENU_TEXTBOX_POS
from models.textbox_model import TextBoxModel
from textbox import TextBox
from button import Button
from userdata import UserData


class Menu:
    def __init__(self):
        self.buttons = {}
        self.rect = (0, 0, 800, 600)
        self.background = WHITE

    """
	Goes through all buttons and returns the name of the button, if it was clicked
	"""

    def execute(self, mouseX, mouseY):
        """
        Executes the menu by checking if the mouse is within the menu area and if any of the buttons are clicked.

        Args:
                mouseX (int): The x-coordinate of the mouse.
                mouseY (int): The y-coordinate of the mouse.

        Returns:
                str: The key of the button that was clicked, or an empty string if no button was clicked.
        """
        if not self.within(mouseX, mouseY):
            return ""

        for key, button in self.buttons.items():
            if button.within(mouseX, mouseY):
                CLICK.play()
                return key

        return ""

    """
	Goes through and updates all buttons, redrawing them if they are hovered
	"""

    def update(self, mouse_position=None):
        assert mouse_position is not None
        for button in list(self.buttons.values()):
            button.update(mouse_position)

    def within(self, mouseX, mouseY):
        (left, top, width, height) = self.rect
        return (
            mouseX >= left
            and mouseX <= left + width
            and mouseY >= top
            and mouseY <= top + height
        )

    def display(self):
        pygame.draw.rect(DISPLAYSURF, self.background, self.rect)
        for button in list(self.buttons.values()):
            button.redraw()


# ==================== MAIN MENU =====================


class MainMenu(Menu):
    NEW_GAME = "new"
    EXIT_GAME = "exit"
    TRAINING = "training"
    ACHIEVEMENT = "achievement"

    def __init__(self, userdata=None):
        Menu.__init__(self)
        trainerText = TextBox(
            [
                "Practice your Scrabble skills with a built-in HINT",
                "box, which lets you know how the AI would have played",
                "your move. But you can't get ACHIEVEMENTS while training.",
            ],
            MAIN_MENU_TEXTBOX_POS,
            DARK_BROWN,
            WHITE,
            horzCenter=True,
        )
        newGameText = TextBox(
            [
                "Play one-on-one against Wordsmith, the Scrabble AI.",
                "No hints allowed, try to beat your best score!",
            ],
            MAIN_MENU_TEXTBOX_POS,
            DARK_BROWN,
            WHITE,
            horzCenter=True,
        )
        achieveText = TextBox(
            self.createAchievementText(),
            MAIN_MENU_TEXTBOX_POS,
            DARK_BROWN,
            WHITE,
            horzCenter=True,
        )
        self.buttons[MainMenu.TRAINING] = Button(
            "Training", (250, 135, 300, 50), trainerText
        )
        self.buttons[MainMenu.NEW_GAME] = Button(
            "Challenge", (250, 190, 300, 50), newGameText
        )
        self.buttons[MainMenu.ACHIEVEMENT] = Button(
            "Achievements", (250, 245, 300, 50), achieveText
        )
        self.buttons[MainMenu.EXIT_GAME] = Button("Exit", (250, 300, 300, 50))
        DISPLAYSURF.fill(WHITE)

    def refresh_achievements(self):
        user_data = UserData().get_user_data()
        self.buttons[MainMenu.ACHIEVEMENT].textBox.text = self.createAchievementText(
            user_data
        )

    def createAchievementText(self, userdata=None):
        # every time we create achievement text, we reread the file
        userdata = UserData().get_user_data()
        text = []
        if "name" in userdata:
            text.append(userdata["name"] + "'s Achievements")
        else:
            text.append("Guest Achievements")

        if "bestScore" in userdata:
            text.append("Highest Score: " + str(userdata["bestScore"]))
        else:
            text.append("Highest Score: 0")

        if "numVictories" in userdata:
            text.append("Victories: " + str(userdata["numVictories"]))
        else:
            text.append("Victories: 0")

        if "numGames" in userdata:
            text.append("Games Played: " + str(userdata["numGames"]))
        else:
            text.append("Games Played: 0")

        return text


# ==================== GAME MENU =====================


class GameMenu(Menu):
    PLAY_TURN = "play"
    RESHUFFLE = "shuffle"
    MAIN_MENU = "quit"
    HINT_TURN = "hint"

    def __init__(self, useHintBox=False):
        Menu.__init__(self)
        self.rect = (570, 300, 150, 300)
        playText = TextBox(
            ["Confirm your move,", "returns your tiles if", "your move is illegal."],
            (570, 480),
            DARK_BROWN,
            WHITE,
        )
        self.buttons[GameMenu.PLAY_TURN] = Button(
            "PLAY", (570, 300, 150, 30), textBox=playText
        )
        shuffleText = TextBox(
            ["Forfeit your turn", "and draw new tiles for", "the next turn."],
            (570, 480),
            DARK_BROWN,
            WHITE,
        )
        self.buttons[GameMenu.RESHUFFLE] = Button(
            "REDRAW", (570, 340, 150, 30), textBox=shuffleText
        )
        if useHintBox:
            hintText = TextBox(
                [
                    "The AI will put your",
                    "pieces down. Just hit",
                    "PLAY to confirm it.",
                ],
                (570, 480),
                DARK_BROWN,
                WHITE,
            )
            self.buttons[GameMenu.HINT_TURN] = Button(
                "HINT",
                (570, 380, 150, 30),
                textBox=hintText,
                color=(255, 255, 100),
                backColor=(255, 170, 50),
            )
            self.buttons[GameMenu.MAIN_MENU] = Button("QUIT", (570, 420, 150, 30))
        else:
            self.buttons[GameMenu.MAIN_MENU] = Button("QUIT", (570, 380, 150, 30))
        DISPLAYSURF.fill(WHITE)
