import socket, sys, json, select, logging
from ServerInfoExpert import ServerInfoExpert

class Server:
	def __init__(self, host = socket.gethostname(), port = 8888, log = True):
		'''
		default constructor

		:param host: default as local machine
		:param port: default 8888
		'''

		logging.basicConfig(level = logging.DEBUG, format = '%(message)s')

		self.log_flag = log

		self.server_info = ServerInfoExpert()

		self.s = socket.socket()
		self.s.setblocking(False)
		## https://stackoverflow.com/questions/29217502/socket-error-address-already-in-use
		self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.s.bind((host, port))
		self.s.listen(5)

		self.connections = [self.s]

		logging.info("Sever has started!\n")

	def server_logging(self):

		logging.info("DEBUG - alias_to_sock: {}\n" 
					 "DEBUG - sock_to_alias: {}\n"
					 "DEBUG - room_to_alias: {}\n"
					 "DEBUG - owner_to_room: {}\n"
					 "DEBUG - room_to_owner: {}\n"
					 "DEBUG - room_blk_list: {}\n"
					 .format(*self.server_info.getter())
					 )


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
						logging.info("{} has connected!\n".format(sock.getpeername()))
						self.connections.append(sock)

					# clients inbound traffic
					else:
						# TODO: need to make sure the client does not send a json longer than 4096!
						data = s.recv(4096).decode("utf-8")
						if self.log_flag: logging.info("DEBUG - received data: " + data)
						# if the client calls socket.close(), the server will receive a empty string
						if data:
							d = json.loads(data, encoding = "utf-8")

							# according to the verb, respond accordingly
							verb = d["verb"]
							# TODO: factorize the following into a dedicated class, and use composition
							if verb == "/say":
								self.server_info.broadcast(d)
							elif verb == "/set_alias":
								# TODO: set_alias also needs to update those ones in the owner list, blocked list etc.
								self.server_info.set_alias(d, s)
							elif verb == "/join":
								self.server_info.join(d, s)
							elif verb == "/create":
								self.server_info.create(d, s)
							elif verb == "/block":
								self.server_info.block(d, s)
							elif verb == "/unblock":
								self.server_info.unblock(d, s)
							elif verb == "/delete":
								self.server_info.delete(d, s)
							elif verb == "/lsroom":
								self.server_info.lsroom(d, s)
							elif verb == "/lsusr":
								self.server_info.lsusr(d, s)

							if self.log_flag: self.server_logging()

						# client Ctrl-C
						else:
							logging.info("{} has logged off.\n".format(s.getpeername()))
							self.server_info.remove_client(s)
							self.connections.remove(s)
							s.close()

		except KeyboardInterrupt:
			# Ctrl-C to quit
			for s in self.connections: s.close()
			logging.info("Shutdown the server...")
			sys.exit(0)


if __name__ == "__main__":
	server = Server()
	server.run_forever()