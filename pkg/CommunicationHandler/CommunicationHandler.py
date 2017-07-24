import socket
import json
import sys
import select


class CommunicationHandler:
	"""
	base class
	"""
	def __init__(self):
		"""
		default constructor
		"""

		self.sock = socket.socket()
		self.sel_list = [self.sock]

	def get_self_sock(self):
		"""
		the getter that returns self.sock

		:return: self.sock. if client calls, return the socket to the server; if server calls, return the server socket
		"""

		return self.sock

	def send(self, dictionary):
		"""
		send the dictionary to self.sock

		:param dictionary: the data dictionary
		:return:
		"""

		data = bytes(json.dumps(dictionary), "utf-8")
		self.sock.send(data)

	def receive(self):
		"""
		receive the json through self.sock, and convert to dictionary

		:return: the loaded dictionary
		"""

		data = self.sock.recv(4096)

		return "" if not data else json.loads(data, encoding="utf-8")

	def close(self):
		"""
		close self.sock

		:return:
		"""

		self.sock.close()

	def get_response(self):
		"""
		monitoring the I/Os and pull them out when some are ready to R/W/E

		:return: three lists of I/Os that are ready to read, write or have exceptional behaviors
		"""

		return select.select(self.sel_list, [], [])


class ServerCommunicationHandler(CommunicationHandler):
	"""
	server side comm hdl class
	"""
	def __init__(self, host, port):
		"""
		initialize the server comm hdl

		:param host: the server address
		:param port: the port to listen
		"""

		super().__init__()

		self.sock.setblocking(False)
		## https://stackoverflow.com/questions/29217502/socket-error-address-already-in-use
		self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.sock.bind((host, port))
		self.sock.listen(5)

	@staticmethod
	def send(dictionary, s):
		"""
		overrides the method in base class
		it's a static method now, which sends the dictionary to the socket s

		:param dictionary: the data dictionary
		:param s: the socket to send through
		:return:
		"""

		data = bytes(json.dumps(dictionary), "utf-8")

		try:
			for sock in s:
				sock.send(data)

		except TypeError:
			s.send(data)

	@staticmethod
	def receive(s):
		"""
		overrides the method in base class
		it's a static method now, which receives 4096 bytes of data through s

		:param s: the socket to send through
		:return: empty string or loaded dictionary
		"""

		data = s.recv(4096)

		return "" if not data else json.loads(data, encoding="utf-8")

	@staticmethod
	def close(s):
		"""
		overrides the method in base class
		it's a static method now, which closes the connection

		:param s: the socket to close
		:return:
		"""

		s.close()

	def close_all(self):
		"""
		close all connection in self.sel_list
		used when shutdown the server

		:return:
		"""

		for sock in self.sel_list:
			sock.close()

	def add_sock(self, sock):
		"""
		add new socket to the list

		:param sock: the new socket
		:return:
		"""

		self.sel_list.append(sock)

	def remove_sock(self, sock):
		"""
		remove the socket from the list
		:param sock: the target socket
		:return:
		"""

		self.sel_list.remove(sock)

	def accept_new_conn(self):
		"""
		accept new connection request through the server socket
		:return: the ip address of client and port
		"""

		sock, addr = self.sock.accept()

		self.add_sock(sock)

		return sock.getpeername()

	@staticmethod
	def get_sock_info(s):
		"""
		get the connection of a socket

		:param s: the target socket
		:return: the conn info
		"""
		return s.getpeername()



class ClientCommunicationHandler(CommunicationHandler):
	"""
	the client side comm hdl
	"""
	def __init__(self, host, port):
		"""
		initialize the client comm hdl, and submit a connection request to the server

		:param host: server addr
		:param port: server port
		"""

		super().__init__()

		self.sel_list.append(sys.stdin)

		try:
			self.sock.connect((host, port))
		except ConnectionRefusedError or socket.gaierror:
			print('Unable to connect {}@{}'.format(host, port))
			sys.exit(1)