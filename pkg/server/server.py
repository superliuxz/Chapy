import logging
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

				rlist, *_ = self.comm_hdl.get_response()

				for s in rlist:

					## new client connection
					if s == self.comm_hdl.get_self_sock():
						sock = self.comm_hdl.accept_new_conn()
						logging.info("{} has connected!\n".format(self.comm_hdl.get_sock_info(sock)))

					## clients inbound traffic
					else:
						# TODO: need to make sure the client does not send a json longer than 4096!
						d = self.comm_hdl.receive(s)
						if self.log_flag: logging.info("DEBUG - received data: " + repr(d))
						## if the client calls socket.close(), the server will receive a empty string
						if d:

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
							logging.info("{} has logged off.\n".format(self.comm_hdl.get_sock_info(s)))

							try:
								self.server_info.remove_client(s)

							## if the client Ctrl-C when entering the alias at login, the server will have no record of the client
							except KeyError:
								pass

							finally:
								self.comm_hdl.remove_sock(s)
								self.comm_hdl.close(s)

		except KeyboardInterrupt:
			## Ctrl-C to quit
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