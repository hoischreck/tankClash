import csv
from math import pi

from PygameCollection.math import Vector2D, Point2D
from PygameCollection.gameObjects import GraphicalObj
import pygame

class Wall(GraphicalObj):
	STANDARD_WIDTH = 10

	def __init__(self, game, start, end):
		super().__init__(game)
		self.start = Vector2D.fromIterable(start)
		self.end = Vector2D.fromIterable(end)
		self.color = (0, 0, 0)
		self.width = 10
		self.norm = Vector2D.getNormVec(self.start-self.end)

	# todo: add small circles to the end of a wall to make them look "cleaner"
	def draw(self, surface=None):
		pygame.draw.line(self.screen if surface is None else surface, self.color, self.start.toTuple(), self.end.toTuple(), self.width)
		#pygame.draw.circle(self.screen, self.color, self.start.toTuple(), self.width)
		#pygame.draw.circle(self.screen, self.color, self.end.toTuple(), self.width)

	# reflects a vector at the norm vector (e.g. used in projectile reflection logic)
	def reflectVector(self, v):
		# handle reflection -> 1.) calc norm vector 2.) compare with direction of shot 3.) combine into a new direction vector
		normVec = self.norm
		if v.enclosedAngle(normVec) > pi / 2:
			normVec.toCounter() #todo: change logic to return a new vector?
		v = Vector2D.fromSymReflection(v, normVec)
		v.toUnitVec()
		v.toCounter()
		return v

	def __len__(self):
		return len(self.start-self.end)

# Basically a collection of walls
class TankMap(GraphicalObj):
	DATA_DELIMITER = ","

	def __init__(self, game):
		super().__init__(game)
		self.walls = list()
		self._renewMask()

	def addWall(self, start, end):
		self.walls.append(Wall(self.game, start, end))
		self._renewMask() # Size effects "hits any wall"

	def removeWall(self, wall):
		self.walls.remove(wall)
		self._renewMask()

	def removeLast(self, minAmount=0):
		if len(self.walls) > 0:
			del self.walls[-1]
			self._renewMask()

	# checks if sprite overlaps map mask
	def hitsAnyWall(self, sprite):
		return self.mask.overlap(sprite.getMask(), sprite.getMaskOffset().toTuple())

	# checks if sprite hits wall and which one that is
	def hitsWall(self, sprite):
		# 1.) get point of collision 2.) distance to all lines 3.) choose closest wall
		cp = self.hitsAnyWall(sprite)
		if cp is None:
			return
		distances = {w: self._distanceToWall(*cp, w) for w in self.walls}
		sd = sorted(distances.items(), key=lambda x: x[1])
		return sd[0][0]

	def addWallH(self, start, length):
		self.addWall(start, (start[0]+length, start[1]))

	def addWallV(self, start, length):
		self.addWall(start, (start[0], start[1]+length))

	def allWallPoints(self):
		return {p for w in self.walls for p in (w.start, w.end)}

	def closestWallCorner(self, x, y):
		closest = (Vector2D(0, 0), float("inf"))
		referencePoint = Vector2D(x, y)
		for p in self.allWallPoints():
			d = (p - referencePoint).magnitude()
			if d < closest[1]:
				closest = (p, d)
		return closest[0]

	def _distanceToWall(self, x, y, wall):
		m = (wall.end-wall.start).slope()
		xp = wall.start.x if m is None else (m**2*wall.start.x+x-m*(wall.start.y-y))/(m**2+1)
		yp = y if m is None else m*(xp-wall.start.x)+wall.start.y
		return Point2D.distance(x, y, xp, yp)

	def _renewMask(self):
		s = pygame.Surface(self.game.windowSize, pygame.SRCALPHA)
		self.draw(s)
		self.mask = pygame.mask.from_surface(s)

	def draw(self, surface=None):
		for w in self.walls:
			w.draw(surface)

	def save(self, filepath):
		# saves each wall as a 4 values (start_x, start_y, end_x, end_y)
		with open(f"{filepath}.csv", "w", newline="", encoding="utf8") as f:
			csvWriter = csv.writer(f, delimiter=TankMap.DATA_DELIMITER)
			csvWriter.writerows([(*w.start.toTuple(), *w.end.toTuple()) for w in self.walls])

	def load(self, filepath):
		with open(f"{filepath}.csv", "r", encoding="utf8") as f:
			csvReader = csv.reader(f, delimiter=TankMap.DATA_DELIMITER)
			for l in csvReader:
				self.addWall((int(l[0]), int(l[1])), (int(l[2]), int(l[3])))
