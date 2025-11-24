import enum
import abc
from common.game_descriptor import GameDescriptor

class NetworkObjectTypes(enum.Enum): #register of network object types
	get_games = 0
	game_list = 1
	join_game = 2
	player_move = 3
	client_update = 4

def get_type(as_binary):
	"""
	Takes a binary representation of some NetworkObject and returns the object_type value
	"""
	return int.from_bytes(as_binary[2:3])

class NetworkObject(abc.ABC): #should not be instantiated on it's own, just a template
	size = None #total size of the data, useful for parsing the byte stream later
	object_type = None #type of request, eg. requesting a list of games, a player movement, a server informing the client about game events, int
	data = None #any additional data required as part of the object. This isn't used as part of the NetworkObject class, but is a template.

	def _set_size(self):
		"""
		Automatically sets the size value based on the other data in the object. should only be called by methods in classes that inherit from NetworkObject
		"""
		self.size = 3 + len(self.data) #size is 2, object_type is 1, data is len(data). Adding the sizes together produces the total size

	def from_data(self, object_type, data):
		"""
		Initializes the object by assigning the passed data to the appropriate variables. data is a byte array.
		"""
		self.object_type = object_type
		self.data = data
		self._set_size()
		return self

	def from_bytes(self, as_bytes):
		"""
		Initializes a NetworkObject using the bytes representation
		"""
		self.size = int.from_bytes(as_bytes[:2]) #takes the first two bytes of as_bytes (the block allocated for the size int), converts it to and int, and stores it.
		self.object_type = int.from_bytes(as_bytes[2:3]) #takes the third byte of as_bytes (the byte that stores the object_type), converts it, and stores it
		self.data = as_bytes[3:] #the rest of the object is data, write the data to data
		return self

	def to_bytes(self):
		"""
		Converts NetworkObject to a bytearray representation to be decoded by to_object
		"""
		as_bytes = bytearray() #this will hold the bytearray representation of the NetworkObject
		#while the size of the network object appears first in the final bytearray, it is easier to calculate the total size and add it at the end, than to do it at the beginning
		as_bytes.extend(bytearray(2)) #create a blank byte array of 2 bytes to serve as a placeholder for the object size value. 2 bytes is a good option beause being limited to 255 byte messages is too small, and 65k messages is more than enough
		as_bytes.extend(self.object_type.to_bytes(1, 'big')) #convert the object type value to a byte and add it to the array. 256 options for network objects is more than enough
		as_bytes.extend(self.data) #data is a byte array of some size, which should be added to the data we send
		as_bytes[:2] = self.size.to_bytes(2, 'big') #convert the size value into a bytearray representation of size 2 and write it to the first two bytes of as_bytes, which we previously write empty data to as a placeholder.
		return as_bytes

class GetGames(NetworkObject):
	"""
	Used by the player client to request a list of running games on the server
	"""
	def from_data(self):
		"""
		Initializes a GetGames network request. A games request doesn't require any additional data, so there are no arguments
		"""
		super().from_data(NetworkObjectTypes['get_games'].value, bytearray()) #calls the super init method. Passes the code for GetGames and a null byte array because no arguments are required for the request
		return self

	def from_bytes(self, as_bytes):
		"""
		Initializes a GetGames using the bytes representation
		"""
		super().from_bytes(as_bytes) #call the super to fill the size and type fields, and put the bytes representation of data into the data field
		#there is no bytes data for this network object, so do nothing
		return self

class GameList(NetworkObject):
	"""
	The server's response to a GetGames request. Contains a list of all the running games on the server, and some information about each game
	"""
	def from_data(self, games):
		"""
		Initializes a GameList network request. Pulls from the list of running games to do this.
		"""
		running_games_descriptor = [] #to hold a list of GameDescriptors that describe each of the games in the game list
		for game in games: #for each game in the game list,
			running_games_descriptor.append(GameDescriptor().from_data(game)) #generates a GameDescriptor for each game and adds it to the list of GameDescriptors
		
		running_games_descriptor_as_bytes = bytearray() #to hold a byte representation of the game descriptor list
		
		for descriptor in running_games_descriptor: #for each game descriptor,
			descriptor_as_bytes = bytearray()
			game_descriptor_as_byte = descriptor.to_bytes() #convert to bytes
			len_as_bytes = len(game_descriptor_as_byte).to_bytes(2, 'big') #append the size of the game descriptor to the beginning of its data to allow for decoding.
			descriptor_as_bytes.extend(len_as_bytes) #append the length of the game descriptor as bytes
			descriptor_as_bytes.extend(game_descriptor_as_byte) #append the game descriptor as bytes
			running_games_descriptor_as_bytes.extend(descriptor_as_bytes) #append to the byte array
		super().from_data(NetworkObjectTypes['game_list'].value, running_games_descriptor_as_bytes) #pass the game id and list of running games to the super init
		return self

	def from_bytes(self, as_bytes):
		"""
		Initializes a GameList network request from the bytes representation. Primarily for use in decoding messages
		"""
		super().from_bytes(as_bytes) #call the super to fill size and type fields, and to put the bytes data in the data field
		self.running_games_descriptor = [] #will hold the final output of GameDescriptors
		
		position = 0

		while position < len(self.data): #while we still have more data to process,
			GameList_len = self.data[position] #get the length of the next GameList object
			GameList_data = self.data[position + 1: position + 1 + GameList_len] # slice from start of data to end of data. Add 1 to position because position is where the length is, so the next byte is the start of the GameList data
			GameList_reconstructed = GameList.GameList().from_bytes(GameList_data) #convert the bytes representation to a GameList
			self.running_games_descriptor.append(GameList_reconstructed) #append the reconstructed object to the list
			position += GameList_len #we processed GameList_len bytes of data, so we should note this in our position
		return self

class JoinGame(NetworkObject):
	"""
	Used for a player to join a game on the server after recieving a GameList
	"""
	def from_data(self, game_id):
		"""
		Initializes a JoinGame network request. game_id should be the index of the game in the game list
		"""
		self.game_id = game_id
		super().from_data(NetworkObjectTypes['join_game'].value, game_id.to_bytes(1)) #calls the super init method. Passes the code for join game and a single byte representation of the game_id
		return self

	def from_bytes(self, as_bytes):
		"""
		Initializes a GetGames using the bytes representation
		"""
		super().from_bytes(as_bytes) #call the super to fill the size and type fields, and put the bytes representation of data into the data field
		self.game_id = int.from_bytes(self.data)
		return self

class PlayerMove(NetworkObject):
	"""
	Used for a player to report their recent movements to the server.
	"""
	def from_data(self, movement):
		"""
		Packages a tuple of player movements (dx, dy, vx, vy) into a PlayerMove network object.
		"""
		self.movement = movement
		as_bytes = bytearray()
		as_bytes.extend(int(movement[0]*1000).to_bytes(4, signed = True)) #mult by 1000 to keep 3 decimals
		as_bytes.extend(int(movement[1]*1000).to_bytes(4, signed = True))
		as_bytes.extend(int(movement[2]*1000).to_bytes(4, signed = True))
		as_bytes.extend(int(movement[3]*1000).to_bytes(4, signed = True))
		super().from_data(NetworkObjectTypes['player_move'].value, as_bytes)
		return self

	def from_bytes(self, as_bytes):
		"""
		Takes a bytes representation of a PlayerMove and convert it to a PlayerMove object
		"""
		super().from_bytes(as_bytes) #call the super to fill size and type fields, and to put the bytes data in the data field
		self.movement = (int.from_bytes(self.data[0:4], signed = True)/1000, int.from_bytes(self.data[4:8], signed = True)/1000, int.from_bytes(self.data[8:12], signed = True)/1000, int.from_bytes(self.data[12:16], signed = True)/1000)
		return self

class ClientUpdate(NetworkObject):
	"""
	Used for a server to report any game state changes to the player.
	"""
	def from_data(self, game_objects):
		"""
		Take a list of game_objects eg. player, enemy, bullets, etc and generate a ClientUpdate. For convenience, put the player recieving the message first.
		"""
		self.game_objects = game_objects
		game_objects_as_bytes = bytearray()
		for game_object in game_objects:
			game_object_as_bytes = game_object.to_bytes()
			game_objects_as_bytes.extend(len(game_objects_as_bytes).to_bytes(2)) #two byte int for length of the next game object in bytes. 1 is too short, 2 is a good length
			game_objects_as_bytes.extend(game_object.to_bytes())
		super().from_data(NetworkObjectTypes['client_update'].value, game_objects_as_bytes)
		return self

	def from_bytes(self, as_bytes):
		"""
		Take a bytes representation of a ClientUpdate and convert it to a ClientUpdate
		"""
		super().from_bytes(as_bytes) #call the super to fill size and type fields, and to put the bytes data in the data field
		
		position = 0

		while position < len(self.data): #while we still have more data to process,
			GameEntity_len = int.from_bytes(self.data[position:position + 2]) #get the length of the next game entity
			GameEntity_data = self.data[position + 2: position + 2 + GameList_len] # slice from start of data to end of data. Add 2 to position because position is where the length is, so two bytes after is the start of the game entity data
			GameEntity_reconstructed = GameEntity.GameEntity().from_bytes(GameEntity_data) #convert the bytes representation to a GameEntity
			self.GameEntities.append(GameEntity_reconstructed) #append the reconstructed object to the list
			position += GameEntity_len #we processed GameEntity_len bytes of data, so we should note this in our position
		return self