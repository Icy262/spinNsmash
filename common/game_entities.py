import enum

class GameEntityIds(enum.Enum):
	player = 1

class GameEntity:
	def from_data(self, dx, dy, vx, vy):
		self.dx = dx
		self.dy = dy
		self.vx = vx
		self.vy = vy

	# def from_bytes(self):