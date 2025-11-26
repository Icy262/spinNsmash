from server.player_container import PlayerContainer
from common.network_connection import NetworkConnection
from common.network_messages import get_type, NetworkObjectTypes, PlayerMove, ClientUpdate, PlayerShoot
from common.game_entities import PlayerEntity, BulletEntity
import pygame
import random
import math

class Game(PlayerContainer):
	def __init__(self, num_bots, size_x, size_y):
		"""
		Initializes the game state.
		"""
		self.num_bots = num_bots #TODO: Unimplimented
		self.size_x = size_x #should be a mult of grid size to make the grids align cleanly with the map bounds
		self.size_y =size_y
		self.game_entities = [] #list of other game entities that are not players.
		super().__init__()

	def add_player(self, player):
		"""
		Overrides the default behaviour to initialize the player in game state
		"""
		#initialize the player with some location and state
		player.player_entity = PlayerEntity().from_data(0, random.randint(1, self.size_x), random.randint(1, self.size_y), 0, 0, 20) #init the player with a random position, zero velocity, and a size of 20
		self.connected_players.append(player) #add the player to the list of players		
	
	def run(self):
		"""
		Processes the main game loop of the game
		"""
		clock = pygame.time.Clock()
		while True: #repeat for the duration of the program
			players_to_remove = []
			for player in self.connected_players: #loop through the connected players and check for any new messages.
				for i in range(3): #process up to three messages per game tick per player. prevents buildup, while also preventing dos
					message = player.network_connection.get_next_message() #get the next message from this player, if there is any, if not it'll be None
					player_updated = False
					if(message != None): #if there is some new message,
						#considered using match case, but python sucks and doesn't support .value					
						if get_type(message) == NetworkObjectTypes["player_move"].value: #if a player_move,
							if player.player_entity_updated:
								player_updated = True
								player.player_entity_updated = False
							else:
								#TODO: verify the values from this message
								movement = PlayerMove().from_bytes(message)
								player.player_entity.dx = movement.dx
								player.player_entity.dy = movement.dy
								player.player_entity.vx = movement.vx
								player.player_entity.vy = movement.vy
								player_updated = False #temp code until movement validation is implemented
						elif get_type(message) == NetworkObjectTypes["player_shoot"].value: #if a player_shoot,
							#TODO: implement shooting rate limit
							#15 pixels per tick, so vT = 15
							#10 px wide, so half the size of a player
							message = PlayerShoot().from_bytes(message)
							self.game_entities.append(BulletEntity().from_data(1, player.player_entity.dx, player.player_entity.dy, math.sin(message.direction)*15, math.cos(message.direction)*15, 10))
						else: #unrecognized status code
							print("ERROR: STATUS CODE NOT RECOGNIZED", get_type(message)) #TODO: replace with actual error handling
					#send the player an updated game status with the player's player object first
					try: #if the player disconnects, causing the send to fail, it could crash the game
						player.network_connection.send(ClientUpdate().from_data([player.player_entity] + [player_i.player_entity for player_i in self.connected_players if player_i is not player] + self.game_entities, player_updated).to_bytes())
					except Exception as error:
						print(error)
						print("Player", player, "disconnected")
						players_to_remove.append(player)
						break
			for player in players_to_remove:
				self.connected_players.remove(player)

			#tick the bullets
			game_entities_to_remove = [] #for any bullets that cross the map edge
			for bullet in self.game_entities:
				bullet.dx += bullet.vx
				bullet.dy += bullet.vy

				#if bullet crosses map edge, remove to save memory
				if bullet.dx < 0 or bullet.dx > self.size_x: game_entities_to_remove.append(bullet)
				if bullet.dy < 0 or bullet.dy > self.size_y: game_entities_to_remove.append(bullet)
			for game_entity in game_entities_to_remove:
				if game_entity in self.game_entities:
					self.game_entities.remove(game_entity)

			clock.tick(60) #limit to 60 ticks per second. TODO: reduce to 20 on client and server while maintaining 60 fps on client