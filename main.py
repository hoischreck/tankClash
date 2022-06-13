import pygame, sys, os
from math import pi
from abc import ABC, abstractmethod
from enum import Enum, auto
from timeit import default_timer

from PygameCollection.math import Vector2D, rad2deg
from PygameCollection.gameObjects import MovableSprite, showRect, showMask
from PygameCollection.game import Base2DGame, KeyType
from PygameCollection.templates import BasicMSpriteController
from PygameCollection.utils import loadConvFacScaledImg, loadConvScaledImg, showVecDirSprite, showVector

from ammo import Ammunition, AmmoType
from map import Wall, TankMap

pygame.init()
# overhaul key mapping system
# account for tank speed when shooting?

class Player:
	def __init__(self, name, id, game):
		self.name = name
		self.id = id
		self.game = game
		self.score = 0
		self.tank = None

	def setTank(self, tank):
		self.tank = tank

	def setPosition(self, pos: Vector2D):
		self.tank.pos = pos

	def setControls(self, controls):
		for key in controls:
			action = controls[key]
			self.game.controls[key] = self.tank.actions[action]


class Tank(MovableSprite, BasicMSpriteController):
	def __init__(self, game, img, pos, *args, **kwargs):
		super().__init__(game, img, pos, *args, **kwargs)
		self.game = game

		self.rotSpeed = 2*pi/50
		self.setRotationOffset(-pi/2) #based on the rotational offset of the sprite image
		self.v = 10

		self.actions = {
			"left": self.left,
			"right": self.right,
			"forward": self.forward,
			"backward": self.backward,
			"shoot": self.shoot
		}

		self.ammo: Ammunition = Ammunition.getAmmo(AmmoType.NORMAL)

	# recursive collision correction
	#todo: enhance performance, generalize approach and evaluate efficiency
	def update(self, scale=1.0, threshold=0.01):
		posBefore = self.pos
		rotBefore = self.rot
		for f in self._tryUpdate:
			f(scale)

		super().update()
		# check for collision with map (todo: if tank to skipping wall because of speed is neglected)
		if self.game.map.hitsAnyWall(self):
			self.pos = posBefore
			self.rot = rotBefore
			if scale >= threshold:
				self.update(scale=scale*0.5)
			else:
				super().update()

		self._tryUpdate = list()

	# todo: implement this
	# if any wall was faced through, this function returns the given wall
	def _hasPhasedAnyWall(self):
		# 1.) check new rect and pos and compare with every wall
		pass

	def shoot(self):
		projectile = self.ammo.tryGetBullet(
			game=self.game,
			pos=self.pos+self.dir*70,
			direction=self.dir
		)
		if projectile is not None:
			self.game.drawingQueue.append(projectile)

class TankClash(Base2DGame):
	MAP_PATH = os.path.join("maps")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.players = set()
		self.controls = {}

	def setup(self):
		AmmoType.setImage(AmmoType.NORMAL, loadConvScaledImg(("assets", "img", "ProjectileBall.png"), (30, 30)))

		self.map = TankMap(self)
		# self.map.addWall((900, 0),(900, 1000))
		# self.map.addWallV((100, 0), 1000)
		# self.map.addWallH((100, 995), 800)
		# self.map.addWallH((100, 0), 800)
		# self.map.addWall((450, 995), (900, 450))
		self.map.load("testMap1")
		self.drawingQueue.insert(0, self.map)
		#self.map.save("testMap")

		p1 = Player("Ivo", 1, self)
		img = loadConvFacScaledImg(("assets", "img", "TankBlue.png"), 0.5)
		p1.setTank(Tank(self, img, Vector2D(0, 0)))
		#showRect(p1.tank)
		#hideHitbox(p1.tank)
		#showMask(p1.tank)

		p1.setControls({
			"w": "forward",
			"a": "left",
			"s": "backward",
			"d": "right",
			"space": "shoot"
		})
		p1.setPosition(Vector2D(self.w // 3, self.h // 2))

		# p2 = Player("Flitzi", 2, self)
		# img = loadConvFacScaledImg(("assets", "img", "TankRed.png"), 0.5)
		# p2.setTank(Tank(self, img, Vector2D(0, 0)))
		# p2.setControls({
		# 	"up": "forward",
		# 	"left": "left",
		# 	"down": "backward",
		# 	"right": "right",
		# 	"return": "shoot"
		# })
		# p2.setPosition(Vector2D((self.w // 3) * 2, self.h // 2))
		#
		# self.players.add(p2)
		self.players.add(p1)  # create playerLobby class

		self.drawingQueue.append(p1.tank)
		#self.drawingQueue.append(p2.tank)

	def loop(self):
		for k in self.controls:
			if self.key.heldDown(k, KeyType.STRING):
				self.controls[k]()

		# collision testing
		#start = default_timer()

		# player collisions
		# tanks = [p.tank for p in self.players]
		# t1, t2 = tuple(tanks)
		# if t1.maskCollidesWith(t2):
		# 	print("boom")
		# player wall collisions

		#print(f"computation time {default_timer()-start}s")
		# for w in self.map.walls:
		# 	showVector(self.screen, w.norm, (w.start.x+w.end.x)/2, (w.start.y+w.end.y)/2)

		for player in self.players:
			#showVecDirSprite(player.tank)
			toBeRemoved = set()
			# checks bullet timeout
			for b in player.tank.ammo.activeShots:
				#showVecDirSprite(b)
				if b.hasExpired():
					toBeRemoved.add(b)

			for i in toBeRemoved:
				player.tank.ammo.kill(i)
				self.drawingQueue.remove(i)

class ClipMode(Enum):
	HORIZONTAL = "Horizontal"
	VERTICAL = "Vertikal"
	DIAGONAL = "Diagonal"
	CORNER = "Corner"

class TankClashMapEditor(TankClash):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.startPoint = None
		self.endPoint = None
		self.fixedTargetEnd = None
		self.clipMode = ClipMode.HORIZONTAL
		self.font = pygame.font.Font(pygame.font.get_default_font(), 30)

	def setup(self):
		print("save map by pressing 'ctrl+s'")
		AmmoType.setImage(AmmoType.NORMAL, loadConvScaledImg(("assets", "img", "ProjectileBall.png"), (30, 30)))

		self.map = TankMap(self)
		self.drawingQueue.append(self.map)
		# base map
		offset = Wall.STANDARD_WIDTH//2
		#todo: use this or implement reflection by "hitting" walls (basic norm reflection)
		self.map.addWallH((0, offset), self.w)
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
			"up": "forward",
			"left": "left",
			"down": "backward",
			"right": "right",
			"return": "shoot"
		})

		p1.setPosition(Vector2D(self.w // 3, self.h // 2))
		self.players.add(p1)

		self.drawingQueue.append(p1.tank)

	def loop(self):
		for k in self.controls:
			if self.key.heldDown(k, KeyType.STRING):
				self.controls[k]()
		# snap courser to closest wall point
		#if self.key.heldDown(pygame.K_LSHIFT) and self.key.keyDown(pygame.K_s) and self.startPoint is None:


		if self.mouse.heldDown(3):
			# if start point was already set
			if self.startPoint is not None:
				if self.clipMode == ClipMode.HORIZONTAL:
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
				elif self.clipMode == ClipMode.CORNER:
					self.fixedTargetEnd = self.map.closestWallCorner(*self.mouse.getPos()).toTuple()
				else:
					pass # todo: what to do?
			else:
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

		if self.key.keyUp(pygame.K_z):
			self.map.removeLast(minAmount=4) #4 base walls are used as a boundary
		elif self.key.keyUp(pygame.K_h):
			self.clipMode = ClipMode.HORIZONTAL
		elif self.key.keyUp(pygame.K_v):
			self.clipMode = ClipMode.VERTICAL
		elif self.key.keyUp(pygame.K_d):
			self.clipMode = ClipMode.DIAGONAL
		elif self.key.keyUp(pygame.K_c):
			self.clipMode = ClipMode.CORNER

		# render clipping mode as text
		textSurface = self.font.render(f"Current clipping mode: {self.clipMode.value}", True, (0, 0, 0))
		self.screen.blit(textSurface, (10, 10))

		# save map
		if self.key.heldDown(pygame.K_LCTRL) and self.key.keyDown(pygame.K_s):
			mapName = input("enter a map name:")
			self.map.save(os.path.join(TankClash.MAP_PATH, mapName))
			print(f"save map: '{mapName}'")


if __name__ == "__main__":
	#g = TankClash()
	#g.run()
	m = TankClashMapEditor()
	m.run()