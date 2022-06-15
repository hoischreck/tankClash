from PygameCollection.game import ObjController
from PygameCollection.gameObjects import MovableSprite
from PygameCollection.math import Vector2D
from math import pi

#todo: automate _tryUpdate paradigm
# -> collision detection uses scaling property of actions
class BasicMSpriteController(ObjController):
	def __init__(self):
		super().__init__()
		self.actions = {
			"left": self.left,
			"right": self.right,
			"forward": self.forward,
			"backward": self.backward,
		}

	def left(self):
		self._tryUpdate.append(self._left)
	def _left(self, scale=1):
		self.rot = self.rot - (self.rotSpeed*scale) % (2 * pi)
		self.dir = Vector2D.fromRadiant(self.rot + self.rotOffset)

	def right(self):
		self._tryUpdate.append(self._right)
	def _right(self, scale=1):
		self.rot = self.rot + (self.rotSpeed*scale) % (2 * pi)
		self.dir = Vector2D.fromRadiant(self.rot + self.rotOffset)

	def forward(self):
		self._tryUpdate.append(self._forward)
	def _forward(self, scale=1):
		self.pos += (self.dir * self.v)*scale

	def backward(self):
		self._tryUpdate.append(self._backward)
	def _backward(self, scale=1):
		self.pos -= (self.dir * self.v)*scale