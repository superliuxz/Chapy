import json

class UserInputParser:

	def __init__(self, usr_alias, input_str):
		'''
		constructor

		:param usr_alias: the alias of the user
		:param input_str: the user input from stdin
		'''
		self.usr = usr_alias
		self.input = input_str

	def parse(self):
		'''
		parse the user input

		:return: the parsed json object
		'''
		dictionary = {"validity": 1, "usr":self.usr}
		parsed_json = ""
		if self.input[0] == "/":
			## commands
			actions = ["/join", "/create", "/set_alias", "/block", "/unblock", "/delete"]
			verb, body = self.input.split()
			if verb in actions:
				dictionary["verb"] = verb
				dictionary["body"] = body
			else:
				dictionary["validity"] = 0

		else:
			## message
			## the server should promote the user to type in the alias when 1st log in
			dictionary["verb"] = "say"
			dictionary["body"] = self.input

		parsed_json = json.dumps(dictionary)
		return parsed_json

# some tests
if __name__ == "__main__":

	p = UserInputParser("will", "test # 1")
	print(p.parse())
	p = UserInputParser("will", "/join room1")
	print(p.parse())
	p = UserInputParser("will", "/create room1")
	print(p.parse())
	p = UserInputParser("will", "/set_alias WILL")
	print(p.parse())
	p = UserInputParser("will", "/block bob")
	print(p.parse())
	p = UserInputParser("will", "/unblock bob")
	print(p.parse())
	p = UserInputParser("will", "/delete room1")
	print(p.parse())
	p = UserInputParser("will", "/DNE_CMD whatever")
	print(p.parse())