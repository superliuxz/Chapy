import socket, sys, json, select, logging
from parser import Parser

class Client:

	def __init__(self, host = socket.gethostname(), port = 8888, log = True):

		logging.basicConfig(level = logging.INFO, format = '%(message)s')

		self.host = host
		self.port = port
		self.logging_flag = log
		self.alias = None
		self.s = socket.socket()
		self.input_list = [sys.stdin, self.s]

		try:
			self.s.connect((self.host, self.port))
		except:
			print('Unable to connect {}@{}'.format(self.host, self.port))
			sys.exit(1)

		self.alias = self._ask_for_alias()


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
			self._send_to_server({"verb": "/set_alias", "body": alias})

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
		msg = Parser.client_input(self.alias, input)
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
						data = s.recv(4096).decode("utf-8")

						if not data:
							print("\nDisconnected from the server")
							sys.exit(1)

						else:
							if self.logging_flag: logging.info("DEBUG - the msg from server {}".format(data))

							parsed_result = Parser.server_inbound(data)

							## Parser.server_inbound only returns when alias is changed
							if parsed_result:
								self.alias = parsed_result

					# from the keyboard
					else:
						msg = self._read_input()

						v = Parser.input_validator(msg)

						## Parse.input_validator only returns 1 when msg["status"] == 1
						if v == 1:
							self._send_to_server(msg)


		except KeyboardInterrupt:
			# Ctrl-C to quit
			self.s.close()
			sys.exit(0)


if __name__ == "__main__":
	u = Client(log = False)
	#print(u.alias)
	u.run_forever()