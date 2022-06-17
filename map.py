import csv
from math import pi

from PygameCollection.graphics import LinearVecArt2D
from PygameCollection.math import Vector2D, Point2D, Line2D
from PygameCollection.gameObjects import GraphicalObj
from PygameCollection.graphics import LinearVecArt2D
import pygame

#todo: add options for filling or line width
#Used to create polygons made up of "Line2D" instances (e.g. used in collision detection and handling)
class Line2DPolygon(GraphicalObj):
	def __init__(self, game, color=(0, 0, 0, 255), lines=None):
		super().__init__(game)
		self.lines = [] if lines is None else lines
		assert all(isinstance(l, Line2D) for l in self.lines)
		self.color = color

	def addLinePt(self, start, end):
		self.lines.append(Line2D(*Vector2D.fromIterables(start, end)))

	def addLineVec(self, start, end):
		self.lines.append(Line2D(start, end))

	def draw(self, surface=None):
		if len(self.lines) == 0:
			return
		s = self.screen if surface is None else surface
		pygame.draw.polygon(s, self.color, self.linesToCoordinates())

	def linesToCoordinates(self):
		return [pos.toTuple() for line in self.lines for pos in (line.start, line.end)]

	@classmethod
	def fromLinearVecArt(cls, game, lva: LinearVecArt2D):
		l2dPolygon = Line2DPolygon(game)
		points = lva.getPointsV2D()
		for i, p in enumerate(points):
			if i < len(points)-1:
				l2dPolygon.addLineVec(p, points[i+1])
			else:
				l2dPolygon.addLineVec(p, points[0])
		return l2dPolygon

# todo: wall as subclass?
class Wall:
	#todo: use
	STANDARD_WIDTH = 10

	def __init__(self, game, start, end):
		self.game = game
		self.screen = self.game.screen

		self.start = Vector2D.fromIterable(start)
		self.end = Vector2D.fromIterable(end)
		self.startToEnd = self.end-self.start
		self.length = self.startToEnd.magnitude()
		self.color = (0, 0, 0)
		self.width = 10
		#self.norm = Vector2D.getNormVec(self.start-self.end)
		self.color = (0, 0, 0, 255)

		self.line: Line2D = Line2D(self.start, self.end)
		self.polygon: Line2DPolygon = self._buildPolygon()

	# polygon is build once instead of every draw call to save computation time
	def _buildPolygon(self):
		lva = LinearVecArt2D(
			pos=self.start,
			pathVectors=[
				Vector2D(self.length, 0),
				Vector2D(0, self.width),
				Vector2D(-self.length, 0),
				Vector2D(0, -self.width)
			],
			posOffset=Vector2D(0, -self.width//2),
			closed=True
		)
		lva.rotate(self.startToEnd.toRadiant())
		return Line2DPolygon.fromLinearVecArt(self.game, lva)

	def getClosestLine(self, x, y):
		return sorted({l: l.distanceToPoint(x, y) for l in self.polygon.lines}.items(), key=lambda x: x[1])[0]

	# extra width is used for example in finding positions for placing a rectangle, by enhancing the mask size by drawing thicker walls
	def draw(self, surface=None):
		s = self.screen if surface is None else surface
		self.polygon.draw(s)

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
		if len(self.walls) > minAmount:
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

	def _distanceToWall(self, x, y, wall: Wall):
		return wall.line.distanceToPoint(x, y)

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
