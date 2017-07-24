from pkg.client.client import Client

if __name__ == "__main__":
	u = Client(log = False)
	u.run_forever()
