import socket, sys, json, select
from client_parser import ClientInputParser

class Client:
	def __init__(self, host = socket.gethostname(), port = 8888):
		self.host = host
		self.port = port
		self.alias = None
		self.s = socket.socket()
		self.input_list = [sys.stdin, self.s]

		try:
			self.s.connect((self.host, self.port))
		except:
			print('Unable to connect {}@{}'.format(self.host, self.port))
			sys.exit(1)

		self.alias = self._ask_for_alias()

		self.parser = ClientInputParser(self.alias)

	def _ask_for_alias(self):
		'''
		ask for the user to set the alias for the first time

		:return:
		'''
		while not self.alias:
			print("Please enter your alias:")
			alias = sys.stdin.readline().strip()
			if alias == "":
				continue
			## send initial message to set alias
			msg = json.dumps({"usr": "null", "verb": "/set_alias", "body": alias})
			self.s.send(bytes(msg, "utf-8"))
			## server returns the status of the request
			response = json.loads(self.s.recv(4096).decode("utf-8"))

			if response["success"] == "true":
				return alias
			else:
				print("The alias has been used!")



	@staticmethod
	def prompt():
		sys.stdout.write('Me: ')
		sys.stdout.flush()

	def _read_input(self):
		'''
		read the keyboard input then parse to a json object

		:return: the parsed json object
		'''
		input = sys.stdin.readline().strip()
		msg = self.parser.parse(input)
		return msg

	def _send_to_server(self, msg):
		'''
		send the json object to the server

		:param msg: the json object
		:return:
		'''
		data = json.dumps(msg)
		self.s.send(bytes(data, "utf-8"))

	def run_forever(self):
		'''
		the loop the keeps listening to both keyboard and the incoming traffic from the server

		:return:
		'''
		try:
			while True:
				self.prompt()

				rlist, wlist, xlist = select.select(self.input_list, [], [])

				for s in rlist:
					# from the server
					if s == self.s:
						# TODO: data should be recv'd as json objs, so need to convert them to nicely printables
						data = s.recv(4096)

						if not data:
							print("\nDisconnected from the server")
							sys.exit(1)
						else:
							# TODO: more logic will be added to respond to the response from the server
							print("\nthe msg recv'd from server {}".format(data))

					# from the keyboard
					else:
						msg = self._read_input()

						v = msg["status"]

						if v == -1:
							print("Please enter something!")
						elif v == -2:
							print("Your command {} is invalid".format(msg["verb"]))
						elif v == -3:
							print("No argument given after {}".format(msg["verb"]))
						elif v == 1:
							self._send_to_server(msg)

		except KeyboardInterrupt:
			# Ctrl-C to quit
			self.s.close()
			sys.exit(0)

if __name__ == "__main__":
	u = Client()
	#print(u.alias)
	u.run_forever()