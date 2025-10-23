import socket
import threading
from common.client_connection import ClientConnection
from server.lobby import GameLobby
from server.player import Player

#the config should be moved into a json at some point
#adding debugging to log files would be a good idea

max_games = 3 #maximum of 3 games should be running on this server at any given time
port = 4004 #This port is pretty easy to remember and doesn't seem to be in widespread use

client_connection_listener = socket.socket() #create a socket for the server to use to accept client connections
client_connection_listener.bind(('', port)) #bind the socket. the bind function expects a pair containing an ip and port. using '' as the ip causes the socket to bind to all interfaces.
client_connection_listener.listen() #set the socket to listen mode

game_lobby = GameLobby() #create a game lobby to pass players into once they connect
games = [] #a list of running games

threading.Thread(target = game_lobby.player_handler, args = (games,)).start() #start the game_lobby's player handling

while True:
	socket_connection = client_connection_listener.accept()[0] #blocks the thread until a new connection arrives. when a connection arrives, accepts, and stores the connection. accept() returns a tuple with the connection and the address, we use [0] to just take the connection returned
	new_client_connection = ClientConnection(socket_connection) #makes a new client connection object with the socket connection
	player = Player(new_client_connection, True) #create a new player for this player connection, and designate it as a real player
	game_lobby.add_player(player) #transfers the player to the game_lobby
	threading.Thread(target = new_client_connection.recieve).start() #start a new thread to listen for messages from the client