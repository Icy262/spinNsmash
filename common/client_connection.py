import socket

class ClientConnection:
	def __init__(self, connection):
		self.read_queue = bytearray()
		self.recieved_requests_queue = []
		self.socket_connection = connection
	
	def send(self, data):
		"""
		For sending data to an endpoint recieving using recieve(). If used with a healthy connection, guarantees that the data will be sent, or the client will disconnect before all data is sent. should be passed a bytearray
		"""
		total_size = len(data) #gets the total length of the array
		amount_sent = 0 #amount set before anything is sent is 0. We need to know how far we are in sending the data
		while amount_sent < total_size: #while we haven't sent the entire array, repeat
			sent_this_time = self.socket_connection.send(data[amount_sent:]) #send data starting at the end of where we did last time
			if sent_this_time == 0: #if send returns 0, the connection has been closed
				print('connection failed on send') #HANDLE THIS PROPERLY LATER
				return
			else: #connection is healthy
				amount_sent += sent_this_time #increase the total number of bytes sent by the amount of bytes sent this time
	
	def recieve(self):
		"""
		For recieving data from an endpoint using send(). To be run continuously in a separate thread.
		"""
		while True: #for the duration of the connection, try to read the next full packet and return it
			if len(self.read_queue) < 2: #we don't know how long the next object is, read until we find out, if we know the object length, do nothing
				while len(self.read_queue) < 2: #repeat until we have 2 bytes
					recieved_this_time = self.socket_connection.recv(1024) #just try to read a bunch of data
					if len(recieved_this_time) == 0: #if no data was recieved, that means the connection has failed and should be terminated
						print('connection failed on recieve length') #HANDLE THIS PROPERLY LATER
						return
					else: #connection healthy, data was read
						self.read_queue.extend(recieved_this_time)
			#we now have the length of the next network object, we need to read the rest of it
			NetworkObject_length = int.from_bytes(self.read_queue[:2]) #convert the first two bytes to an int. The int represents the length of the network object
			while len(self.read_queue) < NetworkObject_length: #while we don't have the full packet,
				recieved_this_time = self.socket_connection.recv(1024) #read more data
				if len(recieved_this_time) == 0: #if we don't recieve data, the connection failed
					print('connection failed on recieve data') #TODO: HANDLE THIS PROPERLY LATER
					return
				else: #connection helathy, data was read
					self.read_queue.extend(recieved_this_time)
			#we now have the full network object
			request = self.read_queue[:NetworkObject_length] #pull just the full request out of the read_queue
			del self.read_queue[:NetworkObject_length] #remove the request we just read from the queue
			self.recieved_requests_queue.append(request) #add the request to the list of recieved requests that havn't been used yet
	
	def get_next_request(self):
		"""
		Will return the first request in the queue, or None if there are no pending requests
		"""
		return self.recieved_requests_queue.pop(0) if self.recieved_requests_queue else None #takes the first request out of the queue and returns it, if there is anything in the list, if not, returns None