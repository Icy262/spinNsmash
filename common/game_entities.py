import enum

class GameEntityIds(enum.Enum):
	player = 0
	bullet = 1

class GameEntity:
	colour = (0, 0, 0) #default colour
	def get_type(as_bytes):
		"""
		return the game entity id field
		"""
		return as_bytes[0]

	def from_data(self, entity_type, dx, dy, vx, vy, size):
		"""
		To create a game entity from data about it. dx, dy, vx, vy, size should all be floats
		"""
		self.entity_type = entity_type
		self.dx = dx
		self.dy = dy
		self.vx = vx
		self.vy = vy
		self.size = size
		return self

	def from_bytes(self, as_bytes):
		"""
		Convert a bytes representation created by to_bytes and convert back into an object
		"""
		#take 4 byte blocks of data and convert them into values. divide by 1000 because we mult by 1000 to convert to bytes
		self.as_bytes = as_bytes
		self.entity_type = as_bytes[0]
		self.dx = int.from_bytes(as_bytes[1:5], "big", signed = True)/1000
		self.dy = int.from_bytes(as_bytes[5:9], "big", signed = True)/1000
		self.vx = int.from_bytes(as_bytes[9:13], "big", signed = True)/1000
		self.vy = int.from_bytes(as_bytes[13:17], "big", signed = True)/1000
		self.size = int.from_bytes(as_bytes[17:18])
		return self

	def to_bytes(self):
		"""
		Convert and object into a byte array for passing over the network.
		"""
		as_bytes = bytearray()
		as_bytes.extend(int(self.entity_type).to_bytes(1))
		as_bytes.extend(int(self.dx*1000).to_bytes(4, signed = True)) #mult by 1000 to preserve 3 decimals
		as_bytes.extend(int(self.dy*1000).to_bytes(4, signed = True))
		as_bytes.extend(int(self.vx*1000).to_bytes(4, signed = True))
		as_bytes.extend(int(self.vy*1000).to_bytes(4, signed = True))
		as_bytes.extend(int(self.size).to_bytes(1)) #255 is the maximum size we really need anyway
		return as_bytes

class PlayerEntity(GameEntity):
	colour = (0, 255, 0) #green for player

class BulletEntity(GameEntity):
	colour = (255, 0, 0) #red for bullet