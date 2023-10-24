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
import pygame
import sys
import time
from pygame.locals import *

# local files
import ai
import bag
import board
import heuristic
import human
import player
import tile
from userdata import UserData

pygame.init()
tile.Tile.initialize()

# This part, I may have to import after pygame.init() in order to work
# import sound
from config import TIC, TICTIC, DINGDING, SCRIFFLE, CLICK
# import global variables
from config import DISPLAYSURF, ALPHASURF

#IMPORT THE MENU
import menu
from menu import MainMenu, GameMenu

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


def quit_game():
	pygame.quit()
	sys.exit()

##=====================MAIN======================
def main():
	def execute_menu():
		select = the_menu.get_selected_menu(*event.pos)
		if select == MainMenu.NEW_GAME: # menu Challenge
			new_game(user_data, the_menu)
		elif select == MainMenu.TRAINING: # menu Training
			runGame(user_data, useHintBox=True)
		elif select == MainMenu.EXIT_GAME:
			quit_game()

	user_data = UserData().get_user_data()
	the_menu = MainMenu(user_data)
	while True:
		# if training, start a new game automatically
		if TRAINING_FLAG:
			runGame(user_data, useHintBox=True)

		for event in pygame.event.get():
			if event.type == QUIT:
				quit_game()
			elif event.type == MOUSEMOTION: # mouse move
				the_menu.update_menu(*event.pos)
			elif event.type == MOUSEBUTTONUP: # mouse click
				execute_menu()

		the_menu.redraw()
		pygame.display.update()


def new_game(USERDATA, theMenu):
	USERDATA["numGames"] += 1
	# saveUser(USERDATA)
	UserData().save_user_data(USERDATA)
	theMenu.update_achievement(USERDATA)
	runGame(USERDATA)
	theMenu.update_achievement(USERDATA)



	
def runGame(USERDATA, useHintBox = False):	
	theBag = bag.Bag()
	theBoard = board.Board()

	h = heuristic.notEndGameHeuristic(heuristic.tileQuantileHeuristic(.5, 1.0))

	players = [
		human.Human("Player", theBoard, theBag),
		ai.AI(theBoard, theBag, theHeuristic=h, theDifficulty=10.0),
	]
	# Create an iterator that cycles through the list indefinitely

	active = 0
	# computerTurn = isinstance(players[active], ai.AI)
	firstTurn = True
	gameOver = False

	gameMenu = menu.GameMenu(useHintBox)

	redrawEverything(theBoard, players[active], players, gameOver, gameMenu)

	inHand = None
	stillPlaying = True
	AIstuck = False

	while stillPlaying:
		
		mouseClicked = False
		mouseMoved = False
		actionKeyHit = False
		shuffleKeyHit = False
		hintKeyHit = False

		current_player = players[active]

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
			elif event.type == KEYUP:
				if event.key in [K_SPACE, K_RETURN]:
					actionKeyHit = True
				if event.key == K_r:
					shuffleKeyHit = True
				if event.key == K_h and useHintBox:
					hintKeyHit = True

		#GAME MENU BUTTONS	
		if mouseMoved:
			gameMenu.update_menu(mouseX, mouseY)

		if mouseClicked:
			SELECTION = gameMenu.get_selected_menu(mouseX, mouseY)	

			if SELECTION == menu.GameMenu.PLAY_TURN:
				actionKeyHit = True
			elif SELECTION == menu.GameMenu.RESHUFFLE:
				shuffleKeyHit = True
			elif SELECTION == menu.GameMenu.HINT_TURN:
				hintKeyHit = True
			elif SELECTION == menu.GameMenu.MAIN_MENU:
				stillPlaying = False

		# Play hint, put tiles on board and wait for user's action whether user want to play as hinted
		if (hintKeyHit or TRAINING_FLAG) and not is_computer_turn(players, active) and not gameOver:
			place_hinted_tiles(theBoard, current_player, firstTurn)							

		# Play action
		if (actionKeyHit or TRAINING_FLAG or is_computer_turn(players, active)) and not gameOver:
			#If it's the computer turn, we need to process its move first!
			if is_computer_turn(players, active):
				playedMove = current_player.executeTurn(firstTurn, DISPLAYSURF)
			else:
				playedMove = True

			if playedMove:	

				success = current_player.play(firstTurn)
				if success == "END":
					gameOver = True
					endGame(players, active, useHintBox, USERDATA)
				elif success:
					DINGDING.play()
					current_player.pulseScore()
					firstTurn = False
					active += 1
					if active >= len(players):
						active = 0
					current_player = players[active]
					# computerTurn = isinstance(current_player, ai.AI)
					#If we were stuck before, we aren't anymore
					if is_computer_turn(players, active):
						AIstuck = False					
				else:
					if TRAINING_FLAG:
						AIstuck = True
					TICTIC.play()
					if is_computer_turn(players, active):
						print ("AI thinks it has a good move, but it doesn't")
			else:
				# ???
				print("shuffle")
				current_player.shuffle()
				#Let the player know the AI shuffled
				current_player.lastScore = 0
				current_player.pulseScore()
				if theBag.isEmpty():
					AIstuck = True

				active += 1
				if active >= len(players):
					active = 0
				current_player = players[active]
				# computerTurn = isinstance(current_player, ai.AI)

			redrawEverything(theBoard, players[active], players, gameOver, gameMenu)	

		if (shuffleKeyHit or (AIstuck and TRAINING_FLAG)) and not is_computer_turn(players, active) and not gameOver:
			SCRIFFLE.play()
			players[active].shuffle()
			active += 1
			if active >= len(players):
				active = 0
			# computerTurn = is_computer_turn(players, active)
			#If we're stuck AND the AI is stuck, end the game without subtracting points
			if AIstuck:
				gameOver = True
				endGame(players, active, useHintBox, USERDATA, stuck = True)
			redrawEverything(theBoard, players[active], players, gameOver, gameMenu)



		if mouseClicked and not is_computer_turn(players, active) and not gameOver:
			inHand = tileGrab(mouseX, mouseY, inHand, theBoard, players[active])
			redrawEverything(theBoard, players[active], players, gameOver, gameMenu)	

		if gameOver and TRAINING_FLAG: #automatically start a new game for training purposes
			stillPlaying = False

		redrawNecessary(theBoard, players, gameOver)
		pygame.display.update()

def is_computer_turn(players, active):
	return isinstance(players[active], ai.AI)

def place_hinted_tiles(theBoard, player, firstTurn):
	revert_played_tiles(theBoard, player)
	player.executeTurn(firstTurn, DISPLAYSURF)
	TICTIC.play()		

def revert_played_tiles(theBoard, player):
	print("revert_played_tiles")
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
Composite function which redraws everything
'''	
def redrawEverything(board, currentPlayer, players, gameOver, gameMenu):
	DISPLAYSURF.fill(BACKGROUND_COLOR)
	board.draw(DISPLAYSURF, ALPHASURF)
	currentPlayer.drawTray(DISPLAYSURF)	
	drawScore(players, gameOver)
	gameMenu.redraw()
	
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
			
		# saveUser(userdata)
		UserData().save_user_data(userdata)
	
	if TRAINING_FLAG:
		player.Player.aiStats.saveGame([p.score for p in players])
		player.Player.aiStats.save()
	
if __name__ == '__main__':
	main()