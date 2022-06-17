import pygame, os
from enum import Enum

from PygameCollection.math import Vector2D, rad2deg
from PygameCollection.game import KeyType
from PygameCollection.utils import loadConvFacScaledImg, loadConvScaledImg, showVecDirSprite, showVector
from PygameCollection.graphics import LinearVecArt2D

from ammo import AmmoType
from map import Wall, TankMap, Line2DPolygon

from tankGame import TankClash, Tank, Player

class ClipMode(Enum):
	FREE = "Frei"
	HORIZONTAL = "Horizontal"
	VERTICAL = "Vertikal"
	DIAGONAL = "Diagonal"
	CORNER = "Corner"


class TankClashMapEditor(TankClash):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.tps = 60

		self.startPoint = None
		self.endPoint = None
		self.fixedTargetEnd = None
		self.clipMode = ClipMode.FREE
		self.cornerMode = True
		self.font = pygame.font.Font(pygame.font.get_default_font(), 30)

	def setup(self):
		print("save map by pressing 'ctrl+s'")
		AmmoType.setImage(AmmoType.NORMAL, loadConvScaledImg(("assets", "img", "ProjectileBall.png"), (30, 30)))

		self.map = TankMap(self)
		self.drawingQueue.append(self.map)
		# base map
		offset = Wall.STANDARD_WIDTH//2
		#todo: use this or implement reflection by "hitting" walls (basic norm reflection)
		self.map.addWallH((0, offset-1), self.w)
		self.map.addWallH((0, self.h-offset), self.w)
		self.map.addWallV((offset-1, offset), self.h)
		self.map.addWallV((self.w-offset, offset), self.h)

		p1 = Player("Ivo", 1, self)
		img = loadConvFacScaledImg(("assets", "img", "TankBlue.png"), 0.5)
		p1.setTank(Tank(self, img, Vector2D(0, 0)))
		# showRect(p1.tank)
		# hideHitbox(p1.tank)
		# showMask(p1.tank)

		p1.setControls({
			"w": "forward",
			"a": "left",
			"s": "backward",
			"d": "right",
			"space": "shoot"
		})

		p1.setPosition(self.w // 3, self.h // 2)
		self.players.add(p1)

		self.drawingQueue.append(p1.tank)

	def loop(self):
		for k in self.controls:
			if self.key.heldDown(k, KeyType.STRING):
				self.controls[k]()
		# snap courser to closest wall point
		#if self.key.heldDown(pygame.K_LSHIFT) and self.key.keyDown(pygame.K_s) and self.startPoint is None:
		showVecDirSprite(list(self.players)[0].tank)
		# apply snapping mode
		if self.mouse.heldDown(3):
			# if start point was already set
			if self.startPoint is not None:
				if self.clipMode == ClipMode.FREE:
					self.fixedTargetEnd = self.mouse.getPos()
				elif self.clipMode == ClipMode.HORIZONTAL:
					self.fixedTargetEnd = (self.mouse.getPos()[0], self.startPoint[1])
				elif self.clipMode == ClipMode.VERTICAL:
					self.fixedTargetEnd = (self.startPoint[0], self.mouse.getPos()[1])
				elif self.clipMode == ClipMode.DIAGONAL:
					mP = self.mouse.getPos()
					xM = mP[0]
					if mP[1] >= self.startPoint[1]:
						self.fixedTargetEnd = (xM, self.startPoint[1]+(xM-self.startPoint[0])) #todo: implement
					else:
						self.fixedTargetEnd = (xM, self.startPoint[1]-(xM-self.startPoint[0])) #todo: implement

				if self.cornerMode:
					#self.fixedTargetEnd = self.map.closestWallCorner(*self.mouse.getPos()).toTuple()
					self.mouse.setPos(self.map.closestWallCorner(*self.mouse.getPos()).toTuple())

				else:
					pass # todo: what to do?
			elif self.cornerMode:
				self.mouse.setPos(self.map.closestWallCorner(*self.mouse.getPos()).toTuple())
		else:
			self.fixedTargetEnd = self.mouse.getPos()

		# confirm selection
		if self.mouse.mouseUp(1):
			if self.startPoint is None:
				self.startPoint = self.mouse.getPos()
			elif self.endPoint is None:
				self.endPoint = self.fixedTargetEnd
				self.map.addWall(self.startPoint, self.endPoint)
				self.startPoint, self.endPoint = None, None

		# show wall preview
		if self.startPoint is not None:
			pygame.draw.line(self.screen, (122, 122, 122), self.startPoint, self.fixedTargetEnd, 5)

		# select mode of snapping
		if self.key.keyUp(pygame.K_z):
			self.map.removeLast(minAmount=4) #4 base walls are used as a boundary
		elif self.key.keyUp(pygame.K_1):
			self.clipMode = ClipMode.FREE
		elif self.key.keyUp(pygame.K_2):
			self.clipMode = ClipMode.HORIZONTAL
		elif self.key.keyUp(pygame.K_3):
			self.clipMode = ClipMode.VERTICAL
		elif self.key.keyUp(pygame.K_4):
			self.clipMode = ClipMode.DIAGONAL
		elif self.key.keyUp(pygame.K_c):
			self.cornerMode = not self.cornerMode

		# render clipping mode as text
		clipModeTxtSurface = self.font.render(f"Current clipping mode: {self.clipMode.value}", True, (0, 0, 0))
		cornerModeTxtSurface = self.font.render(f"Corner snap-mode: {self.cornerMode}", True, (0, 0, 0))
		self.screen.blit(clipModeTxtSurface, (10, 10))
		self.screen.blit(cornerModeTxtSurface, (10, clipModeTxtSurface.get_height() + 5))

		# save map
		if self.key.heldDown(pygame.K_LCTRL) and self.key.keyDown(pygame.K_s):
			mapName = input("enter a map name:")
			self.map.save(os.path.join(TankClash.MAP_PATH, mapName))
			print(f"save map: '{mapName}'")