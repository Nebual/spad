import sys
import pyglet
import resources

group0 = pyglet.graphics.OrderedGroup(0)
group1 = pyglet.graphics.OrderedGroup(1)
group2 = pyglet.graphics.OrderedGroup(2)

monoFont = (sys.platform=="linux2" and "Monospace" or "Courier New")

class HUD(object): 
	selected = None
	def __init__(self, window, batch):
		self.window, self.batch = window, batch
		
		self.hudScale = 1.0
		
		self.hudX, self.hudY = hudX, hudY = window.width-100, window.height-200 - 100*self.hudScale
		self.minimap = pyglet.sprite.Sprite(img=resources.loadImage("minimap.png"), x=window.width-100*self.hudScale, y=hudY+200, batch=batch, group=group0)
		self.minimap.scale = self.hudScale
		self.minimapPlayer = pyglet.sprite.Sprite(img=resources.loadImage("circle_silver.png"), batch=batch, group=group1)
		
		self.sideBG = pyglet.sprite.Sprite(img=resources.loadImage("sidebar.png"), x=hudX, y=hudY, batch=batch, group=group0)
		self.modeLabel = pyglet.text.Label(text="Starmode: 0", font_size=10,x=hudX+50, y=hudY+180, anchor_x="center", batch=batch, group=group1)
		self.fpsLabel = pyglet.text.Label(text="FPS: 0", x=hudX+50, y=hudY+160, anchor_x="center", batch=batch, group=group1)
		self.coordLabel = pyglet.text.Label(text="0,0", font_size=10, x=hudX+50, y=hudY+140, anchor_x="center", batch=batch, group=group1)
		self.creditLabel = pyglet.text.Label(text="$10000", font_size=10, x=hudX+50, y=hudY+120, anchor_x="center", batch=batch, group=group1)
		self.cargoLabel = pyglet.text.Label(text="CSpace: 0", font_size=10, x=hudX+50, y=hudY+100, anchor_x="center", batch=batch, group=group1)
		
		self.selectionSprite = pyglet.sprite.Sprite(img=resources.loadImage("selectionbox.png", center=True), x=0, y=0, batch=self.window.mainBatch)
		self.selectionSprite.visible = False
	def update(self, dt):
		self.fpsLabel.text = "FPS: %.1f" % pyglet.clock.get_fps()
		self.minimapPlayer.x = self.window.width+int(max(3, min(94, 50 + self.window.playerShip.x / self.window.currentSystem.radius * 50))-100)*self.hudScale
		self.minimapPlayer.y = self.hudY+200+int(max(3, min(94, 50 + self.window.playerShip.y / self.window.currentSystem.radius * 50)))*self.hudScale
		
		self.coordLabel.text = "(%d, %d)" % (self.window.playerShip.x, self.window.playerShip.y)
		self.creditLabel.text = "$%d" % self.window.playerShip.credits
		self.cargoLabel.text = "CSpace: %d" % (self.window.playerShip.cargoMax - sum(cargo.quantity for cargo in self.window.playerShip.cargo.values()))
	def select(self, sprite):
		self.selected = sprite
		self.selectionSprite.x, self.selectionSprite.y = sprite.x, sprite.y
		self.selectionSprite.scale = (sprite.radius + 20) / 100.0
		self.selectionSprite.visible = True
		return sprite
	def deselect(self):
		self.selected = None
		self.selectionSprite.visible = False

largeWindow = resources.loadImage("largewindow.png", center=True)

class Frame(object):
	def __init__(self, title="Unnamed Frame", scale=1.0, start=True):
		self.window = pyglet.window.get_platform().get_default_display().get_windows()[0]
		self.batch = pyglet.graphics.Batch()
		self.buttons = []
		self.elements = []
		
		self.scale = self.window.uiScale * scale
		
		self.background = pyglet.sprite.Sprite(img=largeWindow, x=self.window.width/2, y=self.window.height/2, batch=self.batch, group=group0)
		self.background.scale = self.scale
		
		self.titleLabel = pyglet.text.Label(text=title, x=self.window.width/2, y=self.window.height/2 + 400*self.scale - 40, anchor_x="center", batch=self.batch, group=group1)
		
		if start: self.start()
		
	def addButton(self,x,y,text,callback, args=(), size="500"):
		sprite = pyglet.sprite.Sprite(img=resources.loadImage("button_"+str(size)+".png", center=True), x=self.window.width/2 + x*self.scale, y=self.window.height/2 + y*self.scale, batch=self.batch, group=group1)
		sprite.scale = self.scale
		sprite.label = pyglet.text.Label(text=text, x=sprite.x, y=sprite.y, anchor_x="center", anchor_y="center", batch=self.batch, group=group2)
		sprite.pressed = callback
		sprite.args = args
		self.buttons.append(sprite)
		return sprite
	def addLabel(self,x,y,text, anchor_x="center"):
		label = pyglet.text.Label(text=text, font_name=monoFont,x=self.window.width/2 + x*self.scale, y=self.window.height/2 + y*self.scale, anchor_x=anchor_x, anchor_y="center", batch=self.batch, group=group1)
		label.scale = self.scale
		self.elements.append(label)
		return label
		
	def on_mouse_press(self, x, y, button, modifiers):
		for but in self.buttons:
			if (but.x - but.width/2 < x < but.x + but.width/2) and (but.y - but.height/2 < y < but.y + but.height/2):
				but.pressed(*but.args)
				break
		return True
		
	def start(self):
		self.window.push_handlers(self)
		self.window.paused = True
		pyglet.clock.schedule_interval(self.update, 1/60.0)
	def stop(self):
		self.window.pop_handlers()
		self.window.paused = False
		pyglet.clock.unschedule(self.update)
	
	def on_key_press(self, symbol, modifiers):
		if symbol == pyglet.window.key.ESCAPE: self.stop()
		return pyglet.event.EVENT_HANDLED
	
	def on_draw(self):
		pyglet.gl.glLoadIdentity()
		self.batch.draw()
		
	def update(self, dt): pass


class PlanetFrame(Frame):
	def __init__(self, planet, *args, **kwargs):
		super(PlanetFrame, self).__init__(title="Welcome to "+planet.name, *args, **kwargs)
		self.planet = planet
		
		if planet.hasTrade: self.addButton(-300, 200, "Trade Center", self.openTrade)
		if planet.hasMissions: self.addButton(-300, 100, "Mission Bounty Board", self.openMissions)
		
		self.addButton(-300, -300, "Depart", self.stop)
	def openTrade(self):
		f = self.tradeFrame = Frame("Trade Center", scale=0.8)
		f.goods = {}
		def buy(kind):
			ply = self.window.playerShip
			currentCargo = sum(cargo.quantity for cargo in ply.cargo.values())
			price = self.planet.goods[kind]
			purchased = min(10, ply.cargoMax - currentCargo, ply.credits / price)
			
			if kind in ply.cargo:
				ply.cargo[kind].quantity += purchased
			else:
				ply.cargo[kind] = Cargo(kind, purchased)
			ply.credits -= price * purchased
			f.goods[kind+"total"].text = str(ply.cargo[kind].quantity)
		def sell(kind):
			ply = self.window.playerShip
			if kind not in ply.cargo: return
			
			purchased = min((ply.cargo[kind].quantity % 10) or 10, ply.cargo[kind].quantity)
			
			ply.cargo[kind].quantity -= purchased
			ply.credits += self.planet.goods[kind] * purchased
			if ply.cargo[kind].quantity == 0: del ply.cargo[kind]
			
			f.goods[kind+"total"].text = str(kind in ply.cargo and ply.cargo[kind].quantity or 0)
		i=0
		plyCargo = self.window.playerShip.cargo
		for kind, price in self.planet.goods.items():
			f.goods[kind] = f.addLabel(-500, 240 - i*80, kind.capitalize()+": "+("$"+str(price)).rjust(14-len(kind)), anchor_x="left")
			f.goods[kind+"total"] = f.addLabel(0, 240 - i*80, str(kind in plyCargo and plyCargo[kind].quantity or 0), anchor_x="left")
			f.goods[kind+"sell"] = f.addButton(275, 240 - i*80, "Sell", sell, (kind,), size="125")
			f.goods[kind+"buy"] = f.addButton(425, 240 - i*80, "Buy", buy, (kind,), size="125")
			i+=1
	def openMissions(self):
		self.missionFrame = Frame("Mission Bounty Board", scale=0.8)


class Cargo(object):
	def __init__(self, kind, quantity=1):
		self.kind = kind
		self.quantity = quantity