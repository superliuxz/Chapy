import socket, sys, json, select
from input_parser import ClientInputParser

class Client:
	def __init__(self, host = socket.gethostname(), port = 8888, debug = True):
		self.host = host
		self.port = port
		self.debug = debug
		self.alias = None
		self.s = socket.socket()
		self.input_list = [sys.stdin, self.s]

		try:
			self.s.connect((self.host, self.port))
		except:
			print('Unable to connect {}@{}'.format(self.host, self.port))
			sys.exit(1)

		self.alias = self._ask_for_alias()

		self.parser = ClientInputParser()

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
		msg = self.parser.parse(self.alias, input)
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
							if self.debug: print("\nDEBUG - the msg from server {}".format(data))

							d = json.loads(data, encoding="utf-8")

							# TODO: factorize the following into a class to handle the response from the server
							if d["verb"] == "/say":
								print("\n[{}]: {}".format(d["usr"], d["body"]))

							else:
								if d["success"] == "true":

									if d["verb"] == "/set_alias":
										print("\nYour alias has been set to {}".format(d["body"]))
										self.alias = d["body"]

									elif d["verb"] == "/create":
										print("\n{} is created!".format(d["body"]))

									elif d["verb"] == "/join":
										print("\nYou have joined room {}".format(d["body"]))

									elif d["verb"] == "/block":
										print("\nYou have blocked {}".format(d["body"]))

									elif d["verb"] == "/block":
										print("\nYou have unblocked {}".format(d["body"]))

									elif d["verb"] == "/delete":
										print("\nYou have deleted room {}".format(d["body"]))

									elif d["verb"] == "/lsroom":
										rooms = d["rooms"]
										print("\nAvailable rooms:")
										for r in rooms:
											print("\t" + r)

									elif d["verb"] == "/lsusr":
										print("\nAlive users:")
										for u in d["live_users"]:
											print("\t{} in {}".format(*u))

								else:
									## TODO: add failed reason?
									print("\n{} operation failed!".format(d["verb"]))

					# from the keyboard
					else:
						msg = self._read_input()

						## TODO: factorize the following logic into a module
						status = msg["status"]

						if status == 0:
							print(msg["body"])
						elif status == -1:
							print("Please enter something!")
						elif status == -2:
							print("Your command {} is invalid".format(msg["verb"]))
						elif status == -3:
							print("No argument given after {}".format(msg["verb"]))
						elif status == 1:
							self._send_to_server(msg)

		except KeyboardInterrupt:
			# Ctrl-C to quit
			self.s.close()
			sys.exit(0)

if __name__ == "__main__":
	u = Client(debug = False)
	#print(u.alias)
	u.run_forever()