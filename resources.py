import pyglet
pyglet.resource.path = ['./resources']
pyglet.resource.reindex()

def centerImage(image):
	"""Sets an image's anchor point to its center"""
	image.anchor_x = image.width/2
	image.anchor_y = image.height/2

imageCache = dict()

def loadImage(filename, center=False):
	if filename in imageCache:
		image = imageCache[filename]
	else:
		image = pyglet.resource.image(filename)
		imageCache[filename] = image
		if center == True:
			centerImage(image)
	return image

def copyImage(base):
	ret = pyglet.image.Texture.create(base.width, base.height)
	ret.blit_into(base.image_data, 0, 0, 0)
	return ret

def loadSound(filename):
	try: return pyglet.resource.media("sounds/"+filename, streaming=False)
	except pyglet.media.riff.WAVEFormatException:
		print "ERROR: AVbin must be installed to handle ogg/mp3!"
		print "https://github.com/downloads/AVbin/AVbin/avbin-win32-5.zip"
		return pyglet.resource.media("sounds/null.wav", streaming=False)
warpSound = loadSound("warp_start.ogg")
