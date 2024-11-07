import socket
import wmi
import hashlib

w = wmi.WMI() # Initialize WMI object

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "172.24.96.1"
ADDR = (SERVER, PORT)

#  THE HASH IS TESTED WITH "test"
single_test = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
double_test = "7b3d979ca8330a94fa7e9e1b466d8b99e0bcdea1ec90596c0dcc8d7ef6b4300c"
triple_test = "5b24f7aa99f1e1da5698a4f91ae0f4b45651a1b625c61ed669dd25ff5b937972"


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def hash(content):
    global hex_dig
    hash_object = hashlib.sha256(content.encode(FORMAT))
    hex_dig = hash_object.hexdigest()
    

def doubleHash(content):
    global double_hex_dig
    hash_object = hashlib.sha256(content.encode(FORMAT))
    double_hash_object = hashlib.sha256(hash_object.hexdigest().encode(FORMAT))
    double_hex_dig = double_hash_object.hexdigest()

def tripleHash(content):
    global triple_hex_dig
    hash_object = hashlib.sha256(content.encode(FORMAT))
    double_hash_object = hashlib.sha256(hash_object.hexdigest().encode(FORMAT))
    triple_hash_object = hashlib.sha256(double_hash_object.hexdigest().encode(FORMAT))
    triple_hex_dig = triple_hash_object.hexdigest()

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048))

send("hi")
send(DISCONNECT_MESSAGE)
