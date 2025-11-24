class GameDescriptor:
	def from_data(self, game):
		"""
		Creates a GameDescriptor of a Game.
		"""
		self.player_count = len(game.connected_players) #player count is equal to the number of players in the player list
		self.size_x = game.size_x
		self.size_y = game.size_y
		return self

	def from_bytes(self, as_bytes):
		"""
		Creates a GameDescriptor from its bytes representation
		"""
		self.player_count = as_bytes[0].from_bytes() #first byte is the number of players
		self.size_x = as_bytes[1:3].from_bytes() #next two are the x dimensions
		self.size_y = as_bytes[3:5].from_bytes() #next two after that are the y dimensions
		return self

	def to_bytes(self):
		"""
		Converts a GameDescriptor to its bytes representation for passing over the network
		"""
		as_bytes = bytearray() #to hold the bytes representation
		as_bytes.extend(self.player_count.to_bytes(1)) #Convert the number of players to a 1 byte int and append
		as_bytes.extend(self.player_count.to_bytes(2)) #Convert the game dimensions to a 2 byte int and append
		as_bytes.extend(self.player_count.to_bytes(2))
		return as_bytes #return the bytes representation