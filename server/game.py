from server.player_container import PlayerContainer

class Game(PlayerContainer):
	def __init__(self, num_bots, size_x, size_y):
		"""
		Initializes the game state.
		"""
		self.num_bots = num_bots #TODO: Unimplimented
		self.size_x = size_x
		self.size_y =size_y
		super().__init__()

	def add_player(self, player):
		"""
		Overrides the default behaviour to initialize the player in game state
		"""
		self.connected_players.append(player) #add the player to the list of players
		#initialize the player with some location and state
	
	def run(self):
		"""
		Processes the main game loop of the game
		"""
		while True: #repeat for the duration of the program
			for player in self.connected_players: #loop through the connected players and check for any new messages.
				request = player.network_connection.get_next_request() #get the next request from this player, if there is any, if not it'll be None
				if(request != None): #if there is some new request,
					#considered using match case, but python sucks and doesn't support .value					
					if get_type(request) == NetworkObjectTypes['player_move'].value: #if a get_games request,
					else: #unrecognized status code
						print("ERROR: STATUS CODE NOT RECOGNIZED", get_type(request)) #TODO: replace with actual error handling