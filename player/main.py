import socket
import threading
from common.network_requests import NetworkObjectTypes, GetGames
from common.client_connection import ClientConnection

#TEST CODE, REMOVE LATER

server_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_connection.connect(('127.0.0.1', 4004))
connection = ClientConnection(server_connection)
request = GetGames()
request.from_data()
connection.send(request.to_bytes())
threading.Thread(target = connection.recieve).start()
while True:
	print(connection.get_next_request())