import math
from math import pi, sin, cos, acos, tan
import numpy as np

def rad2deg(rad):
	return 180*rad/pi

def deg2rad(deg):
	return pi*deg/180

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

	def toDegrees(self):
		return rad2deg(self.toRadiant())

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

	def isZero(self):
		return self.x == 0 and self.y == 0

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
	def fromIterables(cls, *iterables, dtype=np.double):
		assert all(len(i) == 2 for i in iterables)
		return [Vector2D(*i, dtype=dtype) for i in iterables]

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
	def asRounded(cls, v, digits=0):
		return Vector2D(round(v.x, digits), round(v.y, digits))

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
		return Vector2D.asUnitVector(v2)*v1.magnitude()

	@classmethod
	def fromMatrixVecMul(cls, v1, matrix):
		assert isinstance(matrix, Matrix2D)
		return Vector2D.fromIterable(v1.vec.dot(matrix.matx))

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
		return Matrix2D.fromVectors(i, j)

# todo: implement? -> change convention to work with vectors instead of x, y pairs?
# what about Vector(0, 0)?
class Straight2D:
	def __init__(self, supportVector: Vector2D, directionVector: Vector2D):
		assert not directionVector.isZero()
		self.sV = supportVector
		self.dV = directionVector

	def distanceToPoint(self, x, y):
		m = self.dV.slope()
		xp = self.sV.x if m is None else (m ** 2 * self.sV.x + x - m * (self.sV.y - y)) / (m ** 2 + 1)
		yp = y if m is None else m * (xp - self.sV.x) + self.sV.y
		return Point2D.distance(x, y, xp, yp)

	def includesPoint(self, x, y):
		return int((x-self.sV.x)*(self.dV.y)) == int((y-self.sV.y)*(self.dV.x))

	# if point is on straight, stretch factor is returned
	def includesPointStFactor(self, x, y):
		if int((x-self.sV.x)*(self.dV.y)) == int((y-self.sV.y)*(self.dV.x)):
			if self.dV.x == 0:
				return (y - self.sV.y) / (self.dV.y)
			else:
				return (x - self.sV.x) / (self.dV.x) # =v

	@classmethod
	def fromStartEnd(cls, start: Vector2D, end: Vector2D):
		return Straight2D(start, end-start)


class Line2D:
	def __init__(self, start: Vector2D, end: Vector2D):
		self.start = start
		self.end = end
		self.dV = end-start
		self.norm = Vector2D.getNormVec(self.dV)

	def distanceToPoint(self, x, y):
		m = self.dV.slope()
		xp = self.start.x if m is None else (m ** 2 * self.start.x + x - m * (self.start.y - y)) / (m ** 2 + 1)
		yp = y if m is None else m * (xp - self.start.x) + self.start.y
		# if line isn't the closest reference point, start and end point are taken as reference
		if self.includesPoint(xp, yp):
			return Point2D.distance(x, y, xp, yp)
		else:
			return min(Point2D.distance(x, y, *self.start.toTuple()), Point2D.distance(x, y, *self.end.toTuple()))


	def includesPoint(self, x, y):
		#todo: rounding is necessary (any better method or more general approach)? (also see StraightClass)

		if int((x-self.start.x)*(self.dV.y)) == int((y-self.start.y)*(self.dV.x)):
			if self.dV.x == 0:
				return 0 <= (y - self.start.y) / (self.dV.y) <= 1
			else:
				return 0 <= (x - self.start.x) / (self.dV.x) <= 1
		return False

	def includesPointStFactor(self, x, y):
		if int((x - self.start.x) * (self.dV.y)) == int((y - self.start.y) * (self.dV.x)):
			if self.dV.x == 0:
				if 0 <= (v := (y - self.start.y) / (self.dV.y)) <= 1:
					return v
			else:
				if 0 <= (v := (x - self.start.x) / (self.dV.x)) <= 1:
					return v

	# reflects a vector at the norm vector (e.g. used in projectile reflection logic)
	def reflectVector(self, v: Vector2D):
		# handle reflection -> 1.) calc norm vector 2.) compare with direction of shot 3.) combine into a new direction vector
		normVec = self.norm
		if v.enclosedAngle(normVec) > pi / 2:
			normVec.toCounter()  # todo: change logic to return a new vector?
		v = Vector2D.fromSymReflection(v, normVec)
		v.toUnitVec()
		v.toCounter()
		return v


class Point2D:
	@classmethod
	def distance(cls, x1, y1, x2, y2):
		return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)