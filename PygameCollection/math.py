from math import pi, sin, cos, acos
import numpy as np

def rad2deg(rad):
	return 180*rad/pi

def deg2rad(deg):
	return pi*deg/180

class Vector2D:
	def __init__(self, x, y, dtype="float64"):
		self.x, self.y = x, y
		self.vec = np.array((x, y), dtype=dtype)

	def enclosedAngle(self, v2):
		return acos((self*v2)/(len(self)*len(v2)))

	def toRadiant(self):
		return self.enclosedAngle(Vector2D(1, 0))

	def toTuple(self):
		return self.x, self.y

	def __str__(self):
		return f"Vector2D({self.x} {self.y})"

	def __len__(self):
		return np.sqrt(self.vec.dot(self.vec))

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
	def fromIterable(cls, iterable, dtype="float64"):
		assert len(iterable) == 2
		return Vector2D(*iterable, dtype=dtype)

	@classmethod
	def fromRadiant(cls, radiant, dtype="float64"):
		return Vector2D(cos(radiant), sin(radiant), dtype=dtype)