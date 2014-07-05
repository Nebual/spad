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

def textureBorderFix(tex): 
	""" Takes a pyglet texture/region and insets the texture coordinates by half a texel 
	allowing for sub-pixel blitting without interpolation with nearby regions within same texture atlas.
	This fixes the transparent edges of some sprites showing weird lines.""" 
	coord_width = tex.tex_coords[3] - tex.tex_coords[0] 
	coord_height = tex.tex_coords[4] - tex.tex_coords[1] 
	x_adjust = (coord_width / tex.width) / 2.0		# get tex coord half texel width 
	y_adjust = (coord_height / tex.height) / 2.0	# get tex coord half texel width 
	# create new 12-tuple texture coordinate 
	tex.tex_coords = (tex.tex_coords[0]+x_adjust, 	tex.tex_coords[1]+y_adjust, 	0, 								tex.tex_coords[3]-x_adjust,
					tex.tex_coords[4]+y_adjust, 	0, 								tex.tex_coords[6]- x_adjust, 	tex.tex_coords[7]-y_adjust, 
					0, 								tex.tex_coords[9]+x_adjust, 	tex.tex_coords[10]-y_adjust, 	0) 

def loadSound(filename):
	try: return pyglet.resource.media("sounds/"+filename, streaming=False)
	except pyglet.media.riff.WAVEFormatException:
		print "ERROR: AVbin must be installed to handle ogg/mp3!"
		print "https://github.com/downloads/AVbin/AVbin/avbin-win32-5.zip"
		return pyglet.resource.media("sounds/null.wav", streaming=False)
warpSound = loadSound("warp_start.ogg")
