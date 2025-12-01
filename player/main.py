import socket
import threading
import pygame
from common.player_brief import PlayerBrief
from common.network_messages import NetworkObjectTypes, GetGames, JoinGame, PlayerMove, ClientUpdate, get_type, PlayerShoot
from common.network_connection import NetworkConnection
from common.game_entities import GameEntity, PlayerEntity, BulletEntity
import math



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
	#draw a border of black lines
	pygame.draw.line(background, (0, 0, 0), (0,0), (width, 0), 5)
	pygame.draw.line(background, (0, 0, 0), (0,0), (0, height), 5)
	pygame.draw.line(background, (0, 0, 0), (width,0), (width, height), 5)
	pygame.draw.line(background, (0, 0, 0), (0,height), (width, height), 5)

def clamp(val, min, max):
	"""
	Given a numeric value, and minimum and maximum values, will restrict the value to within the range of min to max and return. Min should be less than max or nothing will happen
	"""
	if val < min: val = min
	elif val > max: val = max
	return val

def render_entity(entity):
	#attempting to draw an entity that is offscreen will not cause issues, so we don't need to check if they are onscreen
	corner_of_screen_x = player.dx - screen.get_size()[0]/2 #the coordinate value on the map of the point at the corner of the screen
	corner_of_screen_y = player.dy - screen.get_size()[1]/2 #same
	#clamp the viewable area of the screen to the boundaries of the map by restricting the corner of the screen to between the top left corner of the map and one screen width/height from the other corners respectively
	corner_of_screen_x = clamp(corner_of_screen_x, 0, bounds_x - screen.get_size()[0])
	corner_of_screen_y = clamp(corner_of_screen_y, 0, bounds_y - screen.get_size()[1])
	pygame.draw.circle(screen, entity.colour, (entity.dx - corner_of_screen_x, entity.dy - corner_of_screen_y), entity.size, 0) #draw a solid green circle on the screen with a radius of 20 centered on the entity's location relative to the player

pygame.init()

display_flags = pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE #flags to use when seting the display mode
pygame.display.set_caption("Network Game Prototype")
display_info = pygame.display.Info()
screen = pygame.display.set_mode((display_info.current_w, display_info.current_h), display_flags) #create a monitor surface the size of the display, using the display flags
clock = pygame.time.Clock()

while pygame.QUIT not in pygame.event.get():
	#main menu
	title_text = pygame.font.SysFont("Arial", 120).render("Network Game Prototype", True, (255, 255, 0))
	start_prompt = pygame.font.SysFont("Arial", 72).render("press ENTER to start", True, (0, 255, 0))
	screen.fill((0,0,0))
	screen.blit(title_text, (display_info.current_w//2 - title_text.get_width()//2, display_info.current_h//3 - title_text.get_height()//2))
	screen.blit(start_prompt, (display_info.current_w//2 - title_text.get_width()//2, display_info.current_h//2 - title_text.get_height()//2))
	
	start = False
	while not start:
		pygame.display.flip()
		clock.tick(60) #Limit the game to 60 fps, also limit physics logic
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
			elif event.type == pygame.VIDEORESIZE:
				new_dimensions = event.size #a VIDEORESIZE event has a size attribute which contains the current dimensions of the window
				screen = pygame.display.set_mode(new_dimensions, display_flags) #recreate the monitor surface with the new window dimensions and preserving the flags
				gen_background() #regen a new background for the new screen size
		start = pygame.key.get_pressed()[pygame.K_RETURN]
	
	#join game menu

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.connect(("127.0.0.1", 4004))
	server = NetworkConnection(server)
	game_message = GetGames()
	game_message.from_data()
	server.send(game_message.to_bytes())
	threading.Thread(target = server.recieve).start()

	recieved_list = False
	while not recieved_list:
		list = server.get_next_message()
		if list != None:
			recieved_list = True
	
	#TEMP CODE, REMOVE LATER
	server.send(JoinGame().from_data(0).to_bytes()) #TODO: add game selecter menu
	bounds_x = 3000
	bounds_y = 3000

	#game

	#TODO: remove, test code
	player_max_speed = 150

	grid_spacing = 50 #height and width of each grid square
	gen_background()
	player = PlayerEntity().from_data(0,0,0,0,0,0) #create a player and init to garbage variables until we recieve proper data from the server
	
	game_objects = [] #holds all the entities existing on the game map

	quit = False
	while not quit:
		while True: #Python is an abomination. I just want a do-while.
			message = server.get_next_message()
			if message == None:
				break
			elif get_type(message) == NetworkObjectTypes["client_update"].value:
				game_objects = ClientUpdate().from_bytes(message).game_objects
				if ClientUpdate().from_bytes(message).updated: player = game_objects.pop(0) #the first element is our player, so remove it from the list and put it in the player value
				else: game_objects.pop(0)
			else: #unrecognized status code
				print("ERROR: STATUS CODE NOT RECOGNIZED", get_type(message)) #TODO: replace with actual error handling

		#TODO: Let the grids align with the map bounds
		background_x_orgin = clamp(player.dx, screen.get_size()[0]/2, bounds_x - screen.get_size()[0]/2)%grid_spacing
		background_y_orgin = clamp(player.dy, screen.get_size()[1]/2, bounds_y - screen.get_size()[1]/2)%grid_spacing
		screen.blit(background, (0, 0), pygame.Rect(background_x_orgin, background_y_orgin, screen.get_size()[0], screen.get_size()[1]))

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit = True
			elif event.type == pygame.VIDEORESIZE:
				new_dimensions = event.size #a VIDEORESIZE event has a size attribute which contains the current dimensions of the window
				screen = pygame.display.set_mode(new_dimensions, display_flags) #recreate the monitor surface with the new window dimensions and preserving the flags
				gen_background() #regen a new background for the new screen size
		
		keystate = pygame.key.get_pressed() #get the currently held keys
		if keystate[pygame.K_w]: #if the key is pressed, accelerate the player in that direction. must all be if, not elif because if not it only accepts one input at a time, preventing sustainable diagonal movement
			player.vy -= 0.3
		if keystate[pygame.K_a]:
			player.vx -= 0.3
		if keystate[pygame.K_s]:
			player.vy += 0.3
		if keystate[pygame.K_d]:
			player.vx += 0.3
		if pygame.mouse.get_pressed()[0]: #if left click held down, shoot
			server.send(PlayerShoot().from_data(math.atan2(pygame.mouse.get_pos()[0] - player.dx + clamp(player.dx - screen.get_size()[0]/2, 0, bounds_x - screen.get_size()[0]/2), pygame.mouse.get_pos()[1] - player.dy + clamp(player.dy - screen.get_size()[1]/2, 0, bounds_y - screen.get_size()[1]))).to_bytes()) #calc angle of line from player to mouse. clockwise from up. then send.

		#tick the player
		player.vx -= player.vx*0.05 #slowly slow down the player and limit top speed
		player.vy -= player.vy*0.05 #same

		player.dx += player.vx #move the player by velocity units every tick
		player.dy += player.vy

		player.dx = clamp(player.dx, 0, bounds_x)
		player.dy = clamp(player.dy, 0, bounds_y)

		#tick the other stuff
		game_entities_to_remove = [] #for any entity that cross the map edge
		for entity in game_objects:
			entity.dx += entity.vx
			entity.dy += entity.vy

			#if entity crosses map edge, remove to save memory
			if entity.dx < 0 or entity.dx > bounds_x: game_entities_to_remove.append(entity)
			if entity.dy < 0 or entity.dy > bounds_y: game_entities_to_remove.append(entity)
		for game_entity in game_entities_to_remove:
			if game_entity in game_objects:
				game_objects.remove(game_entity)

		for entity in game_objects: #render the other entities
			render_entity(entity)
		render_entity(player) #render the player

		pygame.display.flip() #update the screen

		server.send(PlayerMove().from_data(player.dx, player.dy, player.vx, player.vy).to_bytes())

		clock.tick(60) #Limit the game to 60 fps, also limit physics logic

pygame.quit()