import socket, sys, json
from UserInputParser import UserInputParser

class User:
	def __init__(self, host = socket.gethostname(), ip = 5000):
		self.host = host
		self.ip = ip
		self.alias = None

		self.s = socket.socket()

		try:
			self.s.connect((self.host, self.ip))
		except:
			print('Unable to connect {}@{}'.format(self.host, self.ip))
			sys.exit()

		while not self.alias:
			print("Please enter your fucking alias:")
			tmp = sys.stdin.readline()
			## send initial message to set alias
			msg = json.dumps({"usr": "null", "verb": "/set_alias", "body": tmp.strip()})
			self.s.send(bytes(msg, "utf-8"))
			## server returns the status of the request
			success = s.recv(4096).decode("utf-8")

			if success == "T":
				self.alias = tmp
			else:
				print("The alias has been used!")

			self.parser = UserInputParser(self.alias)

	@staticmethod
	def prompt():
		sys.stdout.write('Me: ')
		sys.stdout.flush()

	def read_input(self):
		input = sys.stdin.readline().strip()
		msg = self.parser.parse(input)
		return msg

	def send_to_server(self, msg):
		self.s.send(msg)



if __name__ == "__main__":
	u = User()
	print(u.alias)
	User.prompt()