'''
This will store any menus all inherited from a prototype with two functions
update and execute. Update will change display based on cursor position, while
execute will process button clicks.
'''

import pygame

from config import DISPLAYSURF, CLICK
from userdata import UserData

class Menu():
	
	def __init__(self):
		self.buttons = {}
		self.rect = (0, 0, 800, 600)
		self.background = (255, 255, 255)
	
	'''
	Goes through all buttons and returns the name of the button, if it was clicked
	'''
	def get_selected_menu(self, mouseX, mouseY):
		if self.within(mouseX, mouseY):
			theKey = ""
			for key in list(self.buttons.keys()):
				if self.buttons[key].within((mouseX, mouseY)):
					theKey = key
		
			# if a menu button was clicked, play the click sound
			if theKey != "":
				CLICK.play()
					
			return theKey
	
	'''
	Goes through and updates all buttons, redrawing them if they are hovered
	'''	
	def update_menu(self, mouseX, mouseY):
		for button in list(self.buttons.values()):
			# button.update(mouseX, mouseY)
			button.update((mouseX, mouseY))
			
	def within(self, mouseX, mouseY):
		(left, top, width, height) = self.rect
		return mouseX >= left and mouseX <= left+width and mouseY >= top and mouseY <= top+height	
		
	def redraw(self):
		pygame.draw.rect(DISPLAYSURF, self.background, self.rect)
		for button in list(self.buttons.values()):
			button.redraw()		

#==================== MAIN MENU =====================
		
class MainMenu(Menu):
	
	NEW_GAME = "new"
	EXIT_GAME = "exit"
	TRAINING = "training"
	ACHIEVEMENT = "achievement"
	
	def __init__(self, userdata):
		Menu.__init__(self)
		trainerText = TextBox(["Practice your Scrabble skills with a built-in HINT",
								"box, which lets you know how the AI would have played",
								"your move. But you can't get ACHIEVEMENTS while training."], (400, 400), 
							(55, 46, 40), (255, 255, 255), horzCenter = True)
		newGameText = TextBox(["Play one-on-one against Wordsmith, the Scrabble AI.",
								"No hints allowed, try to beat your best score!"], (400, 400), 
							(55, 46, 40), (255, 255, 255), horzCenter = True)
		achieveText = TextBox(self.createAchievementText(), (400, 400), 
							(55, 46, 40), (255, 255, 255), horzCenter = True)
		self.buttons[MainMenu.TRAINING] = Button("Training", (250, 135, 300, 50), trainerText)
		self.buttons[MainMenu.NEW_GAME] = Button("Challenge", (250, 190, 300, 50), newGameText)
		self.buttons[MainMenu.ACHIEVEMENT] = Button("Achievements", (250, 245, 300, 50), achieveText)
		self.buttons[MainMenu.EXIT_GAME] = Button("Exit", (250, 300, 300, 50))
		DISPLAYSURF.fill((255,255,255))
		
	def update_achievement(self, userdata):
		""" display the achievement on screen """
		print("update_achievement")
		userdata = UserData().get_user_data()
		self.buttons[MainMenu.ACHIEVEMENT].text_box.text = self.createAchievementText(userdata)
		
	def createAchievementText(self):
		print("createAchievementText")
		userdata = UserData().get_user_data()
		text = []
		if "name" in userdata:
			text.append(userdata["name"]+"'s Achievements")
		else:
			text.append("Guest Achievements")

		if "bestScore" in userdata:
			text.append("Highest Score: "+str(userdata["bestScore"]))
		else:
			text.append("Highest Score: 0")	

		if "numVictories" in userdata:
			text.append("Victories: "+str(userdata["numVictories"]))
		else:
			text.append("Victories: 0")

		if "numGames" in userdata:
			text.append("Games Played: "+str(userdata["numGames"]))
		else:
			text.append("Games Played: 0")	

		print(text)	
		return text
		
		
#==================== GAME MENU =====================

class GameMenu(Menu):

	PLAY_TURN = "play"
	RESHUFFLE = "shuffle"
	MAIN_MENU = "quit"
	HINT_TURN = "hint"

	def __init__(self, useHintBox = False):
		Menu.__init__(self)
		self.rect = (570, 300, 150, 300)
		playText = TextBox(["Confirm your move,",
							"returns your tiles if",
							"your move is illegal."], (570, 480), (55, 46, 40), (255, 255, 255))
		self.buttons[GameMenu.PLAY_TURN] = Button("PLAY", (570, 300, 150, 30), text_box = playText)
		shuffleText = TextBox(["Forfeit your turn",
							"and draw new tiles for",
							"the next turn."], (570, 480), (55, 46, 40), (255, 255, 255))
		self.buttons[GameMenu.RESHUFFLE] = Button("REDRAW", (570, 340, 150, 30), text_box = shuffleText)
		if useHintBox:
			hintText = TextBox(["The AI will put your",
								"pieces down. Just hit",
								"PLAY to confirm it."], (570, 480), (55, 46, 40), (255, 255, 255))
			self.buttons[GameMenu.HINT_TURN] = Button("HINT", (570, 380, 150, 30), text_box = hintText, color = (255, 255, 100), back_color = (255, 170, 50))
			self.buttons[GameMenu.MAIN_MENU] = Button("QUIT", (570, 420, 150, 30))
		else:
			self.buttons[GameMenu.MAIN_MENU] = Button("QUIT", (570, 380, 150, 30))
		DISPLAYSURF.fill((255,255,255))		
		
#==================== TEXT BOX ======================
class TextBox():
	
	initialized = False
	MARGIN = 21
	
	@staticmethod
	def initialize():
		TextBox.FONT = pygame.font.Font('freesansbold.ttf', 18)
		TextBox.initialized = True
		

	def __init__(self, textLines, pos, color, backColor, horzCenter = False):	
		self.text = textLines
		self.pos = pos
		self.color = color
		self.width = 0
		self.backColor = backColor
		self.horzCentered = horzCenter
		if not TextBox.initialized:
			TextBox.initialize()
		
	def draw(self):	
		# print("draw")
		for i, line in enumerate(self.text):
			left, top = self.pos
			top += TextBox.MARGIN * i
			text = TextBox.FONT.render(line, True, self.color, self.backColor)
			rect = text.get_rect()
			# if self.horzCentered:
			# 	rect.centerx = left
			# else:
			# 	rect.left = left
			# rect.top = top
			# if rect.width > self.width:
			# 	self.width = rect.width
			DISPLAYSURF.blit(text, (left, top))
		# i = 0
		# for	line in self.text:
		# 	left = self.pos[0]
		# 	top = self.pos[1] + TextBox.MARGIN * i
		# 	text = TextBox.FONT.render(line, True, self.color, self.backColor)
		# 	rect = text.get_rect()
		# 	if self.horzCentered:
		# 		rect.centerx = left
		# 	else:
		# 		rect.left = left
		# 	rect.top = top
		# 	if rect.width > self.width:
		# 		self.width = rect.width
		# 	DISPLAYSURF.blit(text, rect)		
		# 	i+=1
		# text = TextBox.FONT.render("HI", True, self.color, self.backColor)
		# rect = text.get_rect()
		# rect.top = 480
		# rect.left = 570
		# DISPLAYSURF.blit(text, rect)

			
	def undraw(self):
		# print("undraw")
		height = TextBox.MARGIN * len(self.text)
		if self.horzCentered:
			rect = (self.pos[0]-self.width/2, self.pos[1], self.width, height)
		else:
			rect = (self.pos[0], self.pos[1], self.width, height)
		# rect = self.pos + (200, 21*4)
		pygame.draw.rect(DISPLAYSURF, self.backColor, rect)	

# class Button:
# 	BACKGROUND_COLOR = (125, 125, 170)
# 	HIGHLIGHT_COLOR = (200, 200, 255)
# 	FONT_COLOR = (55, 46, 40)
# 	FONT_SIZE = 18
# 	FONT = 'freesansbold.ttf'
	
# 	ON = "on"
# 	OFF = "off"

# 	def __init__(self, name, rect, text_box=None, color=None, back_color=None):
# 		self.name = name
# 		self.rect = pygame.Rect(rect)
# 		self.last_drawn = Button.OFF
# 		self.text_box = text_box
# 		self.color = color or Button.HIGHLIGHT_COLOR
# 		self.back_color = back_color or Button.BACKGROUND_COLOR
# 		self.font = pygame.font.Font(Button.FONT, Button.FONT_SIZE)

# 	def update(self, mouse_pos):
# 		if self.within(mouse_pos):
# 			self.draw(self.color)
# 			self.last_drawn = Button.ON
# 			if self.text_box:
# 				self.text_box.draw()
# 		else:
# 			self.draw(self.back_color)
# 			if self.last_drawn == Button.ON and self.text_box:
# 				self.text_box.undraw()
# 			self.last_drawn = Button.OFF

# 	def within(self,mouse_pos):
# 		return self.rect.collidepoint(mouse_pos)

# 	def draw(self, back_color):
# 		pygame.draw.rect(DISPLAYSURF, back_color, self.rect)
# 		text_surface = self.font.render(self.name, True, Button.FONT_COLOR, back_color)
# 		text_rect = text_surface.get_rect(center=self.rect.center)
# 		DISPLAYSURF.blit(text_surface, text_rect)

# 	def redraw(self):
# 		if self.last_drawn == Button.ON:
# 			self.draw(self.color)
# 		elif self.last_drawn == Button.OFF:
# 			self.draw(self.back_color)
class Button:
	BACKGROUND_COLOR = (125, 125, 170)
	HIGHLIGHT_COLOR = (200, 200, 255)
	FONT_COLOR = (55, 46, 40)
	FONT_SIZE = 18
	FONT = 'freesansbold.ttf'
	
	def __init__(self, name, rect, text_box=None, color=None, back_color=None):
		self.name = name
		self.rect = rect #pygame.Rect(rect)
		self.is_mouse_over = False
		self.text_box = text_box
		self.color = color or self.HIGHLIGHT_COLOR
		self.back_color = back_color or self.BACKGROUND_COLOR
		self.font = pygame.font.Font(self.FONT, self.FONT_SIZE)

	# def is_button_status_changed(self, mouse_pos):
	# 	# change from not in the area to inside the area
	# 	if self.within(mouse_pos) and not self.is_mouse_over:
	# 		return True
	# 	# change from inside the area to not in the area
	# 	if not self.within(mouse_pos) and self.is_mouse_over:
	# 		return True
	# 	return False
	
	def update(self, mouse_pos):
		# update textbox only when the button status is changed
		# have to update it, before changing the self.is_mouse_over
		# if self.is_button_status_changed(mouse_pos):
		# 	self.update_textbox()

		if self.within(mouse_pos):
			self.is_mouse_over = True
		else:
			self.is_mouse_over = False

		# print(self.is_mouse_over)
		self.update_textbox()

	def update_textbox(self):
		if self.is_mouse_over:
			self.draw(self.color)
			if self.text_box:
				self.text_box.draw()
		else:
			self.draw(self.back_color)
			if self.text_box:
				self.text_box.undraw()

	def within(self,mouse_pos):
		# print(self.name, self.rect, mouse_pos, self.is_mouse_over)
		x, y = mouse_pos
		left, top, width, height = self.rect
		return (left<=x<=left+width) and (top<=y<=top+height)
		# return self.rect.collidepoint(mouse_pos)

	# def draw(self, back_color):
	# 	pygame.draw.rect(DISPLAYSURF, back_color, self.rect)
	# 	text_surface = self.font.render(self.name, True, self.FONT_COLOR, back_color)
	# 	top, left, width, height = self.rect
	# 	center = (left+width/2, top+height/2)
	# 	text_rect = text_surface.get_rect(center=center)
	# 	DISPLAYSURF.blit(text_surface, text_rect)
	def draw(self, backColor):
		pygame.draw.rect(DISPLAYSURF, backColor, self.rect)
		(left, top, width, height) = self.rect	
		text = self.font.render(self.name, True, Button.FONT_COLOR, backColor)
		rect = text.get_rect()
		rect.center = (left+width/2, top+height/2)
		DISPLAYSURF.blit(text, rect)

	def redraw(self):
		if self.is_mouse_over:
			self.draw(self.color)
		else:
			self.draw(self.back_color)
