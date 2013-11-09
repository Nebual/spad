import random
import pyglet
import resources
from mathlib import Vector


class Background(object):
	def __init__(self, stars=None):
		self.stars = []
		self.batch = pyglet.graphics.Batch() #So batches are a bit like... a compiled list of a bunch of things with .draw functions. I made my own stars list, because I don't know what the inside of a Batch looks like, may be able to just use it.
		self.window = pyglet.window.get_platform().get_default_display().get_windows()[0] #For globals
		
		self.num = 80
		self.mode = 1
		self.seed = 0
		
		self.generate(stars)
		self.oldCamVel = Vector(0,0)

	def generate(self, num=None, mode=None, seed=None):
		num = num or self.num
		mode = mode or self.mode
		seed = seed or self.seed
		
		if mode % 2 == 0: 
			del self.stars[:]
		rnd = random.Random()
		im = resources.loadImage("star.png")
		
		if mode < 2:
			for i in range(num):
				rnd.seed(seed + i*10293)
				
				corePos = Vector(rnd.random()*self.window.width*1.5, rnd.random()*self.window.height*1.5)
				spr = pyglet.sprite.Sprite(im, x=corePos.x, y=corePos.y, batch=self.batch)
				
				size = rnd.random() ** 2.8
				spr.scale = size / 2
				spr.speed = size / 6
				self.stars.append(spr)
		elif mode < 4:
			for i in range(num):
				rnd.seed(seed + i*10293)
				
				corePos = Vector(rnd.random()*800*1.5, rnd.random()*600*1.5)
				spr = pyglet.sprite.Sprite(im, x=corePos.x, y=corePos.y, batch=self.batch)
				
				size = rnd.random()
				spr.scale = (size ** 2.8) / 2
				spr.speed = -size
				self.stars.append(spr)

	def update(self, dt):
		w, h = self.window.width, self.window.height
		camX, camY = self.window.camera.x, self.window.camera.y
		if self.window.playerShip.starmode % 2 == 0:
			velX, velY = self.window.playerShip.vel.x * dt, self.window.playerShip.vel.y * dt
		else:
			velX, velY = (camX - self.oldCamVel.x), (camY - self.oldCamVel.y)
		
		for spr in self.stars:
			spr.x -= velX * spr.speed
			if (spr.x + w*0.5) < camX: #going to the right
				spr.x += w*1.5
			if (spr.x - w*1.5) > camX:
				spr.x -= w*1.5
			spr.y -= velY * spr.speed
			if (spr.y + h*0.5) < camY:
				spr.y += h*1.5
			if (spr.y - h*1.5) > camY:
				spr.y -= h*1.5
		self.oldCamVel = Vector(camX, camY)
	
	def draw(self):
		self.batch.draw()
