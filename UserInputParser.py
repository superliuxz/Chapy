import json

class UserInputParser:

	def __init__(self, usr_alias):
		'''
		constructor

		:param usr_alias: the alias of the user
		:param input_str: the user input from stdin
		'''
		self.usr = usr_alias

	def parse(self, input_str):
		'''
		parse the user input

		:return: the parsed json object
		'''
		dictionary = {"status": 1, "usr":self.usr}

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

	p = UserInputParser("will")
	print(p.parse("test # 1"))
	p = UserInputParser("will")
	print(p.parse("/join room1"))
	p = UserInputParser("will")
	print(p.parse("/create room1"))
	p = UserInputParser("will", )
	print(p.parse("/set_alias WILL"))
	p = UserInputParser("will", )
	print(p.parse("/block bob"))
	p = UserInputParser("will", )
	print(p.parse("/unblock bob"))
	p = UserInputParser("will", )
	print(p.parse("/delete room1"))
	p = UserInputParser("will", )
	print(p.parse("/DNE_CMD whatever"))
	p = UserInputParser("will", )
	print(p.parse(""))
	p = UserInputParser("will", )
	print(p.parse("/join"))