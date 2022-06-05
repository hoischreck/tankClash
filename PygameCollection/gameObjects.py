from abc import ABC, abstractmethod
from PygameCollection.math import Vector2D, rad2deg
import pygame

class GraphicalObj(ABC):
	def __init__(self, game):
		self.game = game
		self.screen = game.screen
		self.skipUpdate = False
		self.skipDraw = False
		self.draw = self.__drawWrapper(self.draw)

	@abstractmethod
	def draw(self):
		pass

	def update(self):
		pass

	def __drawWrapper(self, drawMethod):
		def __inner(*args, **kwargs):
			if not self.skipUpdate:
				self.update()
			if not self.skipDraw:
				r = drawMethod(*args, **kwargs)
				return r
			return
		return __inner

# Basic class of game objects with visual representation
class Sprite2D(pygame.sprite.Sprite, GraphicalObj, ABC):
	def __init__(self, game, image, position: Vector2D):
		GraphicalObj.__init__(self, game)
		assert image is not None, "Sprite must be given an image"
		self.img = image
		self.rect = image.get_rect()
		self.pos = position
		self.staticMask = pygame.mask.from_surface(self.img)
		self.mask = None

		self._drawOrg = self.draw # In case draw method is overridden

	def getMask(self):
		return self.staticMask

	def getMaskOffset(self):
		return self.pos - Vector2D(self.rect.w//2, self.rect.h//2)

	def maskCollidesWith(self, other):
		if self.mask is None:
			self.mask = self.getMask()
		if other.mask is None:
			other.mask = other.getMask()
		return pygame.sprite.collide_mask(self, other)

# Base Class to represent moving objects
class MovableSprite(Sprite2D, ABC):
	def __init__(self, game, image, position: Vector2D, velocity=0, direction=Vector2D(1, 0), rotation=0, rotationSpeed=0, *args, **kwargs):
		super().__init__(game, image, position, *args, **kwargs)
		assert isinstance(position, Vector2D) and isinstance(direction, Vector2D)
		self.imgRotated = self.img
		self.v = velocity
		self.dir = direction
		self.rot = rotation
		self.rotSpeed = rotationSpeed
		self.rotOffset = None
		self.staticMask = self.getMask()

		self._tryUpdate = list()

	# set rotation offset (difference between standard vec(1, 0) and sprite direction)
	def setRotationOffset(self, rotOffset):
		self.rotOffset = rotOffset
		self.dir = Vector2D.fromRadiant(rotOffset)

	def getMask(self):
		return pygame.mask.from_surface(self.imgRotated)

	# faster than getMask, but only returns basic mask without rotation, etc.
	def getStaticMask(self):
		return self.staticMask

	def update(self):
		self.rect.center = self.pos.toTuple()
		if self.rot != 0:
			self.imgRotated = pygame.transform.rotate(self.img, rad2deg(-self.rot))
			self.rect = self.imgRotated.get_rect(center=self.rect.center)

	def draw(self):
		if self.rot != 0:
			self.screen.blit(self.imgRotated, self.rect)
		else:
			self.screen.blit(self.img, self.rect)

def showRect(mSprite: MovableSprite, width=4, debugDirLineLen=150):
	def _drawDebug(drawMethod):
		def __inner(*args, **kwargs):
			r = drawMethod(*args, **kwargs)
			pygame.draw.rect(mSprite.screen, (255, 0, 0), mSprite.rect, width)
			pygame.draw.line(mSprite.screen, (255, 0, 0), mSprite.pos.toTuple(), (mSprite.pos + mSprite.dir * debugDirLineLen).toTuple(), 10)
			return r
		return __inner
	mSprite.draw = _drawDebug(mSprite.draw)

def hideRect(mSprite: MovableSprite):
	mSprite.draw = mSprite._drawOrg

def showMask(mSprite: MovableSprite, width=4):
	def _drawDebug(drawMethod):
		def __inner(*args, **kwargs):
			r = drawMethod(*args, **kwargs)
			points = [(Vector2D(*p)+ mSprite.getMaskOffset()).toTuple() for p in mSprite.getMask().outline()]
			pygame.draw.lines(mSprite.screen, (255, 0, 0), True, points, width)
			return r
		return __inner
	mSprite.draw = _drawDebug(mSprite.draw)