import enum
import abc

class NetworkObjectTypes(enum.Enum): #register of network object types
	get_games = 0
	game_list = 1

def get_type(as_binary):
	"""
	Takes a binary representation of some NetworkObject and returns the object_type value
	"""
	return int.from_bytes(as_binary[2:3])

class NetworkObject(abc.ABC): #should not be instantiated on it's own, just a template
	size = None #total size of the data, useful for parsing the byte stream later
	object_type = None #type of request, eg. requesting a list of games, a player movement, a server informing the client about game events
	data = None #any additional data required as part of the object. This isn't used as part of the NetworkObject class, but is a template.

	def _set_size(self):
		"""
		Automatically sets the size value based on the other data in the object. should only be called by methods in classes that inherit from NetworkObject
		"""
		self.size = 3 + len(self.data) #size is 2, object_type is 1, data is len(data). Adding the sizes together produces the total size

	def from_data(self, object_type, data):
		"""
		Initializes the object by assigning the passed data to the appropriate variables
		"""
		self.object_type = object_type
		self.data = data
		self._set_size()

	def from_bytes(self, as_bytes):
		"""
		Initializes a NetworkObject using the bytes representation
		"""
		self.size = int.from_bytes(as_bytes[:2]) #takes the first two bytes of as_bytes (the block allocated for the size int), converts it to and int, and stores it.
		self.object_type = int.from_bytes(as_bytes[2:3]) #takes the third byte of as_bytes (the byte that stores the object_type), converts it, and stores it
		self.data = as_bytes[3:] #the rest of the object is data, write the data to data

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
		Initializes a GetGames network request. A games request doesn't require any additional data, so there are no arugments
		"""
		super().from_data(NetworkObjectTypes['get_games'].value, bytearray()) #calls the super init method. Passes the code for GetGames and a null byte array because no arguments are required for the request
	
	def from_bytes(self, as_bytes):
		"""
		Initializes a GetGames using the bytes representation
		"""
		super().from_bytes(self, as_bytes) #call the super to fill the size and type fields, and put the bytes representation of data into the data field
		#there is no bytes data for this network object, so do nothing

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
			running_games_descriptor.append(game.GameDescriptor().from_data(game)) #generates a GameDescriptor for each game and adds it to the list of GameDescriptors
		
		running_games_descriptor_as_bytes = bytearray() #to hold a byte representation of the game descriptor list
		
		for descriptor in running_games_descriptor: #for each game descriptor,
			descriptor_as_bytes = bytearray()
			game_descriptor_as_byte = descriptor.to_bytes() #convert to bytes
			len_as_bytes = len(game_descriptor_as_byte).to_bytes(2, 'big') #append the size of the game descriptor to the beginning of its data to allow for decoding.
			descriptor_as_bytes.extend(len_as_bytes) #append the length of the game descriptor as bytes
			descriptor_as_bytes.extend(game_descriptor_as_byte) #append the game descriptor as bytes
			running_games_descriptor_as_bytes.extend(descriptor_as_bytes) #append to the byte array
		super().from_data(NetworkObjectTypes['game_list'].value, running_games_descriptor_as_bytes) #pass the game id and list of running games to the super init
	
	def from_bytes(self, as_bytes):
		"""
		Initializes a GameList network request from the bytes representation. Primarily for use in decoding messages
		"""
		super().from_bytes(self, as_bytes) #call the super to fill size and type fields, and to put the bytes data in the data field
		running_games_descriptor = [] #will hold the final output of GameDescriptors
		
		position = 0

		while position < len(self.data): #while we still have more data to process,
			GameList_len = self.data[position] #get the length of the next GameList object
			GameList_data = self.data[position + 1: position + 1 + GameList_len] # slice from start of data to end of data. Add 1 to position because position is where the length is, so the next byte is the start of the GameList data
			GameList_reconstructed = GameList.GameList().from_bytes(GameList_data) #convert the bytes representation to a GameList
			running_games_descriptor.append(GameList_reconstructed) #append the reconstructed object to the list
			position += GameList_len #we processed GameList_len bytes of data, so we should note this in our position