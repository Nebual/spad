import pyglet
import mathlib
from mathlib import Vector
import physicalobject, resources
import math, time, inspect, sys

class Component(object):
	type = "undefined"
	licenseCost = 0
	img = "items/base.png"

class Gun(object):
	
	def __init__(self, ship, gunType="cannon"):
		self.window = pyglet.window.get_platform().get_default_display().get_windows()[0]	
		self.shootTime = time.time()
		self.ship = ship
		self.delay = 0.25
		self.gunType = gunType
	
	def fire(self, vec=Vector(0,0)):
		if time.time() > self.shootTime:	
			if self.gunType == "cannon":
				self.cannon()
			elif self.gunType == "turret":
				self.turret(vec)
			elif self.gunType == "grav":
				self.gravGun()
				self.delay = 2
				
			self.shootTime = time.time() + self.delay	
			
	def cannon(self):
		bulletImg = resources.loadImage("bullet.png", center=True)
		bullet = physicalobject.Bullet(x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.currentSystem.batch)
		bullet.rotation = self.ship.rotation
		angleRadians = -math.radians(self.ship.rotation)
		bullet.vel.x = (self.ship.vel.x + math.cos(angleRadians) * bullet.maxSpeed)
		bullet.vel.y = (self.ship.vel.y + math.sin(angleRadians) * bullet.maxSpeed)	
		self.window.currentSystem.tempObjs.append(bullet)
				
							
	def turret(self, tar):
		#direction = tar.normalized()
		#direction.x *= 100
		#direction.y *= 100
		#target = Vector(direction.x - self.ship.x, direction.y - self.ship.y)	
		bulletImg = resources.loadImage("bullet.png", center=True)
		bullet = physicalobject.Bullet(x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.currentSystem.batch)
		bullet.vel.x = ((self.ship.vel.x/2) + tar.x - self.ship.x) * bullet.turretSpeed
		bullet.vel.y = ((self.ship.vel.y/2) + tar.y - self.ship.y) * bullet.turretSpeed
		self.window.currentSystem.tempObjs.append(bullet)
		
	def gravGun(self):
		bulletImg = resources.loadImage("bullet.png", center=True)
		bullet = physicalobject.GravBullet(x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.mainBatch, deathTime=0.5)
		bullet.rotation = self.ship.rotation
		angleRadians = -math.radians(self.ship.rotation)
		bullet.vel.x = (self.ship.vel.x + math.cos(angleRadians) * bullet.maxSpeed)
		bullet.vel.y = (self.ship.vel.y + math.sin(angleRadians) * bullet.maxSpeed)
		self.window.currentSystem.tempObjs.append(bullet)			


class Cannon(Gun, Component):
	type = "Laser Cannon I"
	img = "items/laserGun1.png"
	def __init__(self, ship=None):
		super(Cannon, self).__init__(ship, gunType="cannon")
class SingularityGun(Gun, Component):
	type = "Singularity Launcher"
	img = "items/singularityGun.png"
	def __init__(self, ship=None):
		super(SingularityGun, self).__init__(ship, gunType="grav")

Components = []
def init():
	for name, Cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
		if Component in Cls.__bases__:
			#Create a new instance of each component
			instance = Cls()
			Components.append(instance)
