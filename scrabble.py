#This is the main scrabble program
'''
BUG
	- if redraw when there are tiles in the board, error occurs

Scrabble To-Do:

	- Apply State pattern for 2-screen board game (can ask chatGPT for explanation)
	- Make processing time delay as a function
	- Have generic "Player" account with achievements
	
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

'''

#local files
import board, tile, bag, player, human, ai, heuristic
from userdata import UserData

import pygame, random, sys, time
from pygame.locals import *

pygame.init()

#window setup
DISPLAYSURF = pygame.display.set_mode((800, 600))
ALPHASURF = DISPLAYSURF.convert_alpha()
pygame.display.set_caption('Wordsmith - Prapat edition')

tile.Tile.initialize()

#Simple sound effects
TIC = pygame.mixer.Sound('media/tic.ogg')
TICTIC = pygame.mixer.Sound('media/tictic.ogg')
DINGDING = pygame.mixer.Sound('media/dingding.ogg')
SCRIFFLE = pygame.mixer.Sound('media/scriffle.ogg')
CLICK = pygame.mixer.Sound('media/click.ogg')

#Achievements and data
USERFILE = 'media/user.txt'

#IMPORT THE MENU
import menu

# Event_state
from dataclasses import dataclass
@dataclass
class EventState:
	mouse_clicked: bool = False
	mouse_moved: bool = False
	action_key_hit: bool = False
	shuffle_key_hit: bool = False
	hint_key_hit: bool = False
	mouse_x: int = None
	mouse_y: int = None

#font setup
SCORE_FONT = pygame.font.Font('freesansbold.ttf', 20)
SCORE_LEFT = 570
SCORE_TOP = 100
SCORE_MARGIN = 25
SCORE_PULSE = 5.0

BACKGROUND_COLOR = (255, 255, 255)
SCORE_COLOR = (55, 46, 40)

#GAME MODES
TRAINING_FLAG = False #With this set to true, entering training mode causes the AI to play against
					  #itself automatically

#If training, make no sound					
if TRAINING_FLAG:
	TIC.set_volume(0.0)
	TICTIC.set_volume(0.0)
	DINGDING.set_volume(0.0)
	SCRIFFLE.set_volume(0.0)
	CLICK.set_volume(0.0)



##=====================MAIN======================
class ScrabbleGame:
	def __init__(self, useHintBox = False):
		self.the_bag = bag.Bag()
		self.the_board = board.Board()		
		h = heuristic.notEndGameHeuristic(heuristic.tileQuantileHeuristic(.5, 1.0))
		self.players = [
			human.Human("Player", self.the_board, self.the_bag),
			ai.AI(self.the_board, self.the_bag, theHeuristic=h, theDifficulty=10.0),
		]
		self.current_player = self.players[0]
		self.active = 0
		self.gameOver = False
		self.gameMenu = menu.GameMenu(useHintBox)
		self.event_state = EventState()
		self.still_playing = True
		self.user_data_file = UserData()

	def setup_game(self, useHintBox):
		self.firstTurn = True
		self.gameMenu = menu.GameMenu(useHintBox)
		self.redrawEverything()
		self.inHand = None
		self.still_playing = True
		self.AIstuck = False

	def prepare_turn(self):
		self.current_player = self.players[self.active]
		self.handle_events()

	def should_place_hinted_tiles(self):
		return (self.event_state.hint_key_hit or TRAINING_FLAG) and not self.is_computer_turn() and not self.gameOver

	def should_play_action(self):
		return (self.event_state.action_key_hit or TRAINING_FLAG or self.is_computer_turn()) and not self.gameOver
	
	def should_redraw(self):
		return (self.event_state.shuffle_key_hit or (self.AIstuck and TRAINING_FLAG)) and not self.is_computer_turn() and not self.gameOver

	def should_handle_mouse_clicked(self):
		return self.event_state.mouse_clicked and not self.is_computer_turn() and not self.gameOver

	def revert_played_tiles(self):
		tilesPulled = self.the_board.removeTempTiles()
		# if there are tiles back, put it back to the player
		if tilesPulled is not None:
			# Take the tiles back
			for tile in tilesPulled:
				self.current_player.take(tile)

	def place_hinted_tiles(self):
		"""	Play hint, put tiles on board and wait for user's action whether user want to play as hinted """
		self.revert_played_tiles()
		self.execute_current_player_turn()
		TICTIC.play()

	def execute_current_player_turn(self):
		return self.current_player.executeTurn(self.firstTurn, DISPLAYSURF)

	def change_current_player(self):
		self.active += 1
		if self.active >= len(self.players):
			self.active = 0
		self.current_player = self.players[self.active]	

	def redraw_tiles(self):
		"""
		Redraws the tiles for the current player, shuffles their tile rack, and changes the active player.
		If the AI is stuck and the player is also stuck, the game ends without subtracting points.
		"""
		SCRIFFLE.play()
		self.players[self.active].shuffle()
		self.change_current_player()
		#If we're stuck AND the AI is stuck, end the game without subtracting points
		if self.AIstuck:
			self.gameOver = True
			self.endGame(self.players, self.active, useHintBox, USERDATA, stuck = True)
		self.redrawEverything()
	
	def handle_computer_cannot_play_move(self):
		print("shuffle")
		self.current_player.shuffle()
		#Let the player know the AI shuffled
		self.current_player.lastScore = 0
		self.current_player.pulseScore()
		if self.the_bag.isEmpty():
			self.AIstuck = True
		self.change_current_player()

	def handle_end_game(self, useHintBox, USERDATA):
		self.gameOver = True
		self.endGame(self.players, self.active, useHintBox, USERDATA)

	def handle_successful_move(self):
		DINGDING.play()
		self.current_player.pulseScore()
		self.firstTurn = False
		self.change_current_player()
		if self.is_computer_turn():
			self.AIstuck = False

	def handle_unsuccessful_move(self):
		if TRAINING_FLAG:
			self.AIstuck = True
		TICTIC.play()
		if self.is_computer_turn():
			print ("AI thinks it has a good move, but it doesn't")

	def handle_played_move(self, useHintBox, USERDATA):
		success = self.current_player.play(self.firstTurn)
		if success == "END":
			self.handle_end_game(useHintBox, USERDATA)
		elif success:
			self.handle_successful_move()
		else:
			self.handle_unsuccessful_move()
					
	def play_action(self, useHintBox, USERDATA):
		playedMove = True
		#If it's the computer turn, we need to process its move first!
		if self.is_computer_turn():
			playedMove = self.execute_current_player_turn()

		if playedMove:	
			self.handle_played_move(useHintBox, USERDATA)
		else:
			# this one is not called when it's player turn
			# I think it's for AI turn
			self.handle_computer_cannot_play_move()

		self.redrawEverything()	

	def handle_no_tile_in_hand(self):
		tile = self.the_board.remove(self.event_state.mouse_x, self.event_state.mouse_y)
		if tile is None:
			tile = self.players[self.active].pickup(self.event_state.mouse_x, self.event_state.mouse_y)
			return tile if tile is not None else None
		else:
			TIC.play()
			self.players[self.active].take(tile)
			return None		

	def handle_tile_in_hand(self):
		(success, blank) = self.the_board.placeTentative(self.event_state.mouse_x, self.event_state.mouse_y, self.inHand)
		if success == False:
			return self.players[self.active].pickup(self.event_state.mouse_x, self.event_state.mouse_y)
		TIC.play()
		if success == "ASK":
			self.the_board.askForLetter(blank, DISPLAYSURF, ALPHASURF)
		self.players[self.active].placeTentative()
		return None
	
	def tileGrab(self):
		if self.inHand is None:
			return self.handle_no_tile_in_hand()
		else:
			return self.handle_tile_in_hand()

	def runGame(self, USERDATA, useHintBox = False):
		self.setup_game(useHintBox)
		while self.still_playing:
			self.prepare_turn()

			if self.should_place_hinted_tiles():
				self.place_hinted_tiles()						

			if self.should_play_action():
				self.play_action(useHintBox, USERDATA)

			if self.should_redraw():
				# FIXME: error when redraw when there are tentatives on the board
				self.redraw_tiles()

			if self.should_handle_mouse_clicked():
				self.inHand = self.tileGrab()
				self.redrawEverything()	

			if self.gameOver and TRAINING_FLAG: #automatically start a new game for training purposes
				self.still_playing = False

			self.redrawNecessary()
			pygame.display.update()

	'''
	Function which redraws only animated elements
	'''	
	def redrawNecessary(self):
		self.the_board.drawDirty(DISPLAYSURF, ALPHASURF)
		drawScore(self.players, self.gameOver)

	def handle_events(self):
		self.gather_events()
		self.handle_mouse_move()
		self.handle_mouse_click()
		return self.event_state

	def gather_events(self):
		# initialize new event state every time
		self.event_state = EventState()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.MOUSEMOTION:
				self.event_state.mouse_x, self.event_state.mouse_y = event.pos
				self.event_state.mouse_moved = True
			elif event.type == pygame.MOUSEBUTTONUP:
				self.event_state.mouse_x, self.event_state.mouse_y = event.pos
				self.event_state.mouse_clicked = True
			elif event.type == pygame.KEYUP:
				if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
					self.event_state.action_key_hit = True
				if event.key == pygame.K_r:
					self.event_state.shuffle_key_hit = True
				if event.key == pygame.K_h and self.game_menu.use_hint_box:
					self.event_state.hint_key_hit = True

	def handle_mouse_move(self):
		if self.event_state.mouse_moved:
			self.gameMenu.update(self.event_state.mouse_x, self.event_state.mouse_y)

	def handle_mouse_click(self):
		if self.event_state.mouse_clicked:
			SELECTION = self.gameMenu.execute(self.event_state.mouse_x, self.event_state.mouse_y)	

			if SELECTION == menu.GameMenu.PLAY_TURN:
				self.event_state.action_key_hit = True
			elif SELECTION == menu.GameMenu.RESHUFFLE:
				self.event_state.shuffle_key_hit = True
			elif SELECTION == menu.GameMenu.HINT_TURN:
				self.event_state.hint_key_hit = True
			elif SELECTION == menu.GameMenu.MAIN_MENU:
				self.still_playing = False	

	def is_computer_turn(self):
		return isinstance(self.current_player, ai.AI)	

	def redrawEverything(self):
		"""Composite function which redraws everything"""
		DISPLAYSURF.fill(BACKGROUND_COLOR)
		self.the_board.draw(DISPLAYSURF, ALPHASURF)
		self.current_player.drawTray(DISPLAYSURF)			
		drawScore(self.players, self.gameOver)
		self.gameMenu.redraw()

	'''
	Ends the game, taking the tray value from all unfinished players, subtracting the value
	from their score and giving it to the active player (who just finished)
	'''
	def endGame(self, players, active, isPractice, userdata, stuck = False):		
		#Do points swaps only if someone could finish
		if not stuck:
			i = 0
			surplus = 0
			for p in players:
				if i != active:
					value = p.trayValue()
					p.givePoints(-value)
					surplus += value
			players[active].givePoints(surplus)	
		
		if not isPractice:
			maxScore = -1
			maxPlayer = players[0]
			for p in players:
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
			player.Player.aiStats.saveGame([p.score for p in players])
			player.Player.aiStats.save()
class MainScreen:
	def __init__(self):
		# self.user_data = loadUser()
		self.user_data_file = UserData()
		self.user_data = self.user_data_file.get_user_data()
		self.menu = menu.MainMenu(self.user_data)
		self.selection = ""

	def handle_menu_selections(self):
		if self.selection == menu.MainMenu.NEW_GAME:
			self.new_game()
		elif self.selection == menu.MainMenu.TRAINING or TRAINING_FLAG:
			ScrabbleGame().runGame(self.user_data, useHintBox=True)
		elif self.selection == menu.MainMenu.EXIT_GAME:
			pygame.quit()
			sys.exit()

	def handle_pygame_events(self):
		self.selection = ""
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				self.menu.update(*event.pos)
			elif event.type == MOUSEBUTTONUP:
				self.selection = self.menu.execute(*event.pos)

	def new_game(self):
		self.user_data["numGames"] += 1
		self.user_data_file.save_user_data(self.user_data)
		# saveUser(self.user_data)
		self.menu.resetAchievements(self.user_data)
		ScrabbleGame().runGame(self.user_data)
		self.menu.resetAchievements(self.user_data)

	def run(self):
		while True:
			self.handle_pygame_events()
			self.handle_menu_selections()
			self.menu.redraw()
			pygame.display.update()

'''
This resolves the action of the player to try to pick up a tile. Two situations:
1) The player has a piece in hand:
	-If it's on the board, attempt to place the piece there. If it doesn't work,
	 do nothing. If it does work, empty the hand and update the board
	-If it's on the tray, swap positions and set the hand to none
2) The player doesn't have a piece in hand:
	-If it's on the board and the piece is not locked, return it to the tray (at the end)
	-If it's on the tray, highlight that piece and put it in hand.
'''

'''
Function which redraws only animated elements
'''	
# def redrawNecessary(board, players, gameOver):
# 	board.drawDirty(DISPLAYSURF, ALPHASURF)
# 	drawScore(players, gameOver)
		
'''
Draws the scores
'''
def drawScore(players, gameOver):
	i = 0
	left = SCORE_LEFT
	for player in players:
		top = SCORE_TOP + SCORE_MARGIN * i
		
		sentence = player.name + ": " + str(player.score)
		
		scoreText = SCORE_FONT.render(sentence, True, SCORE_COLOR, BACKGROUND_COLOR)
		scoreRect = scoreText.get_rect()
		scoreRect.left = left
		scoreRect.top = top
		DISPLAYSURF.blit(scoreText, scoreRect)
		
		#Score Pulse
		if time.time() - player.lastScorePulse < SCORE_PULSE:
			tween = (time.time()-player.lastScorePulse) / SCORE_PULSE
			color = (SCORE_COLOR[0]*(1-tween) + BACKGROUND_COLOR[0]*tween,
					SCORE_COLOR[1]*(1-tween) + BACKGROUND_COLOR[1]*tween,
					SCORE_COLOR[2]*(1-tween) + BACKGROUND_COLOR[2]*tween)
			pulseText = SCORE_FONT.render("(+"+str(player.lastScore)+")", True, color, BACKGROUND_COLOR)
			pulseRect = pulseText.get_rect()
			pulseRect.left = scoreRect.right + 10
			pulseRect.top = top
			DISPLAYSURF.blit(pulseText, pulseRect)
				
		i += 1
	
	#Let players know the game is over!
	if gameOver:
		scoreText = SCORE_FONT.render("Game finished!", True, SCORE_COLOR, BACKGROUND_COLOR)
		scoreRect = scoreText.get_rect()
		scoreRect.left = left
		scoreRect.top = SCORE_TOP + SCORE_MARGIN * i
		DISPLAYSURF.blit(scoreText, scoreRect)		
	
def main():
	main_screen = MainScreen().run()
	
##===============================================
if __name__ == '__main__':
	main()