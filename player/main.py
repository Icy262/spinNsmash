import socket
import threading
import pygame
from common.player_brief import PlayerBrief
from common.network_requests import NetworkObjectTypes, GetGames
from common.client_connection import ClientConnection

def gen_background():
	global background #make the background global so that it can be accessed everywhere
	width, height = screen.get_size() #get the size of the screen
	width, height = width + grid_spacing, height + grid_spacing #add grid_spacing px for reasons explained below
	background = pygame.Surface((width, height)) #create a surface to use as a template background. create it grid_spacingpx larger than it needs to be, so we can shift it around slighty to give the appearance of a static grid that the player moves relative to, instead of the grid moving with the player
	background.fill((237,232,208)) #set the background to beige
	#draw horizontal and vertical black lines grid_spacing px apart
	for x in range(0, width//grid_spacing + 1): #we need lines grid_spacing px apart, so divide the window width by grid_spacing and round down to the nearest whole number. we need to add 1 because line 0 is actually on the border and not visible. the code below could be written to put the first line on screen, but it's unecessary, and easier to just add an extra line
		pygame.draw.line(background, (0, 0, 0), (x*grid_spacing, 0), (x*grid_spacing, height + grid_spacing)) #draw the line on background, (0, 0, 0) is the colour code for black, start the line at grid_spacing pixels times the line number, and the top of the surface, end the line at the same horizontal, but bottom of the surface
	for y in range(0, height//grid_spacing + 1): #same as above
		pygame.draw.line(background, (0, 0, 0), (0, y*grid_spacing), (width + grid_spacing, y*grid_spacing)) #same as vertical lines, but swapped

def render_player(entity):
	#TODO: check if player onscreen
	pygame.draw.circle(screen, (0, 255, 0), (entity.dx, entity.dy), 20, 0) #draw a green circle on the screen centered on the entity's location with a radius of 20 that is solid

pygame.init()

#TEST CODE, REMOVE LATER
player = PlayerBrief()
player.from_data(0, 0, 100, 100)

player_max_speed = 150

bounds_x = 3000
bounds_y = 3000

display_info = pygame.display.Info()

display_flags = pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE #flags to use when seting the display mode
pygame.display.set_caption("spinNsmash")
screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), display_flags) #create a monitor surface the size of the display, using the display flags

grid_spacing = 50 #height and width of each grid square
gen_background()

clock = pygame.time.Clock()
framerate = 60

quit = False
while not quit:
	screen.blit(background, (0, 0), pygame.Rect(player.dx%grid_spacing, player.dy%grid_spacing, screen.get_size()[0], screen.get_size()[1])) #copy the background onto the screen, starting in the top left. Mod the player's position by grid_spacing to find where the player is relative to the corner of a grid square, and copy the background starting from that point onto the screen. copy a region of the background equivalent to the dimensions of the screen.

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			quit = True
		elif event.type == pygame.VIDEORESIZE:
			new_dimensions = event.size #a VIDEORESIZE event has a size attribute which contains the current dimensions of the window
			screen = pygame.display.set_mode(new_dimensions, display_flags) #recreate the monitor surface with the new window dimensions and preserving the flags
			gen_background() #regen a new background for the new screen size
	
	keystate = pygame.key.get_pressed() #get the currently held keys
	if keystate[pygame.K_w]: #if the key is pressed, accelerate the player in that direction
		player.vy -= 0.3
	elif keystate[pygame.K_a]:
		player.vx -= 0.3
	elif keystate[pygame.K_s]:
		player.vy += 0.3
	elif keystate[pygame.K_d]:
		player.vx += 0.3

	player.vx -= player.vx*0.05 #slowly slow down the player and limit top speed
	player.vy -= player.vy*0.05 #same

	player.dx += player.vx #move the player by velocity units every tick
	player.dy += player.vy

	render_player(player) #render the player
	pygame.display.flip() #update the screen

	clock.tick(60) #Limit the game to 60 fps, also limit physics logic

pygame.quit()