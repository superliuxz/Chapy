import socket, sys, json

class User:
	def __init__(self, HOST = socket.gethostname(), IP = 5000):
		self.host = HOST
		self.ip = IP
		self.alias = None

		s = socket.socket()

		try:
			s.connect((self.host, self.ip))
		except:
			print('Unable to connect {}@{}'.format(self.host, self.ip))
			sys.exit()

		while not self.alias:
			print("Please enter your fucking alias:")
			tmp = sys.stdin.readline()
			## send initial message to set alias
			msg = json.dumps({"usr": "null", "verb": "/set_alias", "body": tmp.strip()})
			s.send(bytes(msg, "utf-8"))
			## server returns the status of the request
			success = s.recv(4096).decode("utf-8")

			if success == "T":
				self.alias = tmp
			else:
				print("The alias has been used!")

	@staticmethod
	def prompt():
		sys.stdout.write('Me: ')
		sys.stdout.flush()

if __name__ == "__main__":
	u = User()
	print(u.alias)
	User.prompt()