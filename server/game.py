from server.player_container import PlayerContainer

class Game(PlayerContainer):
	def __init__(self, name, num_bots, size_x, size_y):
		"""
		Initializes the game state.
		"""
		#TODO: Implement
		self.name = name

	def add_player(self, player):
		"""
		Overrides the default behaviour to initialize the player in game state
		"""
		self.connected_players.append(player) #add the player to the list of players
		#initialize the player with some location and state

class GameDescriptor:
	def from_data(self, game):
		"""
		Creates a GameDescriptor of a Game.
		"""
		self.name = game.name
		self.player_count = len(game.players) #player count is equal to the number of players in the player list

	def from_bytes(self, as_bytes):
		"""
		Creates a GameDescriptor from its bytes representation
		"""
		self.name = as_bytes[:-1].decode('UTF-8') #interprets everything up to the second last byte as the name and decodes it as UTF-8 text
		self.player_count = as_bytes[-1].from_bytes() #last byte is the number of players

	def to_bytes(self):
		"""
		Converts a GameDescriptor to its bytes representation for passing over the network
		"""
		as_bytes = bytearray() #to hold the bytes representation
		as_bytes.extend(name.encode('UTF-8')) #encode the name as UTF-8, and append
		as_bytes.extend(player_count.as_bytes(1)) #Convert the number of players to a 1 byte int and append
		return as_bytes #return the bytes representation