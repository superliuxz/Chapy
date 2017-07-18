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

		if input_str[0] == "/":
			## commands
			actions = ["/join", "/create", "/set_alias", "/block", "/unblock", "/delete"]
			try:
				verb, body = input_str.split()
			except ValueError:
				verb = input_str.split()[0]
				body = ""

			dictionary["verb"] = verb
			dictionary["body"] = body

			## invalid command
			if verb not in actions:
				dictionary["status"] = -2

			## no argument after command
			if body == "":
				dictionary["status"] = -3


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