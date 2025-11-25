import threading
from server.player_container import PlayerContainer
from common.network_messages import NetworkObjectTypes, GameList, GetGames, get_type, JoinGame
from common import network_connection

class GameLobby(PlayerContainer):
	"""
	When the player is connected to the server, but not in a game, the player should be here. The player_handler function handles the main functionality of this class by responding to player messages
	"""

	def player_handler(self, games):
		"""
		Should be run in a separate thread. Will loop though the connected players and respond to any messages they have. Acts as a game selector. Should be passed the main list of running games
		"""
		while True: #repeat for the duration of the program
			for player in self.connected_players: #loop through the connected players and check for any new messages.
				message = player.network_connection.get_next_message() #get the next message from this player, if there is any, if not it'll be None
				if(message != None): #if there is some new message,
					#considered using match case, but python sucks and doesn't support .value					
					if get_type(message) == NetworkObjectTypes["get_games"].value: #if a get_games message,
						#respond to the message by sending a GameList
						response = GameList() #generate a GameList from the list of running games
						response.from_data(games) #populate the GameList object with the running games data
						player.network_connection.send(response.to_bytes()) #convert the GameList to bytes and send it back to the player
					elif get_type(message) == NetworkObjectTypes["join_game"].value: #if a join_game message,
						#TODO: add error handling for illegal join messages
						#transfer the player to the game by removing from our list and adding it to the game's list
						self.transfer_player(player, games[JoinGame().from_bytes(message).game_id])
					else: #unrecognized status code
						print("ERROR: STATUS CODE NOT RECOGNIZED", get_type(message)) #TODO: replace with actual error handling