import pygame

from PygameCollection.math import Vector2D, Matrix2D

#todo: review, check if file systematic is sensible
#Linear vector art allows create polygons, by following a path of vectors
class LinearVecArt2D:
	# takes a list of 2D-Vectors describing a path, which will be computed into points
	def __init__(self,
				 pos: Vector2D,
				 pathVectors,
				 posOffset: Vector2D=Vector2D(0, 0),
				 rotOffset = 0,
				 closed=True, closeOrigin=True, autoClose=False
				 ):
		self.pos = pos #point of reference (moves the origin)
		self.vectors = [[v, None] for v in pathVectors]
		self.pOffset = posOffset # will apply a given offset to all points (useful when centering for example)
		self.rOffset = rotOffset # describes vector-art-axis rotation from x axis
		self.closed = closed # if closed, last point must end at start
		self.closeOrigin = closeOrigin # if False, first vector thus second point is used as closing point
		self.autoClose = autoClose # depending on close mode, if last point invalid, point is added automatically
		self._points = self._calcPoints()

	def _calcPoints(self, rot=0):
		p = list()
		# apply rotation
		if rot != 0:
			m = Matrix2D.fromRotation(self.rOffset - rot)  # todo: why is this argument correct??? why not vector.toRadiant()-offset
			for i, v in enumerate(self.vectors):
				self.vectors[i] = [Vector2D.fromMatrixVecMul(v[0], m), None]
			self.pOffset = Vector2D.fromMatrixVecMul(self.pOffset, m) # rotation positional offset must also be respected

		# calculate points based on path described by vectors
		for i, v in enumerate(self.vectors):
			pos = self.pos + v[0] if i == 0 else self.vectors[i-1][1] + v[0]
			self.vectors[i] = [v[0], pos]

		for v in self.vectors:
			v[1] = v[1] + self.pOffset
			p.append(v[1])
		if not self.closeOrigin:
			del p[0]

		if self.closed:
			if self.closeOrigin:
				if  Vector2D.asRounded(self.pos+self.pOffset) != Vector2D.asRounded(p[-1]): # rounding is needed for rotations
					if not self.autoClose:
						# todo: test this
						raise InvalidLVA("Last point must equal first point (origin)")
			else:
				if p[1] != p[-1]:
					if self.autoClose:
						# todo: test this
						raise InvalidLVA("Last point must equal second point")
		return p

	def getPoints(self):
		return [v.toTuple() for v in self._points] # todo: decide on convention

	# convenience method
	def getPointsV2D(self):
		return self._points

	def rotate(self, rotation):
		self._points = self._calcPoints(rotation)

	# convenience method
	@classmethod
	def draw(cls, lva, surface, color=(255, 0, 0)):
		pygame.draw.polygon(surface, color, lva.getPoints())


class InvalidLVA(Exception):
	def __init__(self, msg="Invalid Linear Vector Art"):
		super().__init__(msg)