import abc
import threading
import server.player

class PlayerContainer(abc.ABC):
	"""
	This should be extended to provide thread-safe functionality for any class that works with players (eg. the game lobby, or a game instance).
	"""
	connected_players = [] #holds all the players being contained in this container

	def add_player(self, player):
		"""
		Adds the player to the connected players list. Probably needs to be overwritten by most of the inheriting classes.
		"""
		with threading.Lock(): #thread safety is cool
			self.connected_players.append(player) #just appends the player to the player list

	def transfer_player(self, player, other_container):
		"""
		Transfers a player from this instance to another instance of PlayerContainer. If the player isn't in the player list here, does nothing
		"""
		with threading.Lock(): #thread safety is fun
			if(self.connected_players.remove(player) != None): #removes the player from our list. list.remove() returns the value it removed. If this is None, it means the player is not in the list. We need to handle this because if not you will get None values getting added to other containers
				other_container.add_player(player) #adds the player to the other container
			else: #player wasn't in player list
				print("PLAYER NOT CONNECTED") #SHOULD PROBABLY HANDLE THIS PROPERLY LATER