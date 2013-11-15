import os, sys
sys.path.append("..")
from optparse import OptionParser
import pyglet

import physicalobject, resources, solarsystem, hud, components
from background import Background
from mathlib import Vector

class GameWindow(pyglet.window.Window):
	def __init__(self, *args, **kwargs):
		super(GameWindow, self).__init__(*args, **kwargs)
		
		self.mainBatch = pyglet.graphics.Batch() #"Misc" drawables
		self.hudBatch = pyglet.graphics.Batch() #Drawn after everything

		self.background = Background()
		self.playerShip = physicalobject.Player(x=0, y=0)		
		
		self.push_handlers(self.playerShip.keyHandler)

		self.paused = False
		self.camera = Vector(0,0)

		#Basically targetting either 1920x1080 (and 1920x1200) at 1, or 1366x768 ish at 0.5
		self.uiScale = 1
		if self.width < 1400 or self.height < 800: self.uiScale = 0.5
		
		self.hud = hud.HUD(window=self, batch=self.hudBatch)
		
		self.currentSystem = solarsystem.SolarSystem(x=0, y=0, seed=0)
		
		components.init()
	
		pyglet.clock.schedule_interval(self.update, 1/60.0)
	def update(self, dt):
		if not self.paused:
			self.playerShip.update(dt)
			self.background.update(dt)
			self.currentSystem.update(dt)
				
		self.hud.update(dt)		
		#print self.mainBatch
	def on_draw(self):
		pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
		
		pyglet.gl.glLoadIdentity() #Set camera to middle
		pyglet.gl.glTranslatef(-self.camera[0], -self.camera[1], 0.5) #Set camera position
		
		self.background.draw()
		self.currentSystem.batch.draw()
		self.mainBatch.draw()
		self.playerShip.draw()
		
		pyglet.gl.glLoadIdentity()
		self.hudBatch.draw()
		
	def dispatch_event(self, event_type, *args):
		"""This function is Pyglet's; I'm overriding a piece of it"""
		if event_type=='on_draw':
			#PYGLET HACK: We want it to iterate through the on_draws backwards, and self.on_draw contains the glClear()
			self.on_draw()
			for frame in reversed(self._event_stack):
				handler = frame.get(event_type, None)
				if handler:
					try:
						if handler(*args): return True
					except TypeError:
						self._raise_dispatch_exception(event_type, args, handler)
			return True
		else:
			return super(GameWindow, self).dispatch_event(event_type, *args)
	def enterSystem(self, target):
		self.currentSystem = solarsystem.SolarSystem(x=0, y=0, seed=target)
		self.background.generate(seed=self.currentSystem.seed)
		
		self.playerShip.position = (750, 750)
		self.playerShip.vel = Vector(-440, -440)
		self.camera = Vector(100, 200)
		
		pyglet.clock.schedule_interval(self.playerShip.brake, 0.1)
		def stopBrake(dt): pyglet.clock.unschedule(self.playerShip.brake)
		pyglet.clock.schedule_once(stopBrake, 2.1)
			

argparser = OptionParser()
argparser.add_option("-f", "--fullscreen", action="store_true", dest="fullscreen", default=False, help="Load game at max resolution, in a nobordered window")

options, args = argparser.parse_args()
if options.fullscreen:
	screen = pyglet.window.get_platform().get_default_display().get_default_screen()
	gameWindow = GameWindow(screen.width, screen.height, style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
else:
	gameWindow = GameWindow(800, 600)
pyglet.clock.set_fps_limit(60)
	
if __name__ == '__main__':
	pyglet.app.run()
