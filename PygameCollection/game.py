import pygame
from abc import ABC, abstractmethod
from enum import Enum, auto

# Basic implementation of a drawing queue
class BaseDrawingQueue:
	def __init__(self, drawableObjects=None):
		self.items: list = [] if drawableObjects is None else drawableObjects

	def append(self, drawableObj):
		self.items.append(drawableObj)

	def insert(self, drawableObj, priority):
		self.items.insert(drawableObj, priority)

	def remove(self, drawableObj):
		# find more efficient design
		self.items.remove(drawableObj)

	def drawAll(self):
		for i in self.items[::-1]:
			i.draw()

class Base2DGame(ABC):
	def __init__(self, name="[PLACEHOLDER]"):
		self.name = name
		self.windowSize = (1920, 1080)
		self.w, self.h = self.windowSize
		self.windowCaption = "WindowCaption"
		self.backgroundColor = (255, 255, 255)

		self.tps = 60

		self.drawingQueue: BaseDrawingQueue = BaseDrawingQueue()
		self.key: Keys = None
		self.mouse: Mouse = None

		self.loop = self.loopWrapper(self.loop)

	def run(self):
		self.screen = pygame.display.set_mode(self.windowSize)
		self.clock = pygame.time.Clock()
		self.setup()
		self.running = True
		while self.running:
			self.loop()

	def setup(self):
		pass

	@abstractmethod
	def loop(self):
		pass

	def loopWrapper(self, runMethod):
		def gameloop(*args, **kwargs):
			self.__loopBegin()
			r = runMethod(*args, **kwargs)
			self.__loopClose()
			return r
		return gameloop

	def __loopBegin(self):
		self.screen.fill(self.backgroundColor)

		self.__handleEvents()
		self.__drawObjects()

	#todo: change handler logic, to only traverse all events once (e.g. keys and mouse class shouldnt iterate individually)
	def __handleEvents(self):
		events = pygame.event.get()
		self.key = Keys(pygame.key.get_pressed(), events)
		self.mouse = Mouse(pygame.mouse.get_pressed(), events)
		# events is iterated twice <- efficient solution?
		for event in events:
			if event.type == pygame.QUIT:
				self.running = False

	def __drawObjects(self):
		self.drawingQueue.drawAll()

	def __loopClose(self):
		self.clock.tick(self.tps)
		pygame.display.flip()

class KeyType(Enum):
	PYGAME = auto()
	STRING = auto()

class Keys:
	def __init__(self, pygameKeys, pygameEvents):
		self.pyKeys = pygameKeys
		self.pyEvts = pygameEvents

	def get(self):
		return self.pyKeys

	def heldDown(self, key, keyType: KeyType=KeyType.PYGAME):
		assert isinstance(keyType, KeyType)
		if keyType == KeyType.PYGAME:
			return self.pyKeys[key]
		elif keyType == KeyType.STRING:
			return self.pyKeys[pygame.key.key_code(key)]

	def __checkEvt(self, key, keyType, condition):
		assert isinstance(keyType, KeyType)
		for e in self.pyEvts:
			if e.type == condition:
				if e.key == (key if keyType == KeyType.PYGAME else pygame.key.key_code(key)):
					return True
		return False

	def keyUp(self, key, keyType: KeyType=KeyType.PYGAME):
		return self.__checkEvt(key, keyType, pygame.KEYUP)

	def keyDown(self, key, keyType: KeyType=KeyType.PYGAME):
		return self.__checkEvt(key, keyType, pygame.KEYDOWN)


class Mouse:
	def __init__(self, pygameMouse, pygameEvents):
		self.pyMouse = pygameMouse
		self.pyEvts = pygameEvents

	def heldDown(self, mouseButton=None):
		assert mouseButton in (1, 2, 3)
		if mouseButton is not None:
			return True if self.pyMouse[mouseButton-1] else False
		else:
			return 1 in self.pyMouse

	def getPos(self):
		return pygame.mouse.get_pos()

	def setPos(self, pos):
		pygame.mouse.set_pos(pos)

	def __checkEvt(self, mouseButton, condition):
		assert mouseButton in (1, 2, 3)
		for e in self.pyEvts:
			if e.type == condition:
				if mouseButton is not None:
					return True if mouseButton == e.button else False
				else:
					return True
		return False

	def mouseDown(self, mouseButton):
		return self.__checkEvt(mouseButton, pygame.MOUSEBUTTONDOWN)

	def mouseUp(self, mouseButton):
		return self.__checkEvt(mouseButton, pygame.MOUSEBUTTONUP)

