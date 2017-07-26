import tabulate

class Parser:

	def client_input(self, usr, input_str):
		return self.__client_input(usr, input_str)

	@staticmethod
	def __client_input(usr, input_str):
		"""
		parse the client input (stdin)

		:param usr: alias of the client
		:param input_str: the input raw string
		:return: the parsed dictionary(json)
		"""
		dictionary = {"status": 1, "usr":usr}

		## enter empty string
		if input_str == "":
			dictionary.update({"verb":""})
			dictionary.update({"body":""})
			dictionary["status"] = -1
			return dictionary

		## non-empty string
		if input_str[0] == "/":

			## commands
			verbs = ["/join", "/create", "/set_alias", "/block", "/unblock", "/delete", "/help", "/lsroom", "/lsusr"]

			try:
				verb, body = input_str.split()

			## value error means that only the verb is present from the user input: /help, /lsroom and /lsusr
			except ValueError:

				verb = input_str.split()[0]

				if verb == "/help":

					body = "\n/join $chatroom: join a chatroom\n" \
						   "/set_alias $alias: set an alias\n" \
						   "/create $chatroom: create a chatroom\n" \
						   "/block $alias: block a user\n" \
						   "/unblock $alias: unblock a user\n" \
						   "/delete $chatroom: delete a chatroom\n" \
						   "/help: display help message\n"

					dictionary["status"] = 0

				else:
					body = ""

					if verb != "/lsroom" and verb != "/lsusr":
						## valid command but no arguments given
						dictionary["status"] = -3

			dictionary["verb"] = verb
			dictionary["body"] = body

			## invalid command
			if verb not in verbs:
				dictionary["status"] = -2

		else:
			## message
			dictionary["verb"] = "/say"
			dictionary["body"] = input_str

		return dictionary


	def server_inbound(self, data):
		return self.__server_inbound(data)

	@staticmethod
	def __server_inbound(d):
		"""
		parse server inbound message

		:param d: raw server inbound data
		:return: new alias if /set_alias is successful
		"""

		if d["verb"] == "/say":
			print("[{}]: {}".format(d["usr"], d["body"]))

		else:
			if d["success"] == "true":

				if d["verb"] == "/set_alias":
					print("[Server]: Your alias has been set to {}".format(d["body"]))
					return d["body"]

				elif d["verb"] == "/create":
					print("[Server]: {} is created!".format(d["body"]))

				elif d["verb"] == "/join":
					print("[Server]: You have joined room {}".format(d["body"]))

				elif d["verb"] == "/block":
					print("[Server]: You have blocked {}".format(d["body"]))

				elif d["verb"] == "/unblock":
					print("[Server]: You have unblocked {}".format(d["body"]))

				elif d["verb"] == "/delete":
					print("[Server]: You have deleted room {}".format(d["body"]))

				elif d["verb"] == "/lsroom":
					rooms = d["rooms"]
					print("\n[Server]: Available rooms: {}".format(len(rooms)))
					print(tabulate.tabulate([[_] for _ in rooms],
											headers = ['Chatroom'],
											tablefmt = 'orgtbl'))
					print()

				elif d["verb"] == "/lsusr":
					lu = d["live_users"]
					print("\n[Server]: Alive users: {}".format(len(lu)))
					print(tabulate.tabulate([[_[0], _[1]] for _ in lu],
											headers = ['Alias', 'Chatroom'],
											tablefmt = 'orgtbl'))
					print()

			else:
				## TODO: add failed reason?
				print("[Server]: {} operation failed! Reason: {}".format(d["verb"], d["reason"]))


	def input_validator(self, msg):
		return self.__input_validator(msg)

	@staticmethod
	def __input_validator(msg):
		"""
		validate the parsed user input

		:param msg: parsed user input
		:return: status if status == 1
		"""

		status = msg["status"]

		if status == 1:
			return status
		elif status == 0:
			print(msg["body"])
		elif status == -1:
			print("Please enter something!")
		elif status == -2:
			print("Your command {} is invalid".format(msg["verb"]))
		elif status == -3:
			print("No argument given after {}".format(msg["verb"]))


# some tests
if __name__ == "__main__":

	p = Parser()

	print(p.client_input("will","test # 1"))
	print(p.client_input("will","/join room1"))
	print(p.client_input("will","/create room1"))
	print(p.client_input("will","/set_alias WILL"))
	print(p.client_input("will","/block bob"))
	print(p.client_input("will","/unblock bob"))
	print(p.client_input("will","/delete room1"))
	print(p.client_input("will","/DNE_CMD whatever"))
	print(p.client_input("will",""))
	print(p.client_input("will","/join"))