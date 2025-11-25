class Player:
	def __init__(self, network_connection, real, player_entity = None):
		#None for connection if real is False
		self.network_connection = network_connection
		self.real = real
		self.player_entity = player_entity
		self.player_entity_updated = True