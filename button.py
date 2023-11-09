import pygame
from textbox import NullTextBox  # replace with your actual module
from gui import DARK_LAVENDOR, LIGHT_LAVENDOR, DARK_BROWN
from gui import DISPLAYSURF

class Button():
	
	BACKGROUND = DARK_LAVENDOR
	HIGHLIGHT = LIGHT_LAVENDOR
	FONT_COLOR = DARK_BROWN
	
	ON = "on"
	OFF = "off"
	
	initialized = False

	@staticmethod
	def initialize():
		Button.FONT = pygame.font.Font('freesansbold.ttf', 18)
		Button.initialized = True
	
	def __init__(self, name, rect, textBox = None, color = None, backColor = None):
		#Make sure the fonts are set up
		if not Button.initialized:
			Button.initialize()
			
		if color == None:
			color = Button.HIGHLIGHT
		if backColor == None:
			backColor = Button.BACKGROUND
		
		self.name = name
		self.rect = rect
		self.lastDrawn = Button.OFF
		if textBox is None:
			self.textBox = NullTextBox()
		else:
			self.textBox = textBox
		self.color = color
		self.backColor = backColor

	def update(self, mouse_position):
		""" update button highlighting based on mouse position and draw text box if necessary"""
		mouseX, mouseY = mouse_position
		if self.within(mouseX, mouseY):
			self.highlight()
		else:
			self.no_highlight()

	def highlight(self):
		self.draw(self.color)
		self.lastDrawn = Button.ON
		self.textBox.draw()

	def no_highlight(self):
		self.draw(self.backColor)
		if self.lastDrawn == Button.ON:
			self.textBox.undraw()
		self.lastDrawn = Button.OFF		

	def within(self, mouseX, mouseY):
		(left, top, width, height) = self.rect
		return mouseX >= left and mouseX <= left+width and mouseY >= top and mouseY <= top+height
		
	def draw(self, backColor):
		pygame.draw.rect(DISPLAYSURF, backColor, self.rect)
		(left, top, width, height) = self.rect	
		text = Button.FONT.render(self.name, True, Button.FONT_COLOR, backColor)
		rect = text.get_rect()
		rect.center = (left+width/2, top+height/2)
		DISPLAYSURF.blit(text, rect)
		
	def redraw(self):
		if self.lastDrawn == Button.ON:
			self.draw(self.color)
		elif self.lastDrawn == Button.OFF:
			self.draw(self.backColor)