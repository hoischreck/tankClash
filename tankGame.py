import random

import pygame, sys, os
from math import pi
from abc import ABC, abstractmethod
from enum import Enum, auto
from timeit import default_timer

from PygameCollection.math import Vector2D, rad2deg
from PygameCollection.gameObjects import MovableSprite, showRect, showMask, showCenter
from PygameCollection.game import Base2DGame, KeyType
from PygameCollection.templates import BasicMSpriteController
from PygameCollection.utils import loadConvFacScaledImg, loadConvScaledImg, showVecDirSprite, showVector, printRuntime

from ammo import Ammunition, AmmoType
from map import Wall, TankMap

#todo: finish controller

class Player:
	def __init__(self, name, id, game):
		self.name = name
		self.id = id
		self.game = game
		self.score = 0
		self.tank = None

	def setTank(self, tank):
		self.tank = tank

	def setPosition(self, x, y):
		self.tank.pos = Vector2D(x, y)

	def setControls(self, controls):
		for key in controls:
			action = controls[key]
			self.game.controls[key] = self.tank.actions[action]

class Tank(MovableSprite, BasicMSpriteController):
	#todo: implement properly
	WIDTH = 62#40
	HEIGHT = 114#80

	def __init__(self, game, img, pos, *args, **kwargs):
		MovableSprite.__init__(self, game, img, pos, *args, **kwargs)
		BasicMSpriteController.__init__(self)

		self.rotSpeed = 2*pi/100
		self.setRotationOffset(-pi/2) #based on the rotational offset of the sprite image
		self.v = 5

		self.actions["shoot"] = self.shoot
		self.ammo: Ammunition = Ammunition.getAmmo(AmmoType.NORMAL)

	# recursive collision correction
	#todo: enhance performance, generalize approach and evaluate efficiency
	def update(self, scale=1.0, threshold=0.01):
		posBefore = self.pos
		rotBefore = self.rot
		for f in self._tryUpdate:
			f(scale)

		MovableSprite.update(self)
		# check for collision with map (todo: don't allow objects to pass through wall because of to high speeds)
		if self.game.map.hitsAnyWall(self):
			self.pos = posBefore
			self.rot = rotBefore
			if scale >= threshold:
				self.update(scale=scale*0.5)
			else:
				MovableSprite.update(self)

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
		self.windowSize = (1080, 720)


	def setup(self):
		AmmoType.setImage(AmmoType.NORMAL, loadConvScaledImg(("assets", "img", "ProjectileBall.png"), (30, 30)))

		self.map = TankMap(self)
		self.map.load(os.path.join(TankClash.MAP_PATH ,"testMap3"))
		self.drawingQueue.insert(0, self.map)

		#todo: include placeable spawnpoints
		spawns = self.possibleSpawnLocations(2)

		p1 = Player("Ivo", 1, self)
		img = loadConvFacScaledImg(("assets", "img", "TankBlue.png"), 0.5)
		p1.setTank(Tank(self, img, Vector2D(0, 0)))
		showRect(p1.tank)
		showCenter(p1.tank)
		#hideHitbox(p1.tank)
		#showMask(p1.tank)

		p1.setControls({
			"w": "forward",
			"a": "left",
			"s": "backward",
			"d": "right",
			"space": "shoot"
		})

		p1.setPosition(*spawns[0])

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
		# p2.setPosition((self.w // 3) * 2, self.h // 2)
		#
		# self.players.add(p2)
		self.players.add(p1)  # create playerLobby class

		self.drawingQueue.append(p1.tank)
		#self.drawingQueue.append(p2.tank)

	# if unique is True locations are only returned if their count matches the amount
	def possibleSpawnLocations(self, amount, unique=False):
		m = self.map.maskFittingRect(Tank.WIDTH, Tank.HEIGHT)
		pos = list()
		# todo: measure if shuffling saves time since its O(n)
		w, h = m.get_size()
		xs = list(range(w))
		ys = list(range(h))
		random.shuffle(xs)
		random.shuffle(ys)
		for x in xs:
			for y in ys:
				if m.get_at((x, y)):
					pos.append((x, y))
					if len(pos) >= amount:
						return pos
					break #x coordinate is changed
		if not unique:
			return pos

	#@printRuntime
	def loop(self):
		for k in self.controls:
			if self.key.heldDown(k, KeyType.STRING):
				self.controls[k]()

		# collision testing
		# player collisions
		# tanks = [p.tank for p in self.players]
		# t1, t2 = tuple(tanks)
		# if t1.maskCollidesWith(t2):
		# 	print("boom")
		# player wall collisions

		# for w in self.map.walls:


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

	def addPlayer(self, player):
		self.players.add(player)
		self.drawingQueue.append(player.tank)

	def removePlayer(self, player):
		self.players.remove(player)
		self.drawingQueue.remove(player)