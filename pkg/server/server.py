import json
import logging
import select
import socket
import sys

from pkg.server.ServerInfoExpert import ServerInfoExpert
from ..CommunicationHandler.CommunicationHandler import ServerCommunicationHandler


class Server:
	def __init__(self, host = socket.gethostname(), port = 8888, log = True):
		"""
		default constructor

		:param host: default as local machine
		:param port: default 8888
		"""

		logging.basicConfig(level = logging.DEBUG, format = '%(message)s')

		self.log_flag = log

		self.server_info = ServerInfoExpert()

		# self.s = socket.socket()
		# self.s.setblocking(False)
		# ## https://stackoverflow.com/questions/29217502/socket-error-address-already-in-use
		# self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# self.s.bind((host, port))
		# self.s.listen(5)
		#
		# self.connections = [self.s]

		self.comm_hdl = ServerCommunicationHandler(host, port)

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
		"""
		the loop keeps listening to all the connected clients, and operates based on the verbs

		:return:
		"""
		try:
			while True:

				#rlist, wlist, xlist = select.select(self.connections, [], [])

				rlist, wlist, xlist = self.comm_hdl.get_response()

				for s in rlist:

					## new client connection
					#if s == self.s:
					if s == self.comm_hdl.get_self_sock():
						#sock, *_ = self.s.accept()
						_ = self.comm_hdl.accept_new_conn()
						#logging.info("{} has connected!\n".format(sock.getpeername()))
						logging.info("{} has connected!\n".format(_))
						#self.connections.append(sock)

					## clients inbound traffic
					else:
						# TODO: need to make sure the client does not send a json longer than 4096!
						#data = s.recv(4096).decode("utf-8")
						d = self.comm_hdl.receive(s)
						if self.log_flag: logging.info("DEBUG - received data: " + repr(d))
						## if the client calls socket.close(), the server will receive a empty string
						if data:
							#d = json.loads(data, encoding = "utf-8")

							## according to the verb, respond accordingly
							verb = d["verb"]

							response = {}

							if verb == "/say":
								response, s = self.server_info.broadcast(d)
							elif verb == "/set_alias":
								response = self.server_info.set_alias(d, s)
							elif verb == "/join":
								response = self.server_info.join(d)
							elif verb == "/create":
								response = self.server_info.create(d)
							elif verb == "/block":
								response = self.server_info.block(d)
							elif verb == "/unblock":
								response = self.server_info.unblock(d)
							elif verb == "/delete":
								response = self.server_info.delete(d)
							elif verb == "/lsroom":
								response = self.server_info.lsroom(d)
							elif verb == "/lsusr":
								response = self.server_info.lsusr(d)

							## server returns the response back to the sender
							self.comm_hdl.send(response, s)

							## if the response is successful, then notify the associated users
							if response["success"] == "true":
								self.notify(response)

							if self.log_flag: self.server_logging()

						## client Ctrl-C
						else:
							logging.info("{} has logged off.\n".format(s.getpeername()))

							try:
								self.server_info.remove_client(s)

							## if the client Ctrl-C when entering the alias at login, the server will have no record of the client
							except KeyError:
								pass

							finally:
								#self.connections.remove(s)
								self.comm_hdl.remove_sock(s)
								#s.close()
								self.comm_hdl.close(s)

		except KeyboardInterrupt:
			# Ctrl-C to quit
			#for s in self.connections: s.close()
			self.comm_hdl.close_all()
			logging.info("Shutdown the server...")
			sys.exit(0)

	def notify(self, d):
		"""
		notify the associated clients with the actions

		:param d: the data dictionary
		:return:
		"""
		verb = d["verb"]
		if verb in ["/join", "/create", "/block", "/unblock", "/delete"]:
			self.comm_hdl.send(*self.server_info.notify_usr(d))


	# def send(self, d, s):
	# 	"""
	# 	send dictionary the to target socket or a list of sockets
	#
	# 	:param d:
	# 	:param s:
	# 	:return:
	# 	"""
	#
	# 	data = bytes(json.dumps(d), "utf-8")
	#
	# 	try:
	# 		for sock in s:
	# 			self.__send(data, sock)
	#
	# 	except TypeError:
	# 		self.__send(data, s)
	#
	# @staticmethod
	# def __send(d, s):
	# 	s.send(d)


if __name__ == "__main__":
	server = Server()
	server.run_forever()