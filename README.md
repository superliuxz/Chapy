# Python Chat Program
A centralized client-server chat program written in Python3, using `socket` and `select`.

Dependencies: `pip3 install -r requirements.txt` 

Usage: `python3 start_server.py` and `python3 start_client.py`. After entering the alias from the client terminal, do `/help` to list all the supported commands.

TODOs:

  * <del>need to fix the crash on python 3.5.2 & 3.3.2</del>
  * <del>stuff commented in the code</del>
  * <del>handle client disconnection when the user is promoted to enter the alias for the first time</del>
  * encryption
  * try:
    * `asyncio`
    * `multithreading` 
