import json

class ClientInputParser:

	def __init__(self):
		pass

	def parse(self, usr, input_str):
		'''
		parse the user input

		:return: the parsed json object
		'''
		dictionary = {"status": 1, "usr":usr}

		# enter empty string
		if input_str == "":
			dictionary.update({"verb":""})
			dictionary.update({"body":""})
			dictionary["status"] = -1
			return dictionary

		# non-empty string
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

# some tests
if __name__ == "__main__":

	p = ClientInputParser()
	print(p.parse("will","test # 1"))
	p = ClientInputParser()
	print(p.parse("will","/join room1"))
	p = ClientInputParser()
	print(p.parse("will","/create room1"))
	p = ClientInputParser()
	print(p.parse("will","/set_alias WILL"))
	p = ClientInputParser()
	print(p.parse("will","/block bob"))
	p = ClientInputParser()
	print(p.parse("will","/unblock bob"))
	p = ClientInputParser()
	print(p.parse("will","/delete room1"))
	p = ClientInputParser()
	print(p.parse("will","/DNE_CMD whatever"))
	p = ClientInputParser()
	print(p.parse("will",""))
	p = ClientInputParser()
	print(p.parse("will","/join"))