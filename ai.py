import physicalobject, resources
import pyglet
import math
from mathlib import Vector
import mathlib

class AI(object):
	def __init__(self, ship=None):
		self.ship = ship			#thing we are controlling
		self.window = pyglet.window.get_platform().get_default_display().get_windows()[0] #for globals
		self.enemies = []
		self.aggroed = False		#changed to true first time enemy gets within range. always true after.				
		
	def update(self, dt):
		self.enemies = []			#to clear out any enemies no longer present (dead, left system, etc)
		self.identifyFriendlies()	#scan system, see who's an enemy and who's a friend
		if len(self.enemies) > 0:		#if there are any enemies to target, target and attack one (if it's close enough)
			target = self.pickTarget()
			self.attackEnemy(dt, target)
		
	def identifyFriendlies(self):
		#check all the ships in solar system within range		
		#if is an enemy, append to enemies
		for ship in self.window.currentSystem.ships:
			if ship.faction != self.ship.faction:
				self.enemies.append(ship)
		if self.window.playerShip.faction != self.ship.faction:
			self.enemies.append(self.window.playerShip)
		
	def attackEnemy(self, dt, target):
		#if enemy is too far away, move closer
		#if enemy is in range, fire
		tarPath = self.getPath(self.ship, target)	#find a path to the target
		tarDist = Vector(target.x, target.y).distance(Vector(self.ship.x, self.ship.y))	#distance between ship and target
		if tarDist < self.ship.width*10:					#aggro distance. once aggroed, keep chasing enemy ships until dead.
			self.aggroed = True
		if self.aggroed:
			self.chase(dt, tar=target, stoppingDist=target.width*4, speed=1.0)	#keep pathing to target even if they're outside aggro range
		if tarDist < self.ship.width*4:
			self.ship.fire(self.ship.slots["mainGuns"])
			
	def pickTarget(self):	
			tar = self.enemies[0]
			for ship in self.enemies:
				if ship.hp < tar.hp:
					tar = ship		#target enemy with lowest health	
			return tar
			
	def getPath(self, obj, tar):	#find a path from an object to a target
		return Vector(tar.x - obj.x, tar.y - obj.y)		#straight path
														#TODO: add pathing around stuff		
			
	def pathToDest(self, dt, tar, stoppingDist=100, speed=0.25):	#path to within stoppingDist of destination at a percentage of normal thrust
			path = self.getPath(self.ship, tar)					#line from our ship to destination
			self.rotateToPath(path, dt)
			if mathlib.approxCoTerminal(self.pathAngle, self.ship.rotation, 10):
				#Are we close enough to start driving?
				if path.length() >= stoppingDist:	#if we're further than the distance we want to stop at, keep accelerating
					self.ship.increaseThrust(dt, speed)
				elif path.length() < stoppingDist:	#if we're close enough, brake
					self.ship.brake(dt)				
		
	def rotateToPath(self, path, dt):
		try:
			self.pathAngle = -1*(math.degrees(math.atan2(float(path.y), path.x)))		#angle of path relative to pos x axis. evaluates between 0 and +180 if below the x-axis, otherwise between 0 and -180, so we have to mess with this a bit		
		except ZeroDivisionError:										
			if path.y >= 0:												# if path is directly above us
				self.pathAngle = -90
			elif path.y < 0:											# if path is directly below us
				self.pathAngle = 90				
		angdiff = mathlib.angDiff(self.pathAngle, self.ship.rotation)		
		self.ship.rotation += min(self.ship.rotateSpeed * dt, abs(angdiff)) * -mathlib.sign(angdiff)	
		
	def chase(self, dt, tar, stoppingDist=100, speed=0.25):	#same as path but designed for ships chasing other ships
		desiredVel = self.ship.vel * (Vector(*tar.position)-self.ship.position).normalized()	#vector with the direction we want to be going, and same magnitude as our current vel
		wrongVel = self.ship.vel - desiredVel	#difference between the vel we want and our current vel 
		path = self.getPath(self.ship, tar)					#line from obj to destination
		self.rotateToPath(path, dt)
		
		if mathlib.approxCoTerminal(self.pathAngle, self.ship.rotation, 10):	#we're more or less pointing at our target
			if wrongVel.length() > self.ship.maxSpeed/4:
				self.ship.brake(dt)
			if path.length() >= stoppingDist:	#if we're further than the distance we want to stop at, keep accelerating
				self.ship.increaseThrust(dt, speed)
			elif path.length() < stoppingDist:	#if we're close enough, brake
				self.ship.brake(dt)								
			
class ShipAI(AI):
	def __init__(self, *args, **kwargs):
		super(ShipAI, self).__init__(*args, **kwargs)		
		#Placeholder for now, in case we want to separate out AI and Ship AI later
	
class PathAI(AI):
	def __init__(self, *args, **kwargs):
		super(PathAI, self).__init__(*args, **kwargs)
		
	def update(self, dt):
		pass
		
class MissileAI(AI):
	def __init__(self, *args, **kwargs):
		super(MissileAI, self).__init__(*args, **kwargs)
		flameImg = resources.loadImage("flame.png", center=True)
		flameImg.anchor_x = flameImg.width*2
		flameImg.anchor_y = flameImg.width/2
		self.flame = pyglet.sprite.Sprite(img=flameImg)
		self.flame.visible = False		
		
	def attackEnemy(self, dt, target):
		#if enemy is too far away, move closer
		#if enemy is in range, fire
		tarPath = self.getPath(self.ship, target)	#find a path to the target
		tarDist = Vector(target.x, target.y).distance(Vector(self.ship.x, self.ship.y))	#distance between ship and target
		if tarDist < target.width*10:					#aggro distance. once aggroed, keep chasing enemy ships until dead.
			self.aggroed = True
		if self.aggroed:
			self.chase(dt, tar=target, stoppingDist=target.width/2, speed=1.0)	#keep going max speed until we're right on top of the target (at which point, kaboom)

				
	def chase(self, dt, tar, stoppingDist=100, speed=0.25):	#same as path but designed for ships chasing other ships
		desiredVel = self.ship.vel * (Vector(*tar.position)-self.ship.position).normalized()	#vector with the direction we want to be going, and same magnitude as our current vel
		wrongVel = self.ship.vel - desiredVel	#difference between the vel we want and our current vel 
		path = self.getPath(self.ship, tar)					#line from obj to destination
		self.rotateToPath(path, dt)
		
		if mathlib.approxCoTerminal(self.pathAngle, self.ship.rotation, 10):	#we're more or less pointing at our target
			if wrongVel.length() > self.ship.maxSpeed/4:
				self.ship.brake(dt)
			if path.length() >= stoppingDist:	#if we're further than the distance we want to stop at, keep accelerating
				self.ship.increaseThrust(dt, speed)
				self.flame.rotation = self.ship.rotation
				self.flame.x = self.ship.x
				self.flame.y = self.ship.y
				self.flame.visible = True				
			elif path.length() < stoppingDist:	#if we're close enough, brake
				self.ship.brake(dt)				
						
	def pickTarget(self):	
			tar = self.enemies[0]
			for ship in self.enemies:
				shipDist = Vector(ship.x, ship.y).distance(Vector(self.ship.x, self.ship.y))	#distance between us and the ship were examining
				tarDist = Vector(tar.x, tar.y).distance(Vector(self.ship.x, self.ship.y))		#distance between us and the current target
				if  shipDist < tarDist:
					tar = ship		#target closest enemy	
			return tar		
