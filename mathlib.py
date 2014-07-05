import math, random

class Vector:
	""" Represents a 2D vector
		Hashes like a len2 tuple
	"""
	def __init__(self, x = 0, y = 0):
		self.x = x
		self.y = y
		
	def __add__(self, val):
		return Vector(self.x + val[0], self.y + val[1])
	
	def __sub__(self,val):
		return Vector(self.x - val[0], self.y - val[1])
	
	def __iadd__(self, val):
		self.x += val[0]
		self.y += val[1]
		return self
		
	def __isub__(self, val):
		self.x -= val[0]
		self.y -= val[1]
		return self
	
	def __div__(self, val):
		if hasattr(val, "__getitem__"):
			return Vector(self.x / val[0], self.y / val[1])
		else:
			return Vector(self.x / val, self.y / val)
	
	def __mul__(self, val):
		if hasattr(val, "__getitem__"):
			return Vector(self.x * val[0], self.y * val[1])
		else:
			return Vector(self.x * val, self.y * val)
	
	def __idiv__(self, val):
		if hasattr(val, "__getitem__"):
			self.x /= val[0]
			self.y /= val[1]
			return self
		else:
			self.x /= val
			self.y /= val
			return self
		
	def __imul__(self, val):
		if hasattr(val, "__getitem__"):
			self.x *= val[0]
			self.y *= val[1]
			return self
		else:
			self.x *= val
			self.y *= val
			return self
		
	def __mod__(self, val):
		return Vector(self.x % val[0], self.y % val[1])
				
	def __getitem__(self, key):
		if key == 0:
			return self.x
		elif key == 1:
			return self.y
		else:
			raise IndexError("Invalid key ("+str(key)+") to Vector")
		
	def __setitem__(self, key, value):
		if key == 0:
			self.x = value
		elif key == 1:
			self.y = value
		else:
			raise IndexError("Invalid key ("+str(key)+") to Vector")
		
	def __str__(self):
		return "(" + str(self.x) + "," + str(self.y) + ")"
	
	def __hash__(self):
		return hash((self.x, self.y))
	def __eq__(self, other):
		return self.x == other[0] and self.y == other[1]

	def distance(self, point2 = (0,0)):
		return math.sqrt((self.x - point2[0]) ** 2 + (self.y - point2[1]) ** 2)
	def length(self):
		return math.sqrt(self.x**2 + self.y**2)
	def normalize(self):
		"""Normalize in place"""
		length = self.length()
		self.x /= length
		self.y /= length
	def normalized(self):
		"""Returns a normalized copy of this"""
		length = self.length()
		return Vector(self.x / length, self.y / length)

def VectorRand(rand=random):
	return Vector(rand.random()*2 -1, rand.random()*2 -1).normalized()
	
def isCoTerminal(angle, angle2):
	if angle > 0:				#if angle is positive, keep subtracting 360 until it is between 0 and +360
		while angle >= 360:
			angle -= 360
	elif angle < 0:
		while angle < 0:
			angle += 360
			
	if angle2 > 0:				#if angle is negative, keep adding 360 until it is between 0 and +360
		while angle2 >= 360:
			angle2 -= 360
	elif angle2 < 0:
		while angle2 < 0:
			angle2 += 360			
			
	if angle == angle2:			#if angles are the same, original angles are coterminal
		return True
	else:
		return False
		
def approxCoTerminal(angle, angle2, tolerance):		#returns true if angle2 is coterminal with angle + or - tolerance
	angle = int(angle)								#make angles ints if they arent already
	angle2 = int(angle2)
	testAngle = angle + tolerance					#max value we want to test
	minAngle = angle - tolerance					#min value we want to test
	while testAngle >= minAngle:
		if isCoTerminal(testAngle, angle2):
			return True
		testAngle -= 1
	return False

def smallestCoTerminal(angle):						#returns the smallest positive coterminal angle
	if angle > 0:				
		while angle >= 360:
			angle -= 360
	elif angle < 0:
		while angle < 0:
			angle += 360
	return angle
	
def angDiff(target, current):
	return (current - target + 180) % 360 - 180

def sign(num):
	return (num > 0 and 1) or (num < 0 and -1) or 0
