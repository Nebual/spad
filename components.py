import pyglet
import mathlib
from mathlib import Vector
import physicalobject, resources
import math, time, inspect, sys

class Component(object):
	category = "" 		#Broad, used by shop tab, like "weapon", "engine", "sensor"
	type = "" 			#Narrow, describes how the component works, like "lasercannon", "laserturret", "ionthruster"
	subType = "" 		#Unique to a particular combination of attributes, like "lasercannonsmall", "gravgun100"
	name = ""			#Player viewable pretty name, like "Pulse Laser Turret - 10W", "Singularity Launcher"
	img = "items/base.png" #Used by the shop
	licenseCost = 0		#In credits
	goodsCost = {}		#Keys are materials, values are # of tons of that material required for crafting
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
	
	delay = 0.25
	
	def __init__(self, *args, **kwargs):
		super(Gun, self).__init__(*args, **kwargs)
		self.window = pyglet.window.get_platform().get_default_display().get_windows()[0]	
		self.shootTime = time.time()

class Cannon(Gun):
	type = "cannon"
	subType = "laserGun1"
	name = "Pulse Laser Cannon - 10W"
	img = "items/laserGun1.png"
	licenseCost = 3000
	goodsCost = {"steel": 5, "lithium": 5}
	
	def fire(self):	
		if time.time() > self.shootTime:		
			bulletImg = resources.loadImage("bullet.png", center=True)
			bullet = physicalobject.Bullet(ship=self.ship, x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.currentSystem.batch)
			bullet.rotation = self.ship.rotation
			angleRadians = -math.radians(self.ship.rotation)
			bullet.vel.x = (self.ship.vel.x + math.cos(angleRadians) * bullet.maxSpeed)
			bullet.vel.y = (self.ship.vel.y + math.sin(angleRadians) * bullet.maxSpeed)	
			self.window.currentSystem.tempObjs.append(bullet)
			self.shootTime = time.time() + self.delay
		
class Turret(Gun):
	type = "turret"
	subType = "laserTurret1"
	name = "Pulse Laser Turret - 10W"
	img = "items/laserGun1.png"	
	licenseCost = 5000
	goodsCost = {"steel": 7, "lithium": 5}
	
	def fire(self):	
		if time.time() > self.shootTime:		
			#direction = tar.normalized()
			#direction.x *= 100
			#direction.y *= 100
			#target = Vector(direction.x - self.ship.x, direction.y - self.ship.y)	
			bulletImg = resources.loadImage("bullet.png", center=True)
			bullet = physicalobject.Bullet(ship=self.ship, x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.currentSystem.batch)
			bullet.vel.x = ((self.ship.vel.x/2) + tar.x - self.ship.x) * bullet.turretSpeed
			bullet.vel.y = ((self.ship.vel.y/2) + tar.y - self.ship.y) * bullet.turretSpeed
			self.window.currentSystem.tempObjs.append(bullet)
			self.shootTime = time.time() + self.delay	
				
class GravGun(Gun):
	type = "gravgun"
	subType = "gravgun"
	img = "items/gravGun.png"
	name = "Singularity Launcher"
	licenseCost = 7000 #TODO: This should be balanced to be way more expensive
	goodsCost = {"steel": 1, "lithium": 1, "medicine": 1}
	
	delay = 2
	
	def fire(self):	
		if time.time() > self.shootTime:		
			bulletImg = resources.loadImage("bullet.png", center=True)
			bullet = physicalobject.GravBullet(ship=self.ship, x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.mainBatch, deathTime=0.5)
			bullet.rotation = self.ship.rotation
			angleRadians = -math.radians(self.ship.rotation)
			bullet.vel.x = (self.ship.vel.x + math.cos(angleRadians) * bullet.maxSpeed)
			bullet.vel.y = (self.ship.vel.y + math.sin(angleRadians) * bullet.maxSpeed)
			self.window.currentSystem.tempObjs.append(bullet)
			self.shootTime = time.time() + self.delay	
			
class MissileGun(Gun):
	type = "missilegun"
	supType = "missilegun"
	img = "items/laserGun1.png"
	name = "Missile Launcher"
	
	delay = 2
	
	def fire(self):
		if time.time() > self.shootTime:		
			bulletImg = resources.loadImage("bullet.png", center=True)
			bullet = physicalobject.Missile(ship=self.ship, x=self.ship.x, y=self.ship.y, img=bulletImg, batch=self.window.mainBatch, deathTime=5)
			bullet.rotation = self.ship.rotation
			angleRadians = -math.radians(self.ship.rotation)
			bullet.vel.x = (self.ship.vel.x + math.cos(angleRadians) * bullet.maxSpeed)/2
			bullet.vel.y = (self.ship.vel.y + math.sin(angleRadians) * bullet.maxSpeed)/2
			self.window.currentSystem.tempObjs.append(bullet)
			self.shootTime = time.time() + self.delay	
			
class Engine(Component):
	type = "engine"
	subType = "engine"
	name = "Engine"
	
	def __init__(self, *args, **kwargs):
		super(Engine, self).__init__(*args, **kwargs)
		self.strength = 200
class Engine2(Component):
	type = "engine2"
	subType = "engine2"
	name = "Engine2"
	
	def __init__(self, *args, **kwargs):
		super(Engine2, self).__init__(*args, **kwargs)
		self.strength = 300

class Battery(Component):
	img = "items/battery.png"
	type = "battery"
	subType = "battery"
	name = "Battery"
	def __init__(self, *args, **kwargs):
		super(Battery, self).__init__(*args, **kwargs)
		self.capacity = 100

Components = [] #To populate the shop
def init():
	for name, Cls in inspect.getmembers(sys.modules[__name__], inspect.isclass):
		if issubclass(Cls, Component):
			#Create a new instance of each component
			instance = Cls()
			if instance.name: 
				#Don't put it in the shop unless it has a name (to block parent classes)
				Components.append(instance)
