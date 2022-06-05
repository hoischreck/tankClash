from PygameCollection.math import Vector2D
from PygameCollection.gameObjects import GraphicalObj
import pygame

class Wall(GraphicalObj):
	def __init__(self, game, start, end):
		super().__init__(game)
		self.start = Vector2D.fromIterable(start)
		self.end = Vector2D.fromIterable(end)
		self.color = (0, 0, 0)
		self.width = 10

	def draw(self, surface=None):
		pygame.draw.line(self.screen if surface is None else surface, self.color, self.start.toTuple(), self.end.toTuple(), self.width)

	def __len__(self):
		return len(self.start-self.end)

# Basically a collection of walls
class TankMap(GraphicalObj):
	def __init__(self, game):
		super().__init__(game)
		self.walls = set()
		s = pygame.Surface(self.game.windowSize, pygame.SRCALPHA)
		self.mask = pygame.mask.from_surface(s)

	def addWall(self, start, end):
		self.walls.add(Wall(self.game, start, end))
		wallSurface = pygame.Surface(self.game.windowSize, pygame.SRCALPHA) # Size effects "hits any wall"
		self.draw(wallSurface)
		self.mask = pygame.mask.from_surface(wallSurface)

	# checks if sprite overlaps map mask
	def hitsAnyWall(self, sprite):
		return self.mask.overlap(sprite.getMask(), sprite.getMaskOffset().toTuple())

	def addWallH(self, start, length):
		self.addWall(start, (start[0]+length, start[1]))

	def addWallV(self, start, length):
		self.addWall(start, (start[0], start[1]+length))

	def draw(self, surface=None):
		for w in self.walls:
			w.draw(surface)
