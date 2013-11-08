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
