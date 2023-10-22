#This is the main scrabble program
'''
Scrabble To-Do:

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


import pygame, random, sys, time
from pygame.locals import *

#local files
import board, tile, bag, player, human, ai, heuristic

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

	def as_tuple(self):
		return (self.mouse_clicked, self.mouse_moved, self.action_key_hit, 
				self.shuffle_key_hit, self.hint_key_hit, self.mouse_x, self.mouse_y)

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

	def runGame(self, USERDATA, useHintBox = False):
		players = self.players
		firstTurn = True
		self.gameMenu = menu.GameMenu(useHintBox)
		self.redrawEverything()

		inHand = None
		self.still_playing = True
		AIstuck = False

		while self.still_playing:
			self.current_player = players[self.active]
			mouse_clicked, mouse_moved, actionKeyHit, shuffleKeyHit, hintKeyHit, mouseX, mouseY = self.handle_events().as_tuple()
			#GAME MENU BUTTONS	
			# if mouse_moved:
			# 	self.gameMenu.update(mouseX, mouseY)

			if mouse_clicked:
				SELECTION = self.gameMenu.execute(mouseX, mouseY)	

				if SELECTION == menu.GameMenu.PLAY_TURN:
					actionKeyHit = True
				elif SELECTION == menu.GameMenu.RESHUFFLE:
					shuffleKeyHit = True
				elif SELECTION == menu.GameMenu.HINT_TURN:
					hintKeyHit = True
				elif SELECTION == menu.GameMenu.MAIN_MENU:
					self.stillPlaying = False

			# Play hint, put tiles on board and wait for user's action whether user want to play as hinted
			if (hintKeyHit or TRAINING_FLAG) and not self.is_computer_turn() and not self.gameOver:
				place_hinted_tiles(self.the_board, self.current_player, firstTurn)							

			# Play action
			if (actionKeyHit or TRAINING_FLAG or self.is_computer_turn()) and not self.gameOver:
				#If it's the computer turn, we need to process its move first!
				if self.is_computer_turn():
					playedMove = self.current_player.executeTurn(firstTurn, DISPLAYSURF)
				else:
					playedMove = True

				if playedMove:	

					success = self.current_player.play(firstTurn)
					if success == "END":
						self.gameOver = True
						endGame(players, self.active, useHintBox, USERDATA)
					elif success:
						DINGDING.play()
						self.current_player.pulseScore()
						firstTurn = False
						# self.current_player = next_player(players, active)
						self.active += 1
						if self.active >= len(players):
							self.active = 0
						self.current_player = players[self.active]
						#If we were stuck before, we aren't anymore
						if self.is_computer_turn():
							AIstuck = False					
					else:
						if TRAINING_FLAG:
							AIstuck = True
						TICTIC.play()
						if self.is_computer_turn():
							print ("AI thinks it has a good move, but it doesn't")
				else:
					# ???
					print("shuffle")
					self.current_player.shuffle()
					#Let the player know the AI shuffled
					self.current_player.lastScore = 0
					self.current_player.pulseScore()
					if self.the_bag.isEmpty():
						AIstuck = True
					self.current_player = self.next_player()

				self.redrawEverything()	

			if (shuffleKeyHit or (AIstuck and TRAINING_FLAG)) and not self.is_computer_turn() and not self.gameOver:
				SCRIFFLE.play()
				players[self.active].shuffle()
				self.current_player = self.next_player()
				#If we're stuck AND the AI is stuck, end the game without subtracting points
				if AIstuck:
					self.gameOver = True
					endGame(players, self.active, useHintBox, USERDATA, stuck = True)
				self.redrawEverything()

			if mouse_clicked and not self.is_computer_turn() and not self.gameOver:
				inHand = tileGrab(mouseX, mouseY, inHand, self.the_board, players[self.active])
				self.redrawEverything()	

			if self.gameOver and TRAINING_FLAG: #automatically start a new game for training purposes
				self.still_playing = False

			redrawNecessary(self.the_board, players, self.gameOver)
			pygame.display.update()


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
				self.event_state.actionKeyHit = True
			elif SELECTION == menu.GameMenu.RESHUFFLE:
				self.event_state.shuffleKeyHit = True
			elif SELECTION == menu.GameMenu.HINT_TURN:
				self.event_state.hintKeyHit = True
			elif SELECTION == menu.GameMenu.MAIN_MENU:
				self.still_playing = False	

	def is_computer_turn(self):
		return isinstance(self.current_player, ai.AI)
	
	def next_player(self):
		# toggle active player
		self.active = 1 - self.active
		return self.players[self.active]	

	def redrawEverything(self):
		"""Composite function which redraws everything"""
		DISPLAYSURF.fill(BACKGROUND_COLOR)
		self.the_board.draw(DISPLAYSURF, ALPHASURF)
		self.current_player.drawTray(DISPLAYSURF)			
		drawScore(self.players, self.gameOver)
		self.gameMenu.redraw()

def main():
	USERDATA = loadUser()
	game = ScrabbleGame()
	theMenu = menu.MainMenu(USERDATA)
	while True:
		mouseClicked = False
		mouseMoved = False
		SELECTION = ""
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				mouseX, mouseY = event.pos
				mouseMoved = True
			elif event.type == MOUSEBUTTONUP:
				mouseX, mouseY = event.pos
				mouseClicked = True

		if mouseClicked:
			SELECTION = theMenu.execute(mouseX, mouseY)

		if mouseMoved:
			theMenu.update(mouseX, mouseY)

		if SELECTION == menu.MainMenu.NEW_GAME:
			new_game(USERDATA, theMenu)
		elif SELECTION == menu.MainMenu.TRAINING or TRAINING_FLAG:
			game.runGame(USERDATA, useHintBox=True)
			# theMenu.redraw()
		elif SELECTION == menu.MainMenu.EXIT_GAME:
			pygame.quit()
			sys.exit()
		theMenu.redraw()
		pygame.display.update()


def new_game(USERDATA, theMenu):
	USERDATA["numGames"] += 1
	saveUser(USERDATA)
	theMenu.resetAchievements(USERDATA)
	ScrabbleGame().runGame(USERDATA)
	theMenu.resetAchievements(USERDATA)

def place_hinted_tiles(theBoard, player, firstTurn):
	revert_played_tiles(theBoard, player)
	player.executeTurn(firstTurn, DISPLAYSURF)
	TICTIC.play()		

def revert_played_tiles(theBoard, player):
	tilesPulled = theBoard.removeTempTiles()
	# if there are tiles back, put it back to the player
	if tilesPulled is not None:
		# Take the tiles back
		for tile in tilesPulled:
			player.take(tile)	

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

def tileGrab(x, y, hand, theBoard, theHuman):
	"""
	Grab a tile from the board or the player's hand.

	Args:
		x (int): The x-coordinate of the tile.
		y (int): The y-coordinate of the tile.
		hand (list): The player's hand.
		theBoard (Board): The game board.
		theHuman (Player): The player.

	Returns:
		Tile or None: The grabbed tile, or None if no tile was grabbed.

	If the player's hand is empty, try to remove a tile from the board. If that fails, try to remove a tile from the tray.
	If the player's hand is not empty, try to place the tile on the board. If successful, place a tentative piece on the board.
	"""

	if hand is None:
		tile = theBoard.remove(x, y) # try to remove a piece from the board
		if tile is None:
			tile = theHuman.pickup(x, y) # if it didn't, try to remove from the tray
			return tile if tile != None else None
		else:
			TIC.play()
			theHuman.take(tile)		# if it worked, put it back on our tray
			return None
	else:
		(success, blank) = theBoard.placeTentative(x, y, hand) #try to place the tile on the board
		if success == False:
			return theHuman.pickup(x, y)
		TIC.play()
		if success == "ASK":
			theBoard.askForLetter(blank, DISPLAYSURF, ALPHASURF)
		theHuman.placeTentative()	#if it's successful place a tentative piece
		return None					#empty the hand

'''
Function which redraws only animated elements
'''	
def redrawNecessary(board, players, gameOver):
	board.drawDirty(DISPLAYSURF, ALPHASURF)
	drawScore(players, gameOver)
		
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
		
'''
Ends the game, taking the tray value from all unfinished players, subtracting the value
from their score and giving it to the active player (who just finished)
'''
def endGame(players, active, isPractice, userdata, stuck = False):
	
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
			
		saveUser(userdata)
	
	if TRAINING_FLAG:
		player.Player.aiStats.saveGame([p.score for p in players])
		player.Player.aiStats.save()
	
	
def loadUser():
	userFile = open(USERFILE, 'r')
	i = 0
	userdata = {}
	userdata["name"] = "Guest"
	userdata["bestScore"] = 0
	userdata["numVictories"] = 0
	userdata["numGames"] = 0
	for line in userFile:
		line = line.rstrip()
		if i == 0:
			userdata["name"] = line
		elif i == 1:
			userdata["bestScore"] = int(line)
		elif i == 2:
			userdata["numVictories"] = int(line)
		elif i == 3:
			userdata["numGames"] = int(line)
			
		i += 1
			
	return userdata
	
def saveUser(USERDATA):
	userFile = open(USERFILE, 'w')
	if "name" in USERDATA:
		userFile.write(str(USERDATA["name"])+"\n")
	else:
		userFile.write("Guest\n")
	
	if "bestScore" in USERDATA:
		userFile.write(str(USERDATA["bestScore"])+"\n")
	else:
		userFile.write("0\n")	
		
	if "numVictories" in USERDATA:
		userFile.write(str(USERDATA["numVictories"])+"\n")
	else:
		userFile.write("0\n")

	if "numGames" in USERDATA:
		userFile.write(str(USERDATA["numGames"])+"\n")
	else:
		userFile.write("0\n")	

##===============================================
##===============================================
if __name__ == '__main__':
	main()