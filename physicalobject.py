import pyglet
from pyglet.window import key
import resources, hud, components, ai
import math
import mathlib

from mathlib import Vector

class PhysicalObject(pyglet.sprite.Sprite):
	
	def __init__(self, *args, **kwargs):
		super(PhysicalObject, self).__init__(*args, **kwargs)
		
		self.maxSpeed = 600.0
		self.vel = Vector(0.0, 0.0)
		self.window = pyglet.window.get_platform().get_default_display().get_windows()[0]
		self.gravity = 0
		self.rotateSpeed = 200.0
		self.pathAngle = 0
		self.baseThrust = 300.0
		self.thrust = self.baseThrust
		self.closing = False		#TODO: find a way around this var	
		
		
	def update(self, dt):					#updates position, accounting for time elapsed (dt)
		for planet in self.window.currentSystem.planets:
			self.gravitate(dt, planet)
		for obj in self.window.currentSystem.tempObjs:
			self.gravitate(dt, obj)	
		self.x += self.vel.x * dt
		self.y += self.vel.y * dt
		
	def getPath(self, obj, tar):	#find a path from an object to a target
		return Vector(tar.x - obj.x, tar.y - obj.y)		#straight path
														#TODO: add pathing around stuff		
			
	def pathToDest(self, dt, tar, stoppingDist=100, speed=0.25):	#path to within stoppingDist of destination at a percentage of normal thrust
			path = self.getPath(self, tar)					#line from obj to destination
			self.rotateToPath(path, dt)
			if mathlib.approxCoTerminal(self.pathAngle, self.rotation, 10):
				#Are we close enough to start driving?
				if path.length() >= stoppingDist:	#if we're further than the distance we want to stop at, keep accelerating
					self.increaseThrust(dt, speed)
				elif path.length() < stoppingDist:	#if we're close enough, brake
					self.brake(dt)				
		
	def rotateToPath(self, path, dt):
		try:
			self.pathAngle = -1*(math.degrees(math.atan2(float(path.y), path.x)))		#angle of path relative to pos x axis. evaluates between 0 and +180 if below the x-axis, otherwise between 0 and -180, so we have to mess with this a bit		
		except ZeroDivisionError:										
			if path.y >= 0:												# if path is directly above us
				self.pathAngle = -90
			elif path.y < 0:											# if path is directly below us
				self.pathAngle = 90				
		angdiff = mathlib.angDiff(self.pathAngle, self.rotation)		
		self.rotation += min(self.rotateSpeed * dt, abs(angdiff)) * -mathlib.sign(angdiff)	
		
	def chase(self, dt, tar, stoppingDist=100, speed=0.25):	#same as path but designed for ships chasing other ships
		desiredVel = self.vel * (Vector(*tar.position)-self.position).normalized()	#vector with the direction we want to be going, and same magnitude as our current vel
		wrongVel = self.vel - desiredVel	#difference between the vel we want and our current vel 
		path = self.getPath(self, tar)					#line from obj to destination
		self.rotateToPath(path, dt)
		
		if mathlib.approxCoTerminal(self.pathAngle, self.rotation, 10):	#we're more or less pointing at our target
			if wrongVel.length() > self.maxSpeed/4:
				self.brake(dt)
			if path.length() >= stoppingDist:	#if we're further than the distance we want to stop at, keep accelerating
				self.increaseThrust(dt, speed)
			elif path.length() < stoppingDist:	#if we're close enough, brake
				self.brake(dt)					
				
	def gravitate(self, dt, planet):
		if planet.gravity != 0:
			distance = Vector(planet.x,planet.y).distance((self.x,self.y))
			distance2 = distance - planet.radius
			if distance2 < 300:
				if distance > planet.radius: 
					speedChange = ((planet.gravity) / distance2**2.5) * dt
				#else:
				#	speedChange = -((1000000 * planet.gravity) / 200**2) * dt
					if self.thrust: speedChange = min(self.thrust * 0.75 * dt, speedChange)
					self.vel += Vector(planet.x - self.x, planet.y - self.y).normalized() * speedChange
					
	def collide(self):
		pass
		
class Ship(PhysicalObject):											
	def __init__(self, *args, **kwargs):
		super(Ship, self).__init__(*args, **kwargs)
		self.ai = None
		self.faction = "bad"
		self.hp = 30
		self.dead = False
		self.shipType = "light"
		self.baseMass = 0
		self.mass = self.baseMass
		self.slots = {
			"mainGuns": [0 for x in range(1)],					#slots for components (room for 1 by default)
			"secondaryGuns": [0 for x in range(1)],				#empty slots represented by a 0
			"batteries": [0 for x in range(1)],
			"engines": [0],
		}
		self.cargo = {}
		self.cargoMax = 50
		self.credits = 0	
		self.initShipType()
		self.initComponents()	
		self.updateMass()
				
	def update(self, dt):
		super(Ship, self).update(dt)	
		if self.hp <= 0:
			self.explode(dt)
		if self.ai != None:
			self.ai.update(dt)
		
	def updateMass(self):							#update mass and thrust based on how much cargo we have
		self.mass = self.baseMass
		self.thrust = self.baseThrust
		for item in self.cargo.values():
			self.mass += item.mass * item.quantity
		self.thrust *= self.slots["engines"][0].strength/self.mass #TODO: This only handles one engine
	
	def addCargo(self, kind, amount):
		"""Adds (or removes) cargo to the self.cargo hold"""
		if amount < 0 and kind not in self.cargo: return
		if kind in self.cargo:
			self.cargo[kind].quantity += amount
		else:
			self.cargo[kind] = Cargo(kind, amount)
		if self.cargo[kind].quantity <= 0: del self.cargo[kind]
		self.updateMass()
		
	def initComponents(self):									#default components, should later read in from somewhere 
		components.Cannon().addToShip(ship=self)
		components.Turret().addToShip(ship=self)		
		components.Engine().addToShip(ship=self)
			
	def initShipType(self):
		if self.shipType == "light":
			self.baseMass = 270.0								
		
	def explode(self, dt):
		if not self.dead:
			self.dead = True
			self.oldWidth = self.width
			pyglet.clock.schedule_once(self.die, 0.5)			
			self.image = resources.loadImage("explosion.png", center=True)
			self.scale = 0.1
		if self.dead:
			if self.scale < self.oldWidth/250.0:
				self.scale += 2 * self.oldWidth/250.0 * dt
				self.opacity -= 300 * dt
			else:
				self.opacity -= 510 * dt			

	def die(self, dt):
		for category in self.slots:
			self.slots[category][:] = []
		self.ai = None
		self.window.currentSystem.ships.remove(self)
		
		
	def increaseThrust(self, dt, mul):				#increase speed up to max speed
		angleRadians = -math.radians(self.rotation)
		self.vel += Vector(math.cos(angleRadians), math.sin(angleRadians)) * (self.thrust * dt * mul)
		s = self.vel.length()
		if s > self.maxSpeed:
			self.vel *= self.maxSpeed / s
			
	def brake(self, dt, mul=0.75):
		self.vel.x -= (self.vel.x > 0 and 1 or -1) * min(self.thrust * mul * dt, abs(self.vel.x))
		self.vel.y -= (self.vel.y > 0 and 1 or -1) * min(self.thrust * mul * dt, abs(self.vel.y))				
	
	def fire(self, gunList, vec=Vector(0,0)):
		for gun in gunList:
			if gun != 0:
				if "turret" in gun.type:
					gun.fire(vec)
				else:
					gun.fire()
			
class AIShip(Ship):
	def __init__(self, *args, **kwargs):
		super(AIShip, self).__init__(*args, **kwargs)
		self.thrust = 300.0
			
	def update(self, dt):
		super(AIShip, self).update(dt)
		self.attackEnemy(dt, self.window.playerShip)
		
	def attackEnemy(self, dt, enemy):
		enemyPath = Vector(enemy.x -self.x, enemy.y - self.y)
		enemyDist = Vector(enemy.x, enemy.y).distance(Vector(self.x, self.y))
		if enemyDist < self.width*4:
			self.rotateToPath(enemyPath, dt)								
		
class Player(Ship):
	
	def __init__(self, *args, **kwargs):
		playerImage = resources.loadImage("playership.png", center=True)	#player texture
		super(Player, self).__init__(img=playerImage, *args, **kwargs)
		self.faction = "good"
		self.hp = 1000 #We don't want player to die right now
		self.rotation = 135
		self.starmode = 1
		self.keyHandler = key.KeyStateHandler()
		self.credits = 40000
		self.licenses = {}
		
		@self.window.event
		def on_key_press(symbol, modifiers):
			self.keyPress(symbol, modifiers)
			
		@self.window.event
		def on_key_release(symbol, modifiers):
			self.keyRelease(symbol, modifiers)
			
		@self.window.event
		def on_mouse_press(x, y, button, modifiers): self.mousePress(x, y, button, modifiers)
	
	def mousePress(self, x, y, button, modifiers):
		vec = self.window.camera + (x, y)
		if button == pyglet.window.mouse.LEFT:
			planet = self.window.currentSystem.nearestPlanet(vec)
			if vec.distance((planet.x, planet.y)) < planet.radius:
				self.window.hud.select(planet)
		elif button == pyglet.window.mouse.RIGHT:
				self.fire(self.slots["secondaryGuns"], vec)
	
	def keyPress(self, symbol, modifiers):
		"""This function is run once per key press"""
		if symbol == key.V:
			self.starmode += 1
			if self.starmode > 3: self.starmode = 0
			self.window.hud.modeLabel.text = "Starmode: "+str(self.starmode)
			self.window.background.generate(mode=self.starmode)
		elif symbol == key.L:
			planet = self.window.hud.select(self.window.currentSystem.nearestPlanet(Vector(self.x, self.y)))
			if isinstance(planet, Planet):
				if Vector(*self.position).distance(planet.position) < (planet.radius + 20):
					if self.vel.length() < 30:
						self.window.temp = hud.PlanetFrame(planet)
					else:
						print "You're moving too fast to land!" #TODO: These should be displayed ingame
				else:
					print "You're too far from the planet to land!"
		elif symbol == key.Z:
			self.window.hud.deselect()
		elif symbol == key.J:
			#TODO: Add target system selector
			if self.window.currentSystem.seed != 0:
				self.targetSystem = 0
			else:
				self.targetSystem = 5
			self.warpTime = 0
			resources.warpSound.play()
			pyglet.clock.schedule_interval(self.doWarp, 0.1)
		elif symbol == key.C:
			self.slots["mainGuns"][0] = 0
			newGun = components.Cannon()
			newGun.addToShip(ship=self) 
		elif symbol == key.G:
			self.slots["mainGuns"][0] = 0
			newGun = components.GravGun()
			newGun.addToShip(ship=self)
		elif symbol == key.M:
			self.slots["mainGuns"][0] = 0
			newGun = components.MissileGun()
			newGun.addToShip(ship=self)			
			
	def keyRelease(self, symbol, modifiers):
		pass
		
	def update(self, dt):							#player updater, checks for key presses
		super(Player, self).update(dt)	
		
		if self.keyHandler[key.LEFT]:
			self.rotation -= self.rotateSpeed * dt
		if self.keyHandler[key.RIGHT]:
			self.rotation += self.rotateSpeed * dt
		if self.keyHandler[key.UP]:
			self.increaseThrust(dt, 1)
		if self.keyHandler[key.DOWN]:
			self.increaseThrust(dt, -1)
		if self.keyHandler[key.X]:					#brake
			self.brake(dt)
		if self.keyHandler[key.T]:
			if not self.window.hud.selected:
				self.window.hud.select(self.window.currentSystem.nearestPlanet(Vector(self.x, self.y)))
			dest = self.window.hud.selected
			self.pathToDest(dt, dest, 100, 0.25)
		if self.keyHandler[key.SPACE]:
			self.fire(self.slots["mainGuns"])
		self.updateCamera(dt)
		
	def updateCamera(self, dt):
		"""Shift the camera to always follow the Player."""
		if (self.x - self.window.camera.x) > (self.window.width / 1.5):
			self.window.camera.x += ((self.x - self.window.camera.x) - (self.window.width / 1.5)) * 3 * dt
		elif (self.x - self.window.camera.x) < (self.window.width / 3):
			self.window.camera.x += ((self.x - self.window.camera.x) - (self.window.width / 3)) * 3 * dt
		if (self.y - self.window.camera.y) > (self.window.height / 1.5):
			self.window.camera.y += ((self.y - self.window.camera.y) - (self.window.height / 1.5)) * 3 * dt
		elif (self.y - self.window.camera.y) < (self.window.height / 3):
			self.window.camera.y += ((self.y - self.window.camera.y) - (self.window.height / 3)) * 3 * dt
	
	def doWarp(self, dt):
		self.warpTime += dt
		angleRadians = -math.radians(self.rotation)
		self.vel += Vector(math.cos(angleRadians), math.sin(angleRadians)) * (self.thrust/7 * (1+self.warpTime) * dt)
		if self.warpTime > 6: #TODO: Time should be dependant on ship's acceleration - also sound time
			self.window.enterSystem(self.targetSystem)
			pyglet.clock.unschedule(self.doWarp)

class Planet(PhysicalObject):
	name = "undefined"
	isSun = False
	habited = False
	hasTrade = False
	hasMissions = False
	hasParts = False
	hasShipyard = False
	
	def __init__(self, *args, **kwargs): 
		super(Planet, self).__init__(*args, **kwargs)
		self.gravity = self.width*self.height*300			#Gravity scales with size of image
		self.radius = (self.width + self.height) / 4
		self.goods = {}

	def populate(self, rand, kind):
		if "rock" in kind:
			if "garden" in kind:
				self.name = "GDN_%.4d" % rand.randrange(1,9999)
				self.habited = rand.random() < 0.75
				self.hasTrade = self.habited
				self.hasMissions = self.habited
				if self.habited:
					self.hasParts = rand.random() < 0.6
					if self.hasParts: 
						self.hasShipyard = rand.random() < 0.5
			else:
				self.name = "RCK_%.4d" % rand.randrange(1,9999)
				self.habited = rand.random() < 0.25
				self.hasTrade = self.habited
				self.hasMissions = self.habited
		else:
			#Gas
			self.name = "GAS_%.4d" % rand.randrange(1,9999)
		if self.hasTrade:
			if rand.random() < 0.90: self.goods["food"] = 		80	+ int(rand.random()*4)*20	#80-160
			if rand.random() < 0.85: self.goods["steel"] = 		200	+ int(rand.random()*4)*50	#200-400
			if rand.random() < 0.75: self.goods["lithium"] = 	600	+ int(rand.random()*4)*100 	#600-1000
			if rand.random() < 0.75: self.goods["silicon"] = 	400	+ int(rand.random()*3)*100	#400-700
			if rand.random() < 0.80: self.goods["medicine"] = 	300	+ int(rand.random()*4)*75	#300-600
		
class Sun(Planet):
	isSun = True
	
	name = "TEMPORARY DEBUG SUN"
	habited = True
	hasTrade = True
	hasMissions = True
	hasParts = True
	hasShipyard = True
	def __init__(self, *args, **kwargs):
		super(Sun, self).__init__(*args, **kwargs)
		self.goods = {"steel": 200, "lithium": 600}

class Bullet(PhysicalObject):
	def __init__(self, ship=None, deathTime=0.5, *args, **kwargs):
		super(Bullet, self).__init__(*args, **kwargs)
		self.maxSpeed = 600
		self.turretSpeed = 5
		self.deathTime = deathTime
		self.ship = ship			
		pyglet.clock.schedule_once(self.die, self.deathTime)		
		
	def update(self, dt):					#updates position, accounting for time elapsed (dt)		
		self.x += self.vel.x * dt
		self.y += self.vel.y * dt
		self.checkCollision()
	
	def die(self, dt=0):	#dt because pyglet's clock passes it, but we don't need it
		pyglet.clock.unschedule(self.die)
		self.window.currentSystem.tempObjs.remove(self)
		
	def checkCollision(self):
		for obj in self.window.currentSystem.ships:
			if Vector(self.x, self.y).distance(Vector(obj.x, obj.y)) < obj.width:
				self.collide(obj)		
	
	def collide(self, obj):
		if hasattr(obj, "faction"):
			if self.ship.faction == obj.faction:
				return						#don't collide if ship is the same faction as the one that fired the bullet
		if hasattr(obj, "hp"):
			obj.hp -= 10
			self.die()


class GravBullet(Bullet):									#Spawns a black hole when it dies
	def die(self, dt=0):
		super(GravBullet, self).die(dt)		
		singImg = resources.loadImage("singularity.png", center=True)
		singularity = Singularity(x=self.x, y=self.y, img=singImg, batch=self.window.currentSystem.batch, group=self.window.currentSystem.group1, deathTime=3)
		self.window.currentSystem.tempObjs.append(singularity)
		

class Singularity(Bullet):									#Effect for gravity gun, spawned from GravBullet
	def __init__(self, *args, **kwargs):					
		super(Singularity, self).__init__(*args, **kwargs)
		#self.deathTime = 10
		self.gravity = self.width*self.height*5000			
		self.radius = (self.width + self.height) / 400
		self.opacity = 0.0									#TODO: Dying too early, figure out why.
		self.spawned = False
		self.despawning = False
		pyglet.clock.unschedule(self.die)
		pyglet.clock.schedule_once(self.despawn, self.deathTime)
	
	def update(self, dt):
		super(Singularity, self).update(dt)
		if not self.spawned:
			self.fadeIn(dt)
		if self.despawning:
			self.fadeOut(dt)
	
	def fadeIn(self, dt):
		if self.opacity < 255:
			self.opacity += 200 * dt
		if self.opacity >= 255:
			self.opacity = 255
			self.spawned = True
		
	def despawn(self, dt):			#seprate funct for changing flag so that fadeOut can take actual dt and not dt from clock.schedule_once
		self.despawning = True	
		
	def fadeOut(self, dt):			#this triggers AFTER the scheduled death time, so allow an extra sec or 2 for death
		if self.opacity > 0:
			self.opacity -= 200 * dt
		if self.opacity <= 0:
			self.opacity = 0
			self.die()
	
	def collide(self, obj):
		pass
		
class Missile(Bullet, Ship):
	def __init__(self, *args, **kwargs):
		super(Missile, self).__init__(*args, **kwargs)
		self.ai = ai.MissileAI(ship=self)
		self.faction = self.ship.faction
		self.maxSpeed = 600
		self.baseThrust = 1400
		self.thrust = self.baseThrust
		
	def update(self, dt):
		super(Missile, self).update(dt)
		if self.ai != None:
			self.ai.update(dt)
		
	def die(self, dt=0):
		super(Missile, self).die(dt)
		for category in self.slots:
			self.slots[category][:] = []
		self.ai = None
		
class InertialessMissile(Missile):					#TODO: add AI for this, mess with pathing--doesn't need to brake. Goes slow using pathToDest for some reason. 
	
	def increaseThrust(self, dt, mul):				#increase speed up to max speed
		angleRadians = -math.radians(self.rotation)
		self.vel = Vector(math.cos(angleRadians), math.sin(angleRadians)) * (self.thrust * dt * mul)
		s = self.vel.length()
		if s > self.maxSpeed:
			self.vel *= self.maxSpeed / s		
	

class Cargo(object):
	MASSES = {#mass in tonnes per cubic meter
		"food": 2.0,
		"steel": 7.85,
		"lithium": 3.5,
		"silicon": 2.0,
		"medicine": 1.5,
	}
	def __init__(self, kind, quantity=1):
		self.kind = kind
		self.quantity = quantity
		self.mass = self.MASSES.get(self.kind, 1.0)
