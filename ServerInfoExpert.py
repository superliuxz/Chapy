import json

class ServerInfoExpert:

	def __init__(self):

		self._general_chatroom = "general"

		self._sock_to_alias = {}  # {socket:alias}
		self._alias_to_sock = {}  # {alias:[socket, current_room]}
		self._room_to_alias = {self._general_chatroom: set()}  # {room:<alias>}

		# integer 1 is the creator of the chatroom. because the user alias must be a string, the user alias can never equal to 1 since they are different type
		self._owner_to_room = {1: self._general_chatroom}
		self._room_to_owner = {self._general_chatroom: 1}  # {room: owner_alias}
		self._room_blk_list = {self._general_chatroom: set()}  # {room:<blocked_alias>}


	def getter(self):
		'''
		a getter that returns private fields

		:return: all the private dictionaries
		'''

		return self._sock_to_alias, self._alias_to_sock, self._room_to_alias, self._owner_to_room, \
				self._room_to_owner, self._room_blk_list


	def remove_client(self, socket):
		'''
		wrapper to _remove_client

		:param socket: the client socket to be removed
		:return:
		'''

		self._remove_client(socket)

	def _remove_client(self, socket):
		'''
		remove the socket, and its associated information from the server

		:param socket: the client socket to be removed
		:return:
		'''

		alias = self._sock_to_alias[socket]
		room = self._alias_to_sock[alias][1]
		del self._sock_to_alias[socket]
		del self._alias_to_sock[alias]
		self._room_to_alias[room].remove(alias)


	def send(self, d, s):
		'''
		wrapper to _send

		:param d: the data dictionary to be sent
		:param s: the target socket
		:return:
		'''

		self._send(d, s)

	def _send(self, d, s):
		'''
		send the data dictionary to the target socket

		:param d: the data dictionary to be sent
		:param s: the target socket
		:return:
		'''

		data = json.dumps(d)
		s.send(bytes(data, "utf-8"))


	def broadcast(self, d):
		'''
		wrapper to _broadcast

		:param d: the data dictionary to be broadcast
		:return:
		'''

		self._broadcast(d)

	def _broadcast(self, d):
		'''
		broadcast to other clients in the chatroom

		:param d: the dictionary with /say verb
		:return:
		'''

		sender = d["usr"]
		sender_room = self._alias_to_sock[sender][1]

		for a in self._alias_to_sock:
			sock, room = self._alias_to_sock[a]
			if a != sender:
				if sender_room == room:
					self._send(d, sock)


	def set_alias(self, d, s):
		'''
		wrapper to _set_alias

		:param d: the data dictionary with /set_alias verb
		:param s: the target socket
		:return:
		'''

		self._set_alias(d, s)

	# /set_alias
	def _set_alias(self, d, s):
		'''
		set the alias the the client

		:param d: the data dictionary with /set_alias verb
		:param s: the target socket
		:return:
		'''

		new_alias = d["body"]

		if new_alias not in self._alias_to_sock:

			self._sock_to_alias[s] = new_alias
			# first time set the alias, room = "general"
			if "usr" not in d:
				self._alias_to_sock[new_alias] = [s, self._general_chatroom]
				self._room_to_alias[self._general_chatroom].add(new_alias)
			# reset current alias
			else:
				old_alias = d["usr"]

				current_room = self._alias_to_sock[old_alias][1]

				self._alias_to_sock[new_alias] = [s, current_room]
				del self._alias_to_sock[old_alias]
				self._sock_to_alias[s] = new_alias

				## update room_to_alias
				self._room_to_alias[current_room].remove(old_alias)
				self._room_to_alias[current_room].add(new_alias)

				try:
					## update owner_to_room
					room = self._owner_to_room[old_alias]
					del self._owner_to_room[old_alias]
					self._owner_to_room[new_alias] = room

					## update room_to_owner
					self._room_to_owner[room] = new_alias
				except KeyError:
					pass

				## update room_blk_list
				## O(n), not optimized becoz no reversed dictionary look up
				for room in self._room_blk_list:
					if old_alias in self._room_blk_list[room]:
						self._room_blk_list[room].remove(old_alias)
						self._room_blk_list[room].add(new_alias)

			d["success"] = "true"

		else:
			d["success"] = "false"
			d["reason"] = "The alias has been used!"

		# return the request to the client
		self._send(d, s)


	def join(self, d, s):
		'''
		wrapper to _join

		:param d: the data dictionary
		:param s: the target socket
		:return:
		'''

		self._join(d, s)

	# /join
	def _join(self, d, s):
		'''
		join a user to the target chatroom

		:param d: the the data dictionary
		:param s: the sender socket
		:return: void
		'''

		roomname = d["body"]
		usrName = d["usr"]

		## the two following condition are mutually exclusive.
		## if a room DNE, then no user can be blocked from that room.
		if roomname not in self._room_to_owner:
			d["success"] = "false"
			d["reason"] = "The room does not exist!"

		elif usrName in self._room_blk_list[roomname]:
			d["success"] = "false"
			d["reason"] = "You are blocked!"

		else:
				prevInfo = self._alias_to_sock[usrName]
				prevRoom = prevInfo[1]
				self._move(usrName, prevRoom, roomname)
				d["success"] = "true"

		self._send(d, s)


	def _move(self, usr, old_room, new_room):
		'''
		move a user from the old room to the new room
		this method is to be called with the class therefore no wrapper

		:param usr: the user alias
		:param old_room: the current chatroom
		:param new_room: the chatroom to join
		:return: void
		'''

		if old_room == new_room:
			return

		soc = self._alias_to_sock[usr][0]
		self._room_to_alias[new_room].add(usr)  # adds the usr to its new desired room
		try:
			self._room_to_alias[old_room].remove(usr)  # remove the usr from its previous room
		except KeyError:
			pass
		self._alias_to_sock[usr] = [soc, new_room]  # update usr room info


	def create(self, d, s):
		'''
		wrapper to _create

		:param d: the data dictionary
		:param s: the target socket
		:return:
		'''

		self._create(d, s)

	# /create
	def _create(self, d, s):
		'''
		create a new chatroom

		:param d: the data dictionary
		:param s: socket of the sender
		:return: void
		'''

		roomName = d["body"]
		ownerName = d["usr"]

		if roomName in self._room_to_owner or ownerName in self._owner_to_room:
			d["success"] = "false"

		else:
			self._room_to_owner[roomName] = ownerName
			self._owner_to_room[ownerName] = roomName
			# self.client_to_alias = {} # {socket:alias} maps socket to usr alias
			# self.alias_to_client = {} # {alias:[socket, current_room]} map alias to room number and socket
			self._room_to_alias[roomName] = set()  # {room:<alias>}    set() = all users in the room  room# = 0

			self._room_blk_list[roomName] = set()  # {room:<blocked_alias>}

			d["success"] = "true"

		self._send(d, s)


	def block(self, d, s):
		'''
		the wrapper to _block

		:param d: the data dictionary
		:param s: the target socket
		:return:
		'''

		self._block(d, s)

	# /block
	def _block(self, d, s):
		'''
		block a user from a chatroom, and the user will be moved to the general chatroom

		:param d: the data dictionary
		:param s: sender socket
		:return: void
		'''

		usrName = d["body"]
		ownerName = d["usr"]

		## if the user is not any room owners, or the blocked user alias DNE, then false
		if ownerName not in self._owner_to_room or usrName not in self._alias_to_sock:
			d["success"] = "false"

		else:
			#ivd = {v: k for k, v in self._room_to_owner.items()}
			roomName = self._owner_to_room[ownerName]
			self._room_blk_list[roomName].add(usrName)
			self._move(usrName, roomName, "general")
			d["success"] = "true"

		self._send(d, s)


	def unblock(self, d, s):
		'''
		the wrapper to _unblock

		:param d: the data dictionary
		:param s: the target socket
		:return:
		'''

		self._unblock(d, s)

	# /unblock
	def _unblock(self, d, s):
		'''
		unblock a user from the chatroom

		:param d: the the data dictionary
		:param s: the sender socket
		:return:
		'''

		usrName = d["body"]
		ownerName = d["usr"]

		if ownerName not in self._owner_to_room or usrName not in self._alias_to_sock:
			d["success"] = "false"

		else:
			roomName = self._owner_to_room[ownerName]
			if usrName in self._room_blk_list[roomName]:  # if not in list will result in seg fault
				self._room_blk_list[roomName].remove(usrName)
				d["success"] = "true"

		self._send(d, s)


	def delete(self, d, s):
		'''
		wrapper to _Delete

		:param d: the data dictionary
		:param s: the target socket
		:return:
		'''

		self._delete(d, s)

	# /delete
	def _delete(self, d, s):
		'''
		a user tries to delete a chatroom

		:param d: the data dictionary
		:param s: sender socket
		:return: void
		'''

		ownerName = d["usr"]

		if ownerName not in self._owner_to_room:
			d["success"] = "false"

		else:
			#ivd = {v: k for k, v in self._owner_to_room.items()}
			roomName = self._owner_to_room[ownerName]
			clientList = self._room_to_alias[roomName]  # grab all clients in that room

			##
			while len(clientList) > 0:
				client = clientList.pop()
				self._move(client, roomName, "general")

			del self._room_to_alias[roomName]  # remove the room
			del self._room_blk_list[roomName]
			del self._owner_to_room[ownerName]
			del self._room_to_owner[roomName]

			d["success"] = "true"

		self._send(d, s)


	def lsroom(self, d, s):
		'''
		wrapper to _lsroom

		:param d: the data dictionary
		:param s: the target socket
		:return:
		'''

		self._lsroom(d, s)

	# /lsroom
	def _lsroom(self, d, s):
		'''
		list all chatrooms on the server

		:param d: the the data dictionary
		:param s: the sender socket
		:return: void
		'''

		try:
			d["rooms"] = list(self._room_to_alias.keys())
			d["success"] = "true"
		except:
			d["success"] = "false"

		self._send(d, s)


	def lsusr(self, d, s):
		'''
		wrapper to _lsusr

		:param d: the data dictionary
		:param s: the target socket
		:return:
		'''
		self._lsusr(d, s)

	# /lsusr
	def _lsusr(self, d, s):
		'''
		list all users and the rooms they are in

		:param d: the the data dictionary
		:param s: the sender socket
		:return: void
		'''

		try:
			d["live_users"] = [ (a, v[1]) for a, v in self._alias_to_sock.items() ]
			d["success"] = "true"
		except:
			d["success"] = "false"

		self._send(d, s)