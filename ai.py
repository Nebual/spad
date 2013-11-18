import physicalobject
import pyglet
import math
from mathlib import Vector
import mathlib

class ShipAI(object):
	def __init__(self, ship):
		self.ship = ship			#refer to ship whose AI we are
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
		tarPath = self.ship.getPath(self.ship, target)	#find a path to the target
		tarDist = Vector(target.x, target.y).distance(Vector(self.ship.x, self.ship.y))	#distance between ship and target
		if tarDist < self.ship.width*10:					#aggro distance. once aggroed, keep chasing enemy ships until dead.
			self.aggroed = True
		if self.aggroed:
			self.ship.chase(dt, tar=target, stoppingDist=target.width*4, speed=1.0)	#keep pathing to target even if they're outside aggro range
		if tarDist < self.ship.width*4:
			self.ship.fire(self.ship.mainGuns)
			
	def pickTarget(self):	
			tar = self.enemies[0]
			for ship in self.enemies:
				if ship.hp < tar.hp:
					tar = ship		#target enemy with lowest health	
			return tar
