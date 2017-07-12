import socket, sys, json, select
from UserInputParser import UserInputParser

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

		while not self.alias:
			print("Please enter your alias:")
			tmp = sys.stdin.readline().strip()
			## send initial message to set alias
			msg = json.dumps({"usr": "null", "verb": "/set_alias", "body": tmp.strip()})
			self.s.send(bytes(msg, "utf-8"))
			## server returns the status of the request
			success = self.s.recv(4096).decode("utf-8")

			if success == "T":
				self.alias = tmp
			else:
				print("The alias has been used!")

			self.parser = UserInputParser(self.alias)

	@staticmethod
	def prompt():
		sys.stdout.write('Me: ')
		sys.stdout.flush()

	def _read_input(self):
		input = sys.stdin.readline().strip()
		msg = self.parser.parse(input)
		return msg

	def _send_to_server(self, msg):
		self.s.send(bytes(msg, "utf-8"))

	def run_forever(self):
		while True:

			read_list, *_ = select.select(self.input_list, [], [])

			for s in read_list:
				# from the server
				if s == self.s:
					# TODO: data should be recv'd as json objs, so need to convert them
					data = s.recv(4096)
					if not data:
						print("\nDisconnected from the server")
						sys.exit(1)
					else:
						print(data)
						self.prompt()

				# from the keyboard
				else:
					msg = self._read_input()
					self._send_to_server(msg)
					self.prompt()



if __name__ == "__main__":
	u = Client()
	#print(u.alias)
	Client.prompt()
	u.run_forever()