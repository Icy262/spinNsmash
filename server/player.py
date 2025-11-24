class Player:
	def __init__(self, network_connection, real):
		#None for connection if false
		self.network_connection = network_connection
		self.real = real