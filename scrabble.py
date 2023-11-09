# This is the main scrabble program
"""
BUG
	- if redraw when there are tiles in the board, error occurs

Scrabble To-Do:

	- Apply State pattern for 2-screen board game (can ask chatGPT for explanation)
	- Make processing time delay as a function
	- Have generic "Player" account with achievements
	- Refactor more on endGame method
	
Heuristic ideas:

	IDEA: Conserved play of high letters Q, Z, J, X
	- Figure out word score 'bonus' for high-letter tiles, on average
	
	IDEA: Conserved play of flexible letters S and BLANK
	- Figure out average word score 'bonus' for having a blank or S
	
	IDEA: Open plays (which create significantly more seed positions) should be discouraged
	- Store the seed list and update it with tile slots, deduct points for words which add too much
	
	IDEA: Hanging plays (which create advantageous seed positions) should be penalized
	- For each new seed generated (and subtracted for each seed removed) figure out the 
	  letter and words scores accessible and subtract points

"""

# local files
from dataclasses import dataclass
import menu
from menu import MainMenu, GameMenu
import board
import tile
import bag
import player
import human
import ai
import heuristic
from userdata import UserData

import pygame
import sys
import time
from itertools import cycle
from pygame.locals import *

from gui import DISPLAYSURF, ALPHASURF, TIC, TICTIC, DINGDING, SCRIFFLE, CLICK
from gui import DARK_BROWN, WHITE
from collections import namedtuple

tile.Tile.initialize()

MousePosition = namedtuple("mouse_position", ["x", "y"])

# Initialize logger
# In another module or part of your code
import logging

# Configure the logger
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
# # Configure the logger
# logging.basicConfig(filename='example.log',
#                     level=logging.DEBUG,
#                     filemode='w',  # 'w' for write mode, 'a' for append mode
#                     format='%(asctime)s - %(levelname)s - %(message)s')

# Get the logger with the same name ('scrabble_app') that you created earlier
logger = logging.getLogger("scrabble_app")
logger.setLevel(logging.DEBUG)


# Event_state
@dataclass
class EventState:
    mouse_clicked: bool = False
    action_key_hit: bool = False
    shuffle_key_hit: bool = False
    ask_hint: bool = False
    mouse_x: int = None
    mouse_y: int = None
    mouse_position: MousePosition = None


# font setup
SCORE_FONT = pygame.font.Font("freesansbold.ttf", 20)
SCORE_LEFT = 570
SCORE_TOP = 100
SCORE_MARGIN = 25
SCORE_PULSE = 5.0

BACKGROUND_COLOR = WHITE
SCORE_COLOR = DARK_BROWN

# GAME MODES
# With this set to true, entering training mode causes the AI to play against
# itself automatically
TRAINING_FLAG = False
# TRAINING_FLAG = True

# If training, make no sound
if TRAINING_FLAG:
    TIC.set_volume(0.0)
    TICTIC.set_volume(0.0)
    DINGDING.set_volume(0.0)
    SCRIFFLE.set_volume(0.0)
    CLICK.set_volume(0.0)


# =====================MAIN======================
class ScrabbleGame:
    def __init__(self, useHintBox=False):
        self.the_bag = bag.Bag()
        self.the_board = board.Board()
        h = heuristic.notEndGameHeuristic(heuristic.tileQuantileHeuristic(0.5, 1.0))
        self.players = [
            human.Human("Player", self.the_board, self.the_bag),
            ai.AI(self.the_board, self.the_bag, theHeuristic=h, theDifficulty=10.0),
        ]
        self.players_iterator = cycle(self.players)
        self.active = 0
        self.current_player = self.next_player()  # must run after setting self.active
        self.gameOver = False
        self.event_state = EventState()
        self.user_data_file = UserData()

        self.setup_game(useHintBox)

    def setup_game(self, useHintBox):
        self.firstTurn = True
        self.gameMenu = GameMenu(useHintBox)
        self.redrawEverything()
        self.inHand = None
        self.still_playing = True
        self.AIstuck = False

    def get_current_player(self):
        return self.current_player

    def ask_for_hint(self):
        """return true if user hit hint box or training flag is on and it's not computer turn"""
        return (
            (self.event_state.ask_hint or TRAINING_FLAG)
            and not self.is_computer_turn()
            and not self.gameOver
        )

    def should_play_action(self):
        return (
            self.event_state.action_key_hit or TRAINING_FLAG or self.is_computer_turn()
        ) and not self.gameOver

    def should_redraw(self):
        return (
            (self.event_state.shuffle_key_hit or (self.AIstuck and TRAINING_FLAG))
            and not self.is_computer_turn()
            and not self.gameOver
        )

    def should_handle_mouse_clicked(self):
        return (
            self.event_state.mouse_clicked
            and not self.is_computer_turn()
            and not self.gameOver
        )

    def pull_tiles_back_to_tray(self):
        """if there are tiles on board, pull tiles back to tray"""
        tilesPulled = self.the_board.removeTempTiles()
        # if there are tiles back, put it back to the player
        if tilesPulled is not None:
            # Take the tiles back
            for tile in tilesPulled:
                self.get_current_player().take(tile)

    def place_hinted_tiles(self):
        """Play hint, put tiles on board and wait for user's action whether user want to play as hinted"""
        # self.pull_tiles_back_to_tray()
        self.execute_current_player_turn()
        TICTIC.play()

    def execute_current_player_turn(self):
        return self.get_current_player().executeTurn(self.firstTurn, DISPLAYSURF)

    def next_player(self):
        self.active += 1
        if self.active >= len(self.players):
            self.active = 0
        self.current_player = next(self.players_iterator)
        return self.current_player

    def redraw_tiles(self):
        """
        Redraws the tiles for the current player, shuffles their tile rack, and changes the active player.
        If the AI is stuck and the player is also stuck, the game ends without subtracting points.
        """
        SCRIFFLE.play()
        self.get_current_player().shuffle()
        self.next_player()
        # If we're stuck AND the AI is stuck, end the game without subtracting points
        if self.AIstuck:
            self.gameOver = True
            self.endGame(useHintBox, USERDATA, stuck=True)
        self.redrawEverything()

    def handle_computer_cannot_play_move(self):
        print("shuffle")
        self.get_current_player().shuffle()
        # Let the player know the AI shuffled
        self.get_current_player().lastScore = 0
        self.get_current_player().pulseScore()
        if self.the_bag.isEmpty():
            self.AIstuck = True
        self.next_player()

    def handle_end_game(self, useHintBox):
        self.gameOver = True
        self.endGame(useHintBox)

    def handle_successful_move(self):
        DINGDING.play()
        self.get_current_player().pulseScore()
        self.firstTurn = False
        self.next_player()
        if self.is_computer_turn():
            self.AIstuck = False

    def handle_unsuccessful_move(self):
        if TRAINING_FLAG:
            self.AIstuck = True
        TICTIC.play()
        if self.is_computer_turn():
            print("AI thinks it has a good move, but it doesn't")

    def handle_played_move(self, useHintBox):
        success = self.get_current_player().play(self.firstTurn)
        if success == "END":
            self.handle_end_game(useHintBox)
        elif success:
            self.handle_successful_move()
        else:
            self.handle_unsuccessful_move()

    def play_action(self, useHintBox):
        USERDATA = self.user_data_file.get_user_data()
        playedMove = True
        # If it's the computer turn, we need to process its move first!
        if self.is_computer_turn():
            playedMove = self.execute_current_player_turn()

        if playedMove:
            self.handle_played_move(useHintBox)
        else:
            # this one is not called when it's player turn
            # I think it's for AI turn
            self.handle_computer_cannot_play_move()

        self.redrawEverything()

    def handle_no_tile_in_hand(self):
        # if there is no tile in hand
        # if click on the board, pick up tile from board
        # and put back to the tray
        tile = self.the_board.remove(self.event_state.mouse_x, self.event_state.mouse_y)
        if tile is None:
            tile = self.get_current_player().pickup(
                self.event_state.mouse_x, self.event_state.mouse_y
            )
            return tile if tile is not None else None
        else:
            # if click on the tray, pick up tile from tray?
            TIC.play()
            self.get_current_player().take(tile)
            return None

    def handle_tile_in_hand(self):
        (success, blank) = self.the_board.placeTentative(
            self.event_state.mouse_x, self.event_state.mouse_y, self.inHand
        )
        assert blank is self.inHand
        if success == False:
            return self.get_current_player().pickup(
                self.event_state.mouse_x, self.event_state.mouse_y
            )
        TIC.play()
        if success == "ASK":
            self.the_board.askForLetter(blank, DISPLAYSURF, ALPHASURF)
        self.get_current_player().placeTentative()
        return None

    def tileGrab(self):
        # if there is no tile in hand
        if self.inHand is None:
            return self.handle_no_tile_in_hand()
        else:
            # if there is tile in hand
            return self.handle_tile_in_hand()

    def runGame(self, useHintBox=False):
        # USERDATA = self.user_data_file.get_user_data()
        # Start a new game
        self.setup_game(useHintBox)

        # main game loop
        while self.still_playing:
            self.handle_events()

            if self.ask_for_hint():
                # take back what's already on the board
                self.pull_tiles_back_to_tray()
                # place hinted tiles
                self.place_hinted_tiles()

            if self.should_play_action():
                self.play_action(useHintBox)

            if self.should_redraw():
                # FIXME: error when redraw when there are tentatives on the board
                self.redraw_tiles()

            if self.should_handle_mouse_clicked():
                # note: what can happend when mouse clicked
                # 1. pick up tile from board
                # 2. pick up tile from tray
                # 3. place tile on board
                # 4. place tile on tray

                self.inHand = self.tileGrab()
                # ?:why redraw everything here
                self.redrawEverything()

            if (
                self.gameOver and TRAINING_FLAG
            ):  # automatically start a new game for training purposes
                self.still_playing = False

            self.redrawNecessary()
            pygame.display.update()

    """
	Function which redraws only animated elements
	"""

    def redrawNecessary(self):
        self.the_board.drawDirty(DISPLAYSURF, ALPHASURF)
        self.drawScore()

    def draw_text(self, text, left, top, color):
        """draw text and return rect of the draw area"""
        rendered_text = SCORE_FONT.render(text, True, color, BACKGROUND_COLOR)
        text_rect = rendered_text.get_rect()
        text_rect.left = left
        text_rect.top = top
        DISPLAYSURF.blit(rendered_text, text_rect)
        return text_rect

    def get_pulse_color(self, tween):
        """Calculate the pulse color based on the tween value."""
        return tuple(
            int(SCORE_COLOR[i] * (1 - tween) + BACKGROUND_COLOR[i] * tween)
            for i in range(3)
        )

    def drawScore(self):
        """Draws the score for each player"""
        for i, player in enumerate(self.players):
            top = SCORE_TOP + SCORE_MARGIN * i
            sentence = f"{player.name}: {player.score}"
            score_rect = self.draw_text(sentence, SCORE_LEFT, top, SCORE_COLOR)

            # Score Pulse
            elapsed_time = time.time() - player.lastScorePulse
            if elapsed_time < SCORE_PULSE:
                tween = elapsed_time / SCORE_PULSE
                color = self.get_pulse_color(tween)
                pulse_text = f"(+{player.lastScore})"
                self.draw_text(pulse_text, score_rect.right + 10, top, color)

        # Let players know the game is over!
        if self.gameOver:
            game_over_msg = "Game finished!"
            self.draw_text(
                game_over_msg,
                SCORE_LEFT,
                SCORE_TOP + SCORE_MARGIN * len(self.players),
                SCORE_COLOR,
            )

    def handle_events(self):
        self.gather_events()
        return self.event_state

    def gather_events(self):
        # initialize new event state every time
        self.event_state = EventState()
        selected_menu = None
        for event in pygame.event.get():
            # if click on the close button
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                self.event_state.mouse_x, self.event_state.mouse_y = event.pos
                # update menu highlight
                self.gameMenu.update(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.event_state.mouse_x, self.event_state.mouse_y = event.pos
                self.event_state.mouse_clicked = True
                selected_menu = self.gameMenu.get_selected_menu(event.pos)
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                    self.event_state.action_key_hit = True
                if event.key == pygame.K_r:
                    self.event_state.shuffle_key_hit = True
                if event.key == pygame.K_h and self.game_menu.use_hint_box:
                    self.event_state.ask_hint = True

            # set event_state based on selected menu
            # require python 3.10+ to use match case
            match selected_menu:
                case GameMenu.PLAY_TURN:
                    self.event_state.action_key_hit = True
                case GameMenu.RESHUFFLE:
                    self.event_state.shuffle_key_hit = True
                case GameMenu.HINT_TURN:
                    self.event_state.ask_hint = True
                case GameMenu.MAIN_MENU:
                    self.still_playing = False

    def is_computer_turn(self):
        return isinstance(self.get_current_player(), ai.AI)

    def redrawEverything(self):
        """Composite function which redraws everything"""
        DISPLAYSURF.fill(BACKGROUND_COLOR)
        self.the_board.draw(DISPLAYSURF, ALPHASURF)
        self.get_current_player().drawTray(DISPLAYSURF)
        self.drawScore()
        self.gameMenu.display()

    def swap_points(self):
        surplus = 0
        i = 0
        for player in self.players:
            if i != self.active:
                value = player.tray_value()
                player.give_points(-value)
                surplus += value

        self.players[self.active].give_points(surplus)

    """
	Ends the game, taking the tray value from all unfinished players, subtracting the value
	from their score and giving it to the active player (who just finished)
	"""

    def endGame(self, isPractice, stuck=False):
        userdata = self.user_data_file.get_user_data()
        # Do points swaps only if someone could finish
        # if not stuck:
        # 	self.swap_points()
        if not stuck:
            i = 0
            surplus = 0
            for p in self.players:
                if i != self.active:
                    value = p.trayValue()
                    p.givePoints(-value)
                    surplus += value
            self.players[self.active].givePoints(surplus)

        if not isPractice:
            maxScore = -1
            maxPlayer = self.players[0]
            for p in self.players:
                if isinstance(p, human.Human):
                    if "bestScore" in userdata and p.score > userdata["bestScore"]:
                        userdata["bestScore"] = p.score
                if p.score > maxScore:
                    maxPlayer = p
                    maxScore = p.score

            if isinstance(maxPlayer, human.Human):
                if "numVictories" in userdata:
                    userdata["numVictories"] += 1

            # saveUser(userdata)
            self.user_data_file.save_user_data(userdata)

        if TRAINING_FLAG:
            player.Player.aiStats.saveGame([p.score for p in self.players])
            player.Player.aiStats.save()


class MainScreen:
    def __init__(self):
        self.menu = MainMenu()

    def play_as_challenge(self):
        UserData().increase_gameplay()
        ScrabbleGame().runGame()
        self.menu.refresh_achievements()

    def highlight_hovered_menu(self, mouse_pos):
        self.menu.update(mouse_pos)

    def act_based_on_selected_menu(self, selected_menu):
        if selected_menu == MainMenu.NEW_GAME:
            self.play_as_challenge()
        elif selected_menu == MainMenu.TRAINING:
            ScrabbleGame().runGame(useHintBox=True)

    def run(self):
        logger.info("Starting Scrabble")
        while True:
            for event in pygame.event.get():
                if event.type == MOUSEMOTION:
                    self.highlight_hovered_menu(event.pos)

                selected_menu = ""
                if event.type == MOUSEBUTTONUP:
                    selected_menu = self.menu.get_selected_menu(event.pos)
                    self.act_based_on_selected_menu(selected_menu)
                    self.menu.display()  # redraw the whole menu after coming back from a game

                if event.type == QUIT or selected_menu == MainMenu.EXIT_GAME:
                    pygame.quit()
                    sys.exit()

                if TRAINING_FLAG:
                    ScrabbleGame().runGame(useHintBox=True)
                pygame.display.flip()
            pygame.time.Clock().tick(30)  # cap the frame rate 30 fps


"""
This resolves the action of the player to try to pick up a tile. Two situations:
1) The player has a piece in hand:
	-If it's on the board, attempt to place the piece there. If it doesn't work,
	 do nothing. If it does work, empty the hand and update the board
	-If it's on the tray, swap positions and set the hand to none
2) The player doesn't have a piece in hand:
	-If it's on the board and the piece is not locked, return it to the tray (at the end)
	-If it's on the tray, highlight that piece and put it in hand.
"""

if __name__ == "__main__":
    if sys.version_info < (3, 10):
        print("This program requires Python 3.10 or later.")
        sys.exit(1)
    MainScreen().run()
