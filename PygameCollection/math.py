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
		if v2.x == 1 and v2.y == 0:
			return acos(self.x/self.magnitude())
		return acos((self*v2)/(self.magnitude()*v2.magnitude()))

	# self is projected on to v2
	def projectionLength(self, v2):
		return self.magnitude()*cos(self.enclosedAngle(v2))

	def slope(self):
		if self.x == 0:
			return None
		return self.y/self.x

	# returns radiant from x-axis
	def toRadiant(self):
		a = self.enclosedAngle(Vector2D(1, 0))
		r = a if self.y >= 0 else 2*pi - a
		return r

	def toTuple(self):
		return self.x, self.y

	def toUnitVec(self):
		m = self.magnitude()
		self.x = self.x / m
		self.y = self.y / m
		self.vec = np.array((self.x, self.y), dtype=self.dtype)

	def toCounter(self):
		self.x = -self.x
		self.y = -self.y
		self.vec = np.array((self.x, self.y), dtype=self.dtype)

	#
	# def makeCollinearTo(self, v2):
	# 	pass

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
			return self.vec.dot(other.vec)
		elif isinstance(other, (int, float)):
			return Vector2D(self.x*other, self.y*other)
		else:
			raise TypeError

	def __truediv__(self, other):
		if isinstance(other, (int, float)):
			return Vector2D(self.x / other, self.y / other)
		else:
			raise TypeError

	def __eq__(self, other):
		if isinstance(other, Vector2D):
			return self.x == other.x and self.y == other.y
		else:
			raise TypeError

	def __hash__(self):
		return hash(self.toTuple())

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

	@classmethod
	def asCounterVector(cls, v):
		return Vector2D(v.x*-1, v.y*-1)

	@classmethod
	def getNormVec(cls, v):
		s = v.slope()
		return Vector2D(1, 0) if s is None else Vector2D(-s, 1) #Vector2D(s, -1) counter vector

	# v1 is projected on to v2
	@classmethod
	def fromProjection(cls, v1, v2):
		c = Vector2D.copy(v2)
		c.toUnitVec()
		return  c * v1.projectionLength(v2)

	# v1 is reflected at v2
	@classmethod
	def fromReflection(cls, v1, v2):
		return v2*2 - v1

	@classmethod
	# symmetric reflection is done by reflecting at the point of projection
	def fromSymReflection(self, v1, v2):
		return (Vector2D.fromProjection(v1, v2))*2 - v1

	# todo: test
	# returns a vector by rotating by a given radiant
	@classmethod
	def fromRotation(self, v1, radiant):
		a = v1.toRadiant()
		b = a + radiant
		return Vector2D.fromRadiant(b)*v1.magnitude()

	# v1 is supposed to become collinear to v2
	@classmethod
	def fromCollinearity(cls, v1, v2):
		return v2*v1.magnitude()

	@classmethod
	def fromMatrixVecMul(cls, v1, matrix):
		assert isinstance(matrix, Matrix2D)
		return Vector2D.fromIterable(v1.vec.dot(matrix.matx))


# todo: implement?
class Straight:
	def __init__(self, supportVector: Vector2D, directionVector: Vector2D):
		self.sV = supportVector
		self.dV = directionVector


class Matrix2D:
	def __init__(self, formattedList): # format of iterable must be in analogy to matrix
		self.matx = np.array(formattedList, dtype=np.double)

	# format: x1 x2 ... xn y1 y2 ... yn
	@classmethod
	def fromIterable(cls, iterable):
		return Matrix2D(np.array(iterable).reshape(2, 2))

	@classmethod
	def fromVectors(cls, v1, v2):
		return Matrix2D.fromIterable([v1.x, v2.x, v1.y, v2.y])

	# basic rotation transformation matrix
	@classmethod
	def fromRotation(cls, radiant):
		i = Vector2D.fromRadiant(radiant)
		j = Vector2D.fromRadiant(radiant+pi/2)
		#print("i:", rad2deg(i.toRadiant()))
		return Matrix2D.fromVectors(i, j)
