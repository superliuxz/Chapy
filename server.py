import socket, sys, json, select, time

class Server:
	def __init__(self, host = socket.gethostname(), port = 8888, debug = True):
		'''
		default constructor

		:param host: default as local machine
		:param port: default 8888
		'''
		self.host = host
		self.port = port
		self.debug = debug
		self.general_chatroom = "general"

		self.sock_to_alias = {} # {socket:alias}
		self.alias_to_sock = {} # {alias:[socket, current_room]}
		self.room_to_alias = {self.general_chatroom:set()} # {room:<alias>}

		# integer 1 is the creater of the chatroom. because the user alias must be a string, the user alias can never equal to 1 since they are different type
		self.owner_to_room = {1:self.general_chatroom}
		self.room_to_owner = {self.general_chatroom:1} # {room: owner_alias}
		self.room_blk_list = {self.general_chatroom:set()} # {room:<blocked_alias>}


		self.s = socket.socket()
		self.s.bind((self.host, self.port))
		self.s.listen(5)

		self.connections = [self.s]

		print("Sever has started!")

	def debug_print(self):
		print("DEBUG - alias_to_sock", self.alias_to_sock)
		print("DEBUG - sock_to_alias", self.sock_to_alias)
		print("DEBUG - room_to_alias", self.room_to_alias)
		print("DEBUG - owner_to_room", self.owner_to_room)
		print("DEBUG - room_to_owner", self.room_to_owner)
		print("DEBUG - room_blk_list", self.room_blk_list)
		print()

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
						data = s.recv(4096).decode("utf-8")
						if self.debug: print("DEBUG - " + data)
						# if the client calls socket.close(), the server will receive a empty string
						if data:
							d = json.loads(data, encoding = "utf-8")

							# according to the verb, respond accordingly
							verb = d["verb"]
							# TODO: factorize the following into a dedicated class, and use composition
							if verb == "/say":
								self._broadcast(d)
							elif verb == "/set_alias":
								# TODO: set_alias also needs to update those ones in the owner list, blocked list etc.
								self._set_alias(d, s)
							elif verb == "/join":
								self._join(d, s)
							elif verb == "/create":
								self._create(d, s)
							elif verb == "/block":
								self._block(d, s)
							elif verb == "/unblock":
								self._unblock(d, s)
							elif verb == "/delete":
								self._delete(d, s)
							elif verb == "/lsroom":
								self._lsroom(d, s)
							elif verb == "/lsusr":
								self._lsisr(d, s)
							# elif verb == "/logout":
							# 	print(s.getpeername())
							# 	time.sleep(120)
							# 	self._remove_client(s)
							# 	self.connections.remove(s)
							# 	s.close()
							# 	print(self.connections)
							if self.debug: self.debug_print()
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
		alias = self.sock_to_alias[socket]
		room = self.alias_to_sock[alias][1]
		del self.sock_to_alias[socket]
		del self.alias_to_sock[alias]
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

	def _broadcast(self, d):
		'''
		broadcast to other clients in the chatroom

		:param d: the dictionary with /say verb
		:return:
		'''

		sender = d["usr"]
		sender_room = self.alias_to_sock[sender][1]

		for a in self.alias_to_sock:
			sock, room = self.alias_to_sock[a]
			if a != sender:
				if sender_room == room:
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

		if new_alias not in self.alias_to_sock:

			self.sock_to_alias[s] = new_alias
			# first time set the alias, room = 0, since first time login
			if "status" not in d:
				self.alias_to_sock[new_alias] = [s, self.general_chatroom]
				self.room_to_alias[self.general_chatroom].add(new_alias)
			# reset current alias
			else:
				old_alias = d["usr"]

				current_room = self.alias_to_sock[old_alias][1]

				self.alias_to_sock[new_alias] = [s, current_room]
				del self.alias_to_sock[old_alias]
				self.sock_to_alias[s] = new_alias

				self.room_to_alias[current_room].remove(old_alias)
				self.room_to_alias[current_room].add(new_alias)

			d["success"] = "true"

		else:
			d["success"] = "false"

		# return the request to the client
		self._send(d, s)

	# /join
	def _join(self, d, s):
		'''
		join a user to the target chatroom

		:param d: the message dictionary
		:param s: the sender socket
		:return: void
		'''

		roomname = d["body"]
		usrName = d["usr"]

		if roomname not in self.room_to_owner or usrName in self.room_blk_list[roomname]:
			d["success"] = "false"

		else:
			prevInfo = self.alias_to_sock[usrName]
			prevRoom = prevInfo[1]
			self._move(usrName, prevRoom, roomname)
			d["success"] = "true"

		self._send(d, s)

	def _move(self, usr, old_room, new_room):
		'''
		move a user from the old room to the new room

		:param usr:
		:param old_room:
		:param new_room:
		:return: void
		'''

		soc = self.alias_to_sock[usr][0]
		self.room_to_alias[new_room].add(usr)  # adds the usr to its new desired room
		try:
			self.room_to_alias[old_room].remove(usr)  # remove the usr from its previous room
		except KeyError:
			pass
		self.alias_to_sock[usr] = [soc, new_room]  # update usr room info

	# /create
	def _create(self, d, s):
		'''
		create a new chatroom

		:param d: message dictionary
		:param s: socket of the sender
		:return: void
		'''
		roomName = d["body"]
		ownerName = d["usr"]

		if roomName in self.room_to_owner or ownerName in self.owner_to_room:
			d["success"] = "false"

		else:
			self.room_to_owner[roomName] = ownerName
			self.owner_to_room[ownerName] = roomName
			# self.client_to_alias = {} # {socket:alias} maps socket to usr alias
			# self.alias_to_client = {} # {alias:[socket, current_room]} map alias to room number and socket
			self.room_to_alias[roomName] = set()  # {room:<alias>}    set() = all users in the room  room# = 0

			self.room_blk_list[roomName] = set()  # {room:<blocked_alias>}

			d["success"] = "true"

		self._send(d, s)

	# /block
	def _block(self, d, s):
		'''
		block a user from a chatroom, and the user will be moved to the general chatroom

		:param d: message dictionary
		:param s: sender socket
		:return: void
		'''

		usrName = d["body"]
		ownerName = d["usr"]

		## if the user is not any room owners, or the blocked user alias DNE, then false
		if ownerName not in self.owner_to_room or usrName not in self.alias_to_sock:
			d["success"] = "false"

		else:
			#ivd = {v: k for k, v in self.room_to_owner.items()}
			roomName = self.owner_to_room[ownerName]
			self.room_blk_list[roomName].add(usrName)
			self._move(usrName, roomName, "general")
			d["success"] = "true"

		self._send(d, s)

	# /unblock
	def _unblock(self, d, s):
		'''
		unblock a user from the chatroom

		:param d: the message dictionary
		:param s: the sender socket
		:return:
		'''

		usrName = d["body"]
		ownerName = d["usr"]

		if ownerName not in self.owner_to_room or usrName not in self.alias_to_sock:
			d["success"] = "false"

		else:
			roomName = self.owner_to_room[ownerName]
			if usrName in self.room_blk_list[roomName]:  # if not in list will result in seg fault
				self.room_blk_list[roomName].remove(usrName)
				d["success"] = "true"

		self._send(d, s)

	# /delete
	def _delete(self, d, s):
		'''
		a user tries to delete a chatroom

		:param d: message dictionary
		:param s: sender socket
		:return: void
		'''

		ownerName = d["usr"]

		if ownerName not in self.owner_to_room:
			d["success"] = "false"

		else:
			#ivd = {v: k for k, v in self.owner_to_room.items()}
			roomName = self.owner_to_room[ownerName]
			clientList = self.room_to_alias[roomName]  # grab all clients in that room

			##
			while len(clientList) > 0:
				client = clientList.pop()
				self._move(client, roomName, "general")

			del self.room_to_alias[roomName]  # remove the room
			del self.room_blk_list[roomName]
			del self.owner_to_room[ownerName]
			del self.room_to_owner[roomName]

			d["success"] = "true"

		self._send(d, s)

	# /lsroom
	def _lsroom(self, d, s):
		'''
		list all chatrooms on the server

		:param d: the message dictionary
		:param s: the sender socket
		:return: void
		'''

		try:
			d["rooms"] = list(self.room_to_alias.keys())
			d["success"] = "true"
		except:
			d["success"] = "false"

		self._send(d, s)

	# /lsusr
	def _lsisr(self, d, s):
		'''
		list all users and the rooms they are in

		:param d: the message dictionary
		:param s: the sender socket
		:return: void
		'''

		try:
			d["live_users"] = [ (a, v[1]) for a, v in self.alias_to_sock.items() ]
			d["success"] = "true"
		except:
			d["success"] = "false"

		self._send(d, s)

if __name__ == "__main__":
	server = Server()
	server.run_forever()