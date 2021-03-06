import pygame
import math
import random
from pygame.locals import *
from pygame import gfxdraw

#setup

background_colour = (0,0,0)
(width, height) = (1000, 600)

screen = pygame.display.set_mode((width, height))#,pygame.FULLSCREEN)
screen.fill(background_colour)
pygame.display.set_caption('Patch Map')
pygame.font.init()

myfont = pygame.font.SysFont("monospace", 20, bold = True)
bg = pygame.image.load("bg.png")

clock = pygame.time.Clock()

def draw_aa_circle(colour, pos, radius):
	pygame.gfxdraw.filled_circle(screen, pos[0], pos[1], radius, colour)
	pygame.gfxdraw.aacircle(screen, pos[0], pos[1], radius, colour)

def distance(a,b):
	return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def interpolate(maxi, mini, value):
	return ((value-mini)/(maxi - mini))

def get_depth(pos, ocean_depth, percentage_of_land):
	percentage_of_water = 1 - percentage_of_land
	my_percentage = pos[1]/height
	if pos[1] < percentage_of_land*height:
		return int(-(height*percentage_of_land-pos[1])*15/(height*percentage_of_land))
	elif my_percentage < (percentage_of_land + 0.40*percentage_of_water):
		return int(200*interpolate(percentage_of_land + 0.40*percentage_of_water, percentage_of_land, my_percentage))
	elif my_percentage < (percentage_of_land + 0.60*percentage_of_water):
		return int(200 + 500*interpolate(percentage_of_land + 0.60*percentage_of_water, 
			percentage_of_land + 0.40*percentage_of_water, my_percentage))
	else:
		return int(700 + (ocean_depth - 700)*interpolate(1, 
			percentage_of_land + 0.60*percentage_of_water, my_percentage))



#given a screen position and a total depth of the ocean return the type of patch
def get_type(pos, ocean_depth, percentage_of_land):
	patch_depth = get_depth(pos, ocean_depth, percentage_of_land)

	if patch_depth < 0:
		return [random.choice(["Tidepool", "Estuary"]), patch_depth]	
	#epipelagic zone
	if patch_depth < 200:
		return [random.choice(["Ocean Surface", "Coastal Shelf"]), patch_depth]
	#mesopelagic zone
	if patch_depth < 700:
		return [random.choice(["Mid Ocean", "Mid Ocean", "Mid Ocean", "Cave"]), patch_depth]
	#bathypelagic zone
	if patch_depth > 700 and patch_depth < 0.8*ocean_depth:
		return [random.choice(["Deep Ocean", "Deep Ocean", "Deep Ocean", "Cave"]), patch_depth]
	#ocean floor
	return [random.choice(["Ocean Floor", "Ocean Floor", "Hydrothermal"]), patch_depth]

patch_names = ["Hydrothermal", "Ocean Floor", "Deep Ocean", "Mid Ocean", "Ocean Surface", "Coastal Shelf", "Tidepool", "Cave", "Ice Shelf", "Estuary"]

patches = []
min_seperation = 75 #pixels between patches
max_number_of_caves = 4 #what is the max number of caves allowed?
percentage_of_land = 0#how much of the map is land? between 0 and 0.25, it's randomly chosen later
#note: photosynthesis is linear up to 100w/m^2 and then stops increasing. 

class patch:
	def __init__(self, pos, patch_type, patch_depth, ocean_depth, solar_strike, frozen_percetage):
		#screen position
		self.pos = pos
		#work out depth of the patch
		self.depth = patch_depth
		#how much sunlight hits the patch?
		self.sunlight = 0		
		#how much sun strikes the surface of the planet
		self.solar_strike = solar_strike
		#what type of patch are you? from patch_names
		self.patch_type = patch_type
		#is this patch frozen over?
		self.frozen = False 
		#are you the patch where the player first starts?
		self.starter_patch = False
		#what other patches are you connected to?
		self.neighbours = []
		self.set_colour()
		self.set_light_level(frozen_percetage)

	def set_light_level(self, frozen_percetage):
		#work out how much light hits the patch
		self.sunlight = min(self.solar_strike, math.exp(-0.023*self.depth)*self.solar_strike)
		if self.patch_type == "Cave":
			self.sunlight = 0
		if self.pos[0] < frozen_percetage*width and self.depth > 0:
			self.sunlight = math.exp(-0.046*self.depth)*self.solar_strike


	def check_frozen(self, frozen_percetage):
		if self.pos[0] < frozen_percetage*width and self.depth < 100:
				self.frozen = True
		else:
			self.frozen = False
		self.set_colour()
		self.set_light_level(frozen_percetage)

	def get_neighbours(self):
		for p in patches:
			#if you are horizontally close enough
			if abs(self.pos[0] - p.pos[0]) < 100 and p is not self:
				#if you are less than 700 and so are they
				if self.depth < 100 and p.depth < 100:
					self.neighbours.append(p)
				#if you are more than 0 and so are they
				elif self.depth > 0 and p.depth > 0 and self.depth < 700 and p.depth < 700:
					self.neighbours.append(p)
				elif self.depth > 200 and p.depth > 200:
					self.neighbours.append(p)

	def set_colour(self):
		if self.patch_type == "Hydrothermal":
			self.colour = [255,0,0]
		if self.patch_type == "Ocean Floor":
			self.colour = [109,56,107]
		if self.patch_type == "Deep Ocean":
			self.colour = [0,10,75]
		if self.patch_type == "Mid Ocean":
			self.colour = [0,50,150]
		if self.patch_type == "Ocean Surface":
			self.colour = [100,150,200]
		if self.patch_type == "Coastal Shelf":
			self.colour = [0,255,255]
		if self.patch_type == "Tidepool":
			self.colour = [50,200,50]
		if self.patch_type == "Cave":
			self.colour = [50,50,50]
		if self.patch_type == "Ice Shelf":
			self.colour = [255,255,255]		
		if self.patch_type == "Estuary":
			self.colour = [255,255,0]
		if self.frozen == True:
			self.colour = [255,255,255]

	def draw(self):
		if self.starter_patch:
			draw_aa_circle([0,100,0], self.pos, 12)
		draw_aa_circle([200,200,200], self.pos, 9)
		draw_aa_circle(self.colour, self.pos, 8)


def reset():
	#total ocean depth
	global ocean_depth
	ocean_depth = random.randint(1000,5000)
	#percentage of land, from 0 to 0.25
	global percentage_of_land
	percentage_of_land = random.uniform(0,0.25)
	global patches
	patches = []
	#make a list of patches which must be included
	needed_patches = patch_names[:]
	needed_patches.remove("Ice Shelf")
	if percentage_of_land < 0.1:
		needed_patches.remove("Estuary")
		needed_patches.remove("Tidepool")
		needed_patches.remove("Mid Ocean")
		needed_patches.remove("Deep Ocean")
	#build patch list
	#while there is room for another patch
	cave_counter = 0
	#amount of solar radiation strking the planet
	solar_strike = random.randint(300,3000) #watts per m^2
	while 1:
		made_patch = False
		patch_type = False
		counter = 0
		
		#try to add a patch
		while 1:
			#choose random position
			pos = [random.randint(10,width-10), random.randint(10,height-10)]
			#find out what kind of patch the new one is
			[patch_type, patch_depth] = get_type(pos, ocean_depth, percentage_of_land)
			#check if you need that patch to have one of each
			need_patch = True
			if (len(needed_patches) > 0 and patch_type not in needed_patches) or (patch_type == "Cave" and cave_counter >= max_number_of_caves):
				need_patch = False
			#check if the position is too close to another
			too_close = False
			for p in patches:
				if distance(p.pos,pos) < min_seperation:
					too_close = True
			#if the patch is not too close to another and is needed then make it 
			if too_close == False and need_patch == True:
				made_patch = True
				break
			#fail after 1000 attempts
			counter += 1
			if counter == 1000:
				break
		#if you failed to add a new patch you are done
		if made_patch == False:
			break
		patches.append(patch(pos, patch_type, patch_depth, ocean_depth, solar_strike, frozen_percetage))
		if patch_type in needed_patches:
			needed_patches.remove(patch_type)
		if patch_type == "Cave":
			cave_counter += 1

	#work out where the starter patch is
	best_dist = 10*width
	best_patch = patches[0]
	for p in patches:
		dist = abs(width/2 - p.pos[0])
		if p.patch_type == "Hydrothermal" and dist < best_dist:
			best_dist = dist
			best_patch = p
	best_patch.starter_patch = True

	#get each patch to work out what it's neighbours are
	for p in patches:
		p.get_neighbours()
	print("Done")

#how much of the planet surface is frozen
frozen_percetage = 0.1
reset()


running = True
while running:
	for event in pygame.event.get():
	    if event.type == pygame.QUIT:
	        running = False
	    elif event.type == KEYDOWN:
	        if event.key == K_ESCAPE:
	            running = False
	        elif event.key == K_SPACE:
	        	reset()
	        elif event.key == K_RIGHT:
	        	frozen_percetage = min(1,frozen_percetage + 0.1)
	        	for p in patches:
	        		p.check_frozen(frozen_percetage)
	        elif event.key == K_LEFT:
	        	frozen_percetage = max(0, frozen_percetage - 0.1)
	        	for p in patches:
	        		p.check_frozen(frozen_percetage)
	       

	screen.fill(background_colour)
	screen.blit(bg, [0,percentage_of_land*height])

	#draw ocean levels
	pygame.draw.line(screen, [5,14,26], [0, percentage_of_land*height], [width, percentage_of_land*height], 1)
	textsurface = myfont.render("0m", True, [255,255,255]) 
	screen.blit(textsurface,(10, percentage_of_land*height))

	percentage_of_water = 1 - percentage_of_land
	height_location = (percentage_of_land + 0.40*percentage_of_water)*height
	pygame.draw.line(screen, [5,14,26], [0, height_location], [width, height_location], 1)
	textsurface = myfont.render("200m", True, [255,255,255]) 
	screen.blit(textsurface,(10, height_location))

	height_location = (percentage_of_land + 0.60*percentage_of_water)*height
	pygame.draw.line(screen, [5,14,26], [0, height_location], [width, height_location], 1)
	textsurface = myfont.render("700m", True, [255,255,255]) 
	screen.blit(textsurface,(10, height_location))

	textsurface = myfont.render(str(ocean_depth) + "m", True, [255,255,255]) 
	screen.blit(textsurface,(10, height - 20))

	#display info for hovered patch and show neighbours
	pos = pygame.mouse.get_pos()
	for p in patches:
		if distance(p.pos, pos) < 50:
			textsurface = myfont.render("Patch Type : " + str(p.patch_type) + 
				"  Depth : " + str(p.depth) + "m" +
				"  Sunlight : " + str(round(p.sunlight,2)) + "w/m^2", True, [255,255,255])
			screen.blit(textsurface,(10, 10))

			for n in p.neighbours:
				pygame.draw.line(screen, [150,150,150], p.pos, n.pos, 1)

		
		
	#draw patches
	for p in patches:		
		p.draw()

	


	pygame.display.flip()
	
	

pygame.quit()