class ServerInfoExpert:

	def __init__(self):

		self.__general_chatroom = "general"

		self.__sock_to_alias = {}  # {socket:alias}
		self.__alias_to_sock = {}  # {alias:[socket, current_room]}
		self.__room_to_alias = {self.__general_chatroom: set()}  # {room:<alias>}

		## integer 1 is the creator of the chatroom. because the user alias must be a string,
		## the user alias can never equal to 1 since they are different type
		self.__owner_to_room = {1: self.__general_chatroom}
		self.__room_to_owner = {self.__general_chatroom: 1}  # {room: owner_alias}
		self.__room_blk_list = {self.__general_chatroom: set()}  # {room:<blocked_alias>}


	def getter(self):
		"""
		a getter that returns private fields

		:return: all the private dictionaries
		"""

		return self.__sock_to_alias, self.__alias_to_sock, self.__room_to_alias, self.__owner_to_room, \
				self.__room_to_owner, self.__room_blk_list


	def remove_client(self, sock):
		"""
		wrapper to _remove_client

		:param sock: the target socket
		:return:
		"""

		self.__remove_client(sock)

	def __remove_client(self, socket):
		"""
		remove the socket, and its associated information from the server

		:param socket: the client socket to be removed
		:return:
		"""

		alias = self.__sock_to_alias[socket]
		room = self.__alias_to_sock[alias][1]
		del self.__sock_to_alias[socket]
		del self.__alias_to_sock[alias]
		self.__room_to_alias[room].remove(alias)


	def broadcast(self, d):
		"""
		wrapper to _broadcast

		:param d: the data dictionary to be broadcast
		:return:
		"""

		return self.__broadcast(d)

	def __broadcast(self, d):
		"""
		broadcast to other clients in the chatroom

		:param d: the dictionary with /say verb
		:return: a list of sockets to be broadcast to
		"""

		sender = d["usr"]
		sender_room = self.__alias_to_sock[sender][1]

		tmp = []

		try:
			for a in self.__alias_to_sock:
				sock, room = self.__alias_to_sock[a]
				if a != sender:
					if sender_room == room:
						tmp.append(sock)

			d["success"] = "true"
		except:
			d["success"] = "false"

		return d, tmp

	def set_alias(self, d, s):
		"""
		wrapper to _set_alias

		:param d: the data dictionary with /set_alias verb
		:param s: the target socket
		:return:
		"""

		return self.__set_alias(d, s)

	## /set_alias
	def __set_alias(self, d, s):
		"""
		set the alias the the client

		:param d: the data dictionary with /set_alias verb
		:return: the updated dictionary
		"""

		new_alias = d["body"]

		if new_alias not in self.__alias_to_sock:

			self.__sock_to_alias[s] = new_alias
			## first time set the alias, room = "general"
			if "usr" not in d:
				self.__alias_to_sock[new_alias] = [s, self.__general_chatroom]
				self.__room_to_alias[self.__general_chatroom].add(new_alias)
			## reset current alias
			else:
				old_alias = d["usr"]

				current_room = self.__alias_to_sock[old_alias][1]

				self.__alias_to_sock[new_alias] = [s, current_room]
				del self.__alias_to_sock[old_alias]
				self.__sock_to_alias[s] = new_alias

				## update room_to_alias
				self.__room_to_alias[current_room].remove(old_alias)
				self.__room_to_alias[current_room].add(new_alias)

				try:
					## update owner_to_room
					room = self.__owner_to_room[old_alias]
					del self.__owner_to_room[old_alias]
					self.__owner_to_room[new_alias] = room

					## update room_to_owner
					self.__room_to_owner[room] = new_alias
				except KeyError:
					pass

				## update room_blk_list
				## O(n), not optimized becoz no reversed dictionary look up
				for room in self.__room_blk_list:
					if old_alias in self.__room_blk_list[room]:
						self.__room_blk_list[room].remove(old_alias)
						self.__room_blk_list[room].add(new_alias)

			d["success"] = "true"

		else:
			d["success"] = "false"
			d["reason"] = "The alias has been used!"

		return d


	def join(self, d):
		"""
		wrapper to _join

		:param d: the data dictionary
		:return:
		"""

		return self.__join(d)

	## /join
	def __join(self, d):
		"""
		join a user to the target chatroom

		:param d: the the data dictionary
		:return: the updated dictionary
		"""

		tgt_room = d["body"]
		alias = d["usr"]

		## the two following condition are mutually exclusive.
		## if a room DNE, then no user can be blocked from that room.
		if tgt_room not in self.__room_to_owner:
			d["success"] = "false"
			d["reason"] = "The room does not exist!"

		elif alias in self.__room_blk_list[tgt_room]:
			d["success"] = "false"
			d["reason"] = "You are blocked!"

		else:
				curr_room = self.__alias_to_sock[alias][1]
				self.__move(alias, curr_room, tgt_room)
				d["success"] = "true"

		return d


	def __move(self, usr, old_room, new_room):
		"""
		move a user from the old room to the new room
		this method is to be called within the class therefore no wrapper

		:param usr: the user alias
		:param old_room: the current chatroom
		:param new_room: the chatroom to join
		:return: void
		"""

		if old_room == new_room:
			return

		soc = self.__alias_to_sock[usr][0]
		self.__room_to_alias[new_room].add(usr)
		try:
			self.__room_to_alias[old_room].remove(usr)
		except KeyError:
			pass
		self.__alias_to_sock[usr] = [soc, new_room]


	def create(self, d):
		"""
		wrapper to _create

		:param d: the data dictionary
		:return:
		"""

		return self.__create(d)

	## /create
	def __create(self, d):
		"""
		create a new chatroom

		:param d: the data dictionary
		:return: the updated dictionary
		"""

		new_room = d["body"]
		alias = d["usr"]

		if new_room in self.__room_to_owner or alias in self.__owner_to_room:
			d["success"] = "false"

		else:
			self.__room_to_owner[new_room] = alias
			self.__owner_to_room[alias] = new_room

			self.__room_to_alias[new_room] = set()

			self.__room_blk_list[new_room] = set()

			d["success"] = "true"

		return d


	def block(self, d):
		"""
		the wrapper to _block

		:param d: the data dictionary
		:return:
		"""

		return self.__block(d)

	## /block
	def __block(self, d):
		"""
		block a user from a chatroom, and the user will be moved to the general chatroom

		:param d: the data dictionary
		:return: the updated dictionary
		"""

		tgt_alias = d["body"]
		alias = d["usr"]

		## if the user is not any room owners, or the blocked user alias DNE, then false
		if alias not in self.__owner_to_room or tgt_alias not in self.__alias_to_sock:
			d["success"] = "false"

		else:
			room = self.__owner_to_room[alias]
			self.__room_blk_list[room].add(tgt_alias)
			self.__move(tgt_alias, room, "general")
			d["success"] = "true"

		return d


	def unblock(self, d):
		"""
		the wrapper to _unblock

		:param d: the data dictionary
		:return:
		"""

		return self.__unblock(d)

	## /unblock
	def __unblock(self, d):
		"""
		unblock a user from the chatroom

		:param d: the the data dictionary
		:return: the updated dictionary
		"""

		tgt_alias = d["body"]
		alias = d["usr"]

		if alias not in self.__owner_to_room or tgt_alias not in self.__alias_to_sock:
			d["success"] = "false"

		else:
			room = self.__owner_to_room[alias]
			if tgt_alias in self.__room_blk_list[room]:
				self.__room_blk_list[room].remove(tgt_alias)
				d["success"] = "true"

		return d


	def delete(self, d):
		"""
		wrapper to _Delete

		:param d: the data dictionary
		:return:
		"""

		return self.__delete(d)

	## /delete
	def __delete(self, d):
		"""
		a user tries to delete a chatroom

		:param d: the data dictionary
		:return: the updated dictionary
		"""

		alias = d["usr"]
		tgt_room = d["body"]

		if alias not in self.__owner_to_room or tgt_room not in self.__room_to_owner:
			d["success"] = "false"

		else:
			room = self.__owner_to_room[alias]
			assert(room == tgt_room)
			alive_clients = self.__room_to_alias[room]

			##
			while len(alive_clients) > 0:
				client = alive_clients.pop()
				self.__move(client, room, "general")

			del self.__room_to_alias[room]
			del self.__room_blk_list[room]
			del self.__owner_to_room[alias]
			del self.__room_to_owner[room]

			d["success"] = "true"

		return d


	## /lsroom
	def lsroom(self, d):
		"""
		list all chatrooms on the server

		:param d: the the data dictionary
		:return: the updated dictionary
		"""

		try:
			d["rooms"] = list(self.__room_to_alias.keys())
			d["success"] = "true"
		except:
			d["success"] = "false"

		return d


	## /lsusr
	def lsusr(self, d):
		"""
		list all users and the rooms they are in

		:param d: the the data dictionary
		:return: the updated dictionary
		"""

		try:
			d["live_users"] = [ (a, v[1]) for a, v in self.__alias_to_sock.items() ]
			d["success"] = "true"
		except:
			d["success"] = "false"

		return d


	def notify_usr(self, d):
		"""
		wrapper to __notify_usr

		:param d: the data dictionary
		:return: the dictionary to be sent, and the target socket
		"""

		return self.__notify_usr(d)

	def __notify_usr(self, d):
		"""
		notify the users of the action

		:param d: the data dictionary
		:return: the dictionary to be sent, and the target socket
		"""

		verb = d["verb"]

		if verb == "/create":
			new_response = {"usr":"Server", "verb":"/say", "body":"[{}] has created [{}]".format(d["usr"], d["body"])}
			tgt = [s for s, a in self.__sock_to_alias.items() if a != d["usr"]]
		elif verb == "/join":
			new_response = {"usr": "Server", "verb": "/say", "body": "[{}] has joined [{}]".format(d["usr"], d["body"])}
			tgt = [self.__alias_to_sock[alias][0] for alias in self.__room_to_alias[d["body"]] if alias != d["usr"]]
		elif verb == "/block":
			new_response = {"usr": "Server", "verb": "/say",
							"body": "You are blocked by [{}] from [{}]".format(d["usr"], self.__owner_to_room[d["usr"]])}
			tgt = self.__alias_to_sock[d["body"]][0]
		elif verb == "/unblock":
			new_response = {"usr": "Server", "verb": "/say",
							"body": "You are unblocked by [{}] from [{}]".format(d["usr"], self.__owner_to_room[
								d["usr"]])}
			tgt = self.__alias_to_sock[d["body"]][0]
		elif verb == "/delete":
			new_response = {"usr": "Server", "verb": "/say",
							"body": "room [{}] was deleted by [{}]".format(d["body"], d["usr"])}
			tgt = [s for s, a in self.__sock_to_alias.items() if a != d["usr"]]
		else:
			## for expansion
			response, tgt = "", {}

		return new_response, tgt