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

	@ObjController.tryAction
	def left(self, scale=1):
		self.rot = self.rot - (self.rotSpeed*scale) % (2 * pi)
		self.dir = Vector2D.fromRadiant(self.rot + self.rotOffset)

	@ObjController.tryAction
	def right(self, scale=1):
		self.rot = self.rot + (self.rotSpeed*scale) % (2 * pi)
		self.dir = Vector2D.fromRadiant(self.rot + self.rotOffset)

	@ObjController.tryAction
	def forward(self, scale=1):
		self.pos += (self.dir * self.v)*scale

	@ObjController.tryAction
	def backward(self, scale=1):
		self.pos -= (self.dir * self.v)*scale