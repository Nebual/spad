import pyglet
import mathlib
from mathlib import Vector
import physicalobject, resources
import math, time, inspect, sys

class Component(object):
	type = "component"
	licenseCost = 0
	img = "items/base.png"
	def __init__(self, ship=None):
		self.ship = ship
		
	def addToShip(self, ship, slot):		#add a component to a ship. Slot must be a list, e.g. mainGuns
		self.ship = ship
		for i in range(len(slot)):
			if slot[i] == 0:
				slot[i] = self
				break

class Gun(Component):
	category = "weapon"
	
	def __init__(self, gunType="cannon", *args, **kwargs):
		super(Gun, self).__init__(*args, **kwargs)
		self.window = pyglet.window.get_platform().get_default_display().get_windows()[0]	
		self.shootTime = time.time()
		self.delay = 0.25
		self.gunType = gunType	

class Cannon(Gun):
	type = "cannon"
	img = "items/laserGun1.png"
	def __init__(self):
		super(Cannon, self).__init__(gunType="cannon")
		
	def fire(self):	
		if time.time() > self.shootTime:		
			bulletImg = resources.loadImage("bullet.png", center=True)
			bullet = physicalobject.Bullet(x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.currentSystem.batch)
			bullet.rotation = self.ship.rotation
			angleRadians = -math.radians(self.ship.rotation)
			bullet.vel.x = (self.ship.vel.x + math.cos(angleRadians) * bullet.maxSpeed)
			bullet.vel.y = (self.ship.vel.y + math.sin(angleRadians) * bullet.maxSpeed)	
			self.window.currentSystem.tempObjs.append(bullet)
			self.shootTime = time.time() + self.delay
		
class Turret(Gun):
	type = "turret"
	def __init__(self, vec=Vector(0,0)):
		super(Turret, self).__init__(gunType="turret")				
		
	def fire(self):	
		if time.time() > self.shootTime:		
			#direction = tar.normalized()
			#direction.x *= 100
			#direction.y *= 100
			#target = Vector(direction.x - self.ship.x, direction.y - self.ship.y)	
			bulletImg = resources.loadImage("bullet.png", center=True)
			bullet = physicalobject.Bullet(x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.currentSystem.batch)
			bullet.vel.x = ((self.ship.vel.x/2) + tar.x - self.ship.x) * bullet.turretSpeed
			bullet.vel.y = ((self.ship.vel.y/2) + tar.y - self.ship.y) * bullet.turretSpeed
			self.window.currentSystem.tempObjs.append(bullet)
			self.shootTime = time.time() + self.delay	
				
class GravGun(Gun):
	type = "gravgun"
	img = "items/gravGun.png"
	def __init__(self):
		super(GravGun, self).__init__(gunType="grav")
		self.delay = 2
				
	def fire(self):	
		if time.time() > self.shootTime:		
			bulletImg = resources.loadImage("bullet.png", center=True)
			bullet = physicalobject.GravBullet(x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.mainBatch, deathTime=0.5)
			bullet.rotation = self.ship.rotation
			angleRadians = -math.radians(self.ship.rotation)
			bullet.vel.x = (self.ship.vel.x + math.cos(angleRadians) * bullet.maxSpeed)
			bullet.vel.y = (self.ship.vel.y + math.sin(angleRadians) * bullet.maxSpeed)
			self.window.currentSystem.tempObjs.append(bullet)
			self.shootTime = time.time() + self.delay			

class Engine(Component):
	
	def __init__(self, *args, **kwargs):
		super(Engine, self).__init__(*args, **kwargs)
		self.strength = 200

class Battery(Component):
	
	def __init__(self, *args, **kwargs):
		super(Battery, self).__init__(*args, **kwargs)
		self.capacity = 100

Components = []
def init():
	for name, Cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
		if issubclass(Cls, Component):
			#Create a new instance of each component
			instance = Cls()
			Components.append(instance)
