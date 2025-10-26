class Player:
	def __init__(self, connection, real_player, x = 0, y = 0):
		self.x = x
		self.y = y
		self.client_connection = connection #the player's connection if it is a real person, or None if a bot
		self.real_player = real_player #True if a real player, false if a bot