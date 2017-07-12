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
		dictionary = {"validity": 1, "usr":self.usr}
		parsed_json = ""
		if input_str[0] == "/":
			## commands
			actions = ["/join", "/create", "/set_alias", "/block", "/unblock", "/delete"]
			verb, body = input_str.split()
			if verb in actions:
				dictionary["verb"] = verb
				dictionary["body"] = body
			else:
				dictionary["validity"] = 0

		else:
			## message
			## the server should promote the user to type in the alias when 1st log in
			dictionary["verb"] = "say"
			dictionary["body"] = input_str

		parsed_json = json.dumps(dictionary)
		return parsed_json

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