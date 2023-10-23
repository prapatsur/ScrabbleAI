'''
Represents the bag of tiles, contains all tiles which haven't been drawn yet.
Initialized with the exact distribution of tiles, grab() will choose one tile
from the bag at random. If none are available, it will return None
'''

import pygame, random, tile

class Bag:
	
	#sets up the initial distribution of tiles
	def __init__(self):
		self.tiles = []
		
		# # Initial distribution of tiles
		# tile_data = [
		# 	('A', 1, 9), ('B', 3, 2), ('C', 3, 2), ('D', 2, 4), ('E', 1, 12), 
		# 	('F', 4, 2), ('G', 2, 3), ('H', 4, 2), ('I', 1, 9), ('J', 8, 1),
		# 	('K', 5, 1), ('L', 1, 4), ('M', 3, 2), ('N', 1, 6), ('O', 1, 8),
		# 	('P', 3, 2), ('Q', 10, 1), ('R', 1, 6), ('S', 1, 4), ('T', 1, 6),
		# 	('U', 1, 4), ('V', 4, 2), ('W', 4, 2), ('X', 8, 1), ('Y', 4, 4),
		# 	('Z', 10, 1), (' ', 0, 2)
		# ]
		
		# for letter, score, count in tile_data:
		# 	self.add(letter, score, count)

		
		DEBUG - Small bag for debugging total game states
		self.add('E', 1, 3)
		self.add('S', 1, 3)
		self.add('A', 1, 3)
		self.add('Z', 10, 1)
		self.add('R', 1, 2)
		self.add('I', 1, 2)
		self.add('M', 3, 1)
		self.add('N', 1, 3)
		
		random.shuffle(self.tiles)

	def grab(self):
		"""Grabs one tile from the bag and returns it (None if there aren't any left)."""
		if self.isEmpty():
			return None
		return self.tiles.pop(0)
			
	def isEmpty(self):
		return not self.tiles

	def shuffle(self):
		random.shuffle(self.tiles)
		
	def putBack(self, tile):
		self.tiles.append(tile)

	def add(self, letter, points, n):
		"""Adds the tile n times into the bag."""
		self.tiles.extend([tile.Tile(letter, points) for _ in range(n)])

