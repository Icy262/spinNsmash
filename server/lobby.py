import threading
from server.player_container import PlayerContainer
from common.network_requests import NetworkObjectTypes, GameList, GetGames, get_type
from common import client_connection

class GameLobby(PlayerContainer):
	"""
	When the player is connected to the server, but not in a game, the player should be here. The player_handler function handles the main functionality of this class by responding to player requests
	"""

	def player_handler(self, games):
		"""
		Should be run in a separate thread. Will loop though the connected players and respond to any requests they have. Acts as a game selector. Should be passed the main list of running games
		"""
		while True: #repeat for the duration of the program
			for i in range(len(self.connected_players)): #loop through the connected players and check for any new messages
				request = self.connected_players[i].client_connection.get_next_request() #get the next request from this player, if there is any, if not it'll be None
				if(request != None): #if there is some new request,
					#considered using match case, but python sucks and doesn't support .value					
					if get_type(request) == NetworkObjectTypes['get_games'].value: #if a get_games request,
						#respond to the request by sending a GameList
						response = GameList() #generate a GameList from the list of running games
						response.from_data(games) #populate the GameList object with the running games data
						self.connected_players[i].client_connection.send(response.to_bytes()) #convert the GameList to bytes and send it back to the player
					else: #unrecognized status code
						print("STATUS CODE NOT RECOGNIZED") #TODO: replace with actual error handling