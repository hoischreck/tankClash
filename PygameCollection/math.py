import math
from math import pi, sin, cos, acos
import numpy as np

def rad2deg(rad):
	return 180*rad/pi

def deg2rad(deg):
	return pi*deg/180

class Point2D:
	@classmethod
	def distance(cls, x1, y1, x2, y2):
		return math.sqrt((x2 - x1)**2+(y2-y1)**2)

class Vector2D:
	# np.double = float64
	def __init__(self, x, y, dtype=np.double):
		self.dtype = dtype
		self.x, self.y = x, y
		self.vec = np.array((x, y), dtype=self.dtype)

	def magnitude(self):
		return np.sqrt(self.vec.dot(self.vec))

	def enclosedAngle(self, v2):
		return acos((self*v2)/(self.magnitude()*v2.magnitude()))

	# self is projected on to v2
	def projectionLength(self, v2):
		return self.magnitude()*self.enclosedAngle(v2)

	def slope(self):
		if self.x == 0:
			return None
		return self.y/self.x

	def toRadiant(self):
		return self.enclosedAngle(Vector2D(1, 0))

	def toTuple(self):
		return self.x, self.y

	def toUnitVec(self):
		m = self.magnitude()
		self.x = self.x / m
		self.y = self.y / m
		self.vec = np.array((self.x, self.y), dtype=self.dtype)

	def __str__(self):
		return f"Vector2D({self.x} {self.y})"

	def __len__(self):
		return len(self.vec)

	def __add__(self, other):
		if isinstance(other, Vector2D):
			return Vector2D(self.x + other.x, self.y + other.y)
		else:
			raise TypeError

	def __sub__(self, other):
		if isinstance(other, Vector2D):
			return Vector2D(self.x - other.x, self.y - other.y)
		else:
			raise TypeError

	def __mul__(self, other):
		if isinstance(other, Vector2D):
			return Vector2D.fromIterable(self.vec.dot(other.vec))
		elif isinstance(other, (int, float)):
			return Vector2D(self.x*other, self.y*other)
		else:
			raise TypeError

	def __truediv__(self, other):
		if isinstance(other, (int, float)):
			return Vector2D(self.x / other, self.y / other)
		else:
			raise TypeError

	@classmethod
	def fromIterable(cls, iterable, dtype=np.double):
		assert len(iterable) == 2
		return Vector2D(*iterable, dtype=dtype)

	@classmethod
	def fromRadiant(cls, radiant, dtype=np.double):
		return Vector2D(cos(radiant), sin(radiant), dtype=dtype)

	@classmethod
	def copy(cls, v):
		return Vector2D(v.x, v.y)

	@classmethod
	def asUnitVector(cls, v):
		newVec = Vector2D.copy(v)
		return newVec / newVec.magnitude()

	# v1 is projected on to v2
	@classmethod
	def fromProjection(cls, v1, v2):
		return Vector2D.copy(v2) * v1.projectionLength(v2)

	# v1 is reflected at v2
	@classmethod
	def fromReflection(cls, v1, v2):
		return 2*v2 - v1

	# symmetric reflection is done by reflecting at the point of projection
	def fromSymReflection(self, v1, v2):
		return 2*(Vector2D.fromProjection(v1, v2)) - v1