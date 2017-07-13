import socket, sys, json, select, time

class Server:
	def __init__(self, host = socket.gethostname(), port = 8888):
		'''
		default constructor

		:param host: default as local machine
		:param port: default 8888
		'''
		self.host = host
		self.port = port
		self.general_chatroom = 0

		self.client_to_alias = {} # {socket:alias}
		self.alias_to_client = {} # {alias:[socket, current_room]}
		self.room_to_alias = {0:set()} # {room:<alias>}

		self.room_owners = {0:None} # {room: owner_alias}
		self.room_blk_list = {0:set()} # {room:<blocked_alias>}

		self.s = socket.socket()
		self.s.bind((self.host, self.port))
		self.s.listen(5)

		self.connections = [self.s]

		print("Sever has started!")

	def run_forever(self):
		'''
		the loop keeps listening to all the connected clients, and operates based on the verbs

		:return:
		'''
		try:
			while True:

				rlist, wlist, xlist = select.select(self.connections, [], [])

				for s in rlist:

					# new client connection
					if s == self.s:
						sock, *_ = self.s.accept()
						print("{} has connected!".format(sock.getpeername()))
						self.connections.append(sock)

					# clients send in stuff
					else:
						# TODO: need to make sure the client does not send a json longer than 4096!
						data = s.recv(4096)
						print(data)
						# if the client calls socket.close(), the server will receive a empty string
						if data != b"":
							d = json.loads(data, encoding="utf-8")

							# according to the verb, respond accordingly
							verb = d["verb"]

							# TODO:
							if verb == "/say":
								self._broadcast(d)
							elif verb == "/set_alias":
								self._set_alias(d, s)
							elif verb == "/join":
								print(d)
							elif verb == "/create":
								print(d)
							elif verb == "/block":
								print(d)
							elif verb == "/unblock":
								print(d)
							elif verb == "/delete":
								print(d)
							# elif verb == "/logout":
							# 	print(s.getpeername())
							# 	time.sleep(120)
							# 	self._remove_client(s)
							# 	self.connections.remove(s)
							# 	s.close()
							# 	print(self.connections)

						# client Ctrl-C
						else:
							print("{} has logged off.".format(s.getpeername()))
							self._remove_client(s)
							self.connections.remove(s)
							s.close()
		except KeyboardInterrupt:
			# Ctrl-C to quit
			for s in self.connections: s.close()
			print("Shutdown the server...")
			sys.exit(0)



	def _remove_client(self, socket):
		'''
		remove the socket, and its associated information from the server

		:param socket:
		:return:
		'''
		alias = self.client_to_alias[socket]
		room = self.alias_to_client[alias][1]
		del self.client_to_alias[socket]
		del self.alias_to_client[alias]
		self.room_to_alias[room].remove(alias)

	def _send(self, dictionary, socket):
		'''
		send the json/dictionary to the target socket

		:param dictionary:
		:param socket:
		:return:
		'''
		data = json.dumps(dictionary)
		socket.send(bytes(data, "utf-8"))

	# todo: need to implements these
	def _broadcast(self, d):
		'''
		broadcast to other clients in the chatroom

		:param d: the dictionary with /say verb
		:return:
		'''

		sender = d["usr"]

		for a in self.alias_to_client:
			sock = self.alias_to_client[a][0]
			if a != sender:
				self._send(d, sock)

	# /set_alias
	def _set_alias(self, d, s):
		'''
		set the alias the the client

		:param d:
		:param s:
		:return:
		'''

		new_alias = d["body"]

		if new_alias not in self.alias_to_client:

			self.client_to_alias[s] = new_alias
			# first time set the alias, room = 0, since first time login
			if "status" not in d:
				self.alias_to_client[new_alias] = [s, 0]
				self.room_to_alias[0].add(new_alias)
			# reset current alias
			else:
				# todo: need to update the client alias
				old_alias = d["usr"]
				current_room = self.alias_to_client[old_alias][1]
				self.alias_to_client[new_alias] = [s, current_room]
				self.room_to_alias[current_room].remove(old_alias)
				self.room_to_alias[current_room].add(new_alias)


			d["success"] = "true"
		else:
			d["success"] = "false"

		# return the request to the client
		self._send(d, s)

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