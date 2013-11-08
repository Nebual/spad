import pyglet
import mathlib
from mathlib import Vector
import physicalobject, resources
import math, time

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
			self.shootTime = time.time() + self.delay	
			
	def cannon(self):
		bulletImg = resources.loadImage("bullet.png", center=True)
		bullet = physicalobject.Bullet(x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.mainBatch)
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
		bullet = physicalobject.Bullet(x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.mainBatch)
		bullet.vel.x = ((self.ship.vel.x/2) + tar.x - self.ship.x) * bullet.turretSpeed
		bullet.vel.y = ((self.ship.vel.y/2) + tar.y - self.ship.y) * bullet.turretSpeed
		self.window.currentSystem.tempObjs.append(bullet)	
