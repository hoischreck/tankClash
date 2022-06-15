import csv
from math import pi

from PygameCollection.math import Vector2D, Point2D
from PygameCollection.gameObjects import GraphicalObj
import pygame

class Wall(GraphicalObj):
	#todo: use
	STANDARD_WIDTH = 10

	def __init__(self, game, start, end):
		super().__init__(game)
		self.start = Vector2D.fromIterable(start)
		self.end = Vector2D.fromIterable(end)
		self.color = (0, 0, 0)
		self.width = 10
		self.norm = Vector2D.getNormVec(self.start-self.end)
		self.color = (0, 0, 0, 255)

	# todo: change into polygons? -> made up of walls
	# todo: add small circles to the end of a wall to make them look "cleaner"
	# extra width is used for example in finding positions for placing a rectangle, by enhancing the mask size by drawing thicker walls
	def draw(self, surface=None):
		s = self.screen if surface is None else surface
		#pygame.draw.line(s, self.color, self.start.toTuple(), self.end.toTuple(), self.width) #todo: confirm that performance isn't effected to heavily be drawing rects
		se = self.end-self.start
		wallSurface = pygame.Surface((se.magnitude(), self.width), pygame.SRCALPHA)
		wallSurface.fill(self.color)
		rotatedWall = pygame.transform.rotate(wallSurface, -se.toDegrees())
		offset = Vector2D(-rotatedWall.get_width()//2, -rotatedWall.get_height()//2)
		s.blit(rotatedWall, ((self.start+self.end)*0.5+offset).toTuple())

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
		self.mask: pygame.mask.Mask = None
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

	# returns a mask that is true for every bit that has enough space to fit a rect with given width and height
	def maskFittingRect(self, w, h):
		# basic approach, which does not work pixel perfect
		s = pygame.Surface(self.game.windowSize, pygame.SRCALPHA)
		self.draw(s)
		# draw a rect at every end of an wall, so that sideways collision is not possible
		for wall in self.walls:
			l = wall.width + w if w > h else h # extra width
			t = pygame.Surface(((wall.end-wall.start).magnitude()+l, l+2*(wall.width)), pygame.SRCALPHA) #todo: maybe 2*(wall.width) is wrong
			t.fill((255, 255, 255))
			tmpSurface = pygame.transform.rotate(t, -(wall.end-wall.start).toDegrees())
			offset = Vector2D(-tmpSurface.get_width()//2, -tmpSurface.get_height()//2)
			s.blit(tmpSurface, ((wall.start+wall.end)*0.5+offset).toTuple())

		m = pygame.mask.from_surface(s)
		m.invert()
		return m

	def _distanceToWall(self, x, y, wall):
		m = (wall.end-wall.start).slope()
		xp = wall.start.x if m is None else (m**2*wall.start.x+x-m*(wall.start.y-y))/(m**2+1)
		yp = y if m is None else m*(xp-wall.start.x)+wall.start.y
		return Point2D.distance(x, y, xp, yp)

	def _renewMask(self):
		self.mask = self.__maskFromWalls()

	def __maskFromWalls(self):
		s = pygame.Surface(self.game.windowSize, pygame.SRCALPHA)
		self.draw(s)
		return pygame.mask.from_surface(s)

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
