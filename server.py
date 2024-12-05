from datetime import datetime
import socket
import threading
import hashlib
import pytz
import json
from functions import *

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SHUTDOWN_MESSAGE = "quit"
ENCODE_KEY = '@XM[2ui(#Y!ND1z[xq'
DECODE_KEY = '{+E%%)]XKSZ-w$SMS-'
ID_CODE = ":$z35$7LW$"

# Hash test constants
verifyhash = 'test'
single_test = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
double_test = "7b3d979ca8330a94fa7e9e1b466d8b99e0bcdea1ec90596c0dcc8d7ef6b4300c"
triple_test = "5b24f7aa99f1e1da5698a4f91ae0f4b45651a1b625c61ed669dd25ff5b937972"

# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Actually run all the code here
verifyHash()
threading.Thread(target=start).start()
threading.Thread(target=shutdown_server).start()
