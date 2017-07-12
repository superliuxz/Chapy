import socket, sys, json, select

class Server:
	def __init__(self, host = socket.gethostname(), port = 8888):
		self.host = host
		self.port = port
		self.general_chatroom = 0
		self.clients = {}
		self.rooms = {0:{}}
		# TODO: need four data structures, {alias:socket}, {socket:alias}, {alias:room_id} and {room_id:<alias>}

		self.s = socket.socket()
		self.s.bind((self.host, self.port))
		self.s.listen(5)

		self.connections = [self.s]

		print("Sever has started!")

	def run_forever(self):
		while True:

			read_list, *_ = select.select(self.connections, [], [])

			for s in read_list:
				# new client connection
				if s == self.s:
					sock, *_ = self.s.accept()
					print("{} has connected!".format(sock))
					self.connections.append(sock)
				# clients send in stuff
				else:
					try:
						# TODO: need to make sure the client does not send a json longer than 4096!
						data = s.recv(4096)
						if data:
							d = json.loads(data, encoding="utf-8")
							# TODO: after conversion, perform operations accordingly.
							if d["verb"] == "/say":
								print(d)
							elif d["verb"] == "/set_alias":
								if d["body"] == "will":
									s.send(b"F")
								else:
									s.send(b"T")
							elif d["verb"] == "/join":
								print(d)
							elif d["verb"] == "/create":
								print(d)
							elif d["verb"] == "/block":
								print(d)
							elif d["verb"] == "/unblock":
								print(d)
							elif d["verb"] == "/delete":
								print(d)

					except:
						# lose the connection with the client
						sock.close()
						self.connections.remove(sock)
						continue

	# todo: need to implements these
	def _broadcast(self, d):
		pass

	# /set_alias
	def _set_alias(self, d):
		pass

	# /join
	def _join(self, d):
		pass

	# /create
	def _create(self, d):
		pass

	# /block
	def _block(self, d):
		pass

	# /unblock
	def _unblock(self, d):
		pass

	# /delete
	def _delete(self, d):
		pass

if __name__ == "__main__":
	server = Server()
	server.run_forever()