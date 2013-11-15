import pyglet
import random, os
import physicalobject, resources
from mathlib import Vector

planetImages = [x for x in os.listdir("resources/planets/") if "png" in x or "jpg" in x]

class SolarSystem(object):
	
	def __init__(self, x=0, y=0, seed=0):
		self.window = pyglet.window.get_platform().get_default_display().get_windows()[0]
		self.batch = pyglet.graphics.Batch()
		self.group1 = pyglet.graphics.OrderedGroup(1)
		self.group2 = pyglet.graphics.OrderedGroup(2)
		self.planets = []
		starImage = resources.loadImage("sun.png", center=True) 
		self.star = physicalobject.Sun(x=x, y=y, img=starImage, batch=self.batch, group=self.group1)
		self.planets.append(self.star)
		self.seed = seed
		self.rand = random.Random()
		self.rand.seed(73789 + seed*14032)				
		self.ships = []
		self.tempObjs = []
		self.populateShips()

		dist = 100
		for i in range(self.rand.randint(1, 10)):
			#Find a random new position that isn't too close to any other planets
			dist += 200 + self.rand.random()*200
			newX, newY = Vector(self.rand.random()*2 -1, self.rand.random()*2 -1).normalized() * dist
			
			kind = self.rand.choice(planetImages)
			planetImage = resources.loadImage("planets/"+kind, center=True)
			newPlanet = physicalobject.Planet(x=self.star.x + newX, y=self.star.y + newY, img=planetImage, batch=self.batch)
			newPlanet.populate(rand=self.rand, kind=kind)
			newPlanet.scale *= min(1, 0.65 + self.rand.random() / 2.0)
			self.planets.append(newPlanet)
		self.radius = dist
		
		self.minimap = resources.copyImage(resources.loadImage("minimap.png"))
		self.window.hud.minimap.image = self.minimap
		greenCircle = resources.loadImage("circle_green.png", center=True)
		self.minimap.blit_into(resources.loadImage("circle_gold.png", center=True).image_data, 50, 50, 0)
		for planet in self.planets:
			if planet.isSun: continue
			self.minimap.blit_into(greenCircle.image_data, int(50 + planet.x / dist * 50), int(50 + planet.y / dist * 50), 0)
	
	def nearestPlanet(self, vec):
		nearestDist = vec.distance(Vector(self.star.x, self.star.y))
		nearest = self.star
		for planet in self.planets:
			dist = vec.distance((planet.x, planet.y))
			if dist < nearestDist:
				nearestDist = dist
				nearest = planet
		return nearest
		
	def update(self, dt):
		for obj in self.tempObjs:
			obj.update(dt)
		for obj in self.ships:
			obj.update(dt)
	
	def populateShips(self):
		dummyImg = resources.loadImage("playership.png", center=True)					#test stuff
		pos = 1000		
		for i in xrange(3):
			ship = physicalobject.AIShip(x=pos, y=0, img=dummyImg, batch=self.batch, group=self.group2)
			pos += 100
			self.ships.append(ship)
