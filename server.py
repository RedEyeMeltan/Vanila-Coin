import socket
import threading
import hashlib

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"

# Hash test constants
verifyhash = 'test'
single_test = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
double_test = "7b3d979ca8330a94fa7e9e1b466d8b99e0bcdea1ec90596c0dcc8d7ef6b4300c"
triple_test = "5b24f7aa99f1e1da5698a4f91ae0f4b45651a1b625c61ed669dd25ff5b937972"

# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def singleHash(content):
    global single_hex_dig
    hash_object = hashlib.sha256(content.encode(FORMAT))
    single_hex_dig = hash_object.hexdigest()
    
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

def verifyHash():
    singleHash(verifyhash)
    doubleHash(verifyhash)
    tripleHash(verifyhash)
    
    if single_hex_dig == single_test:
        print("{HASH TEST} Single hash working.\n")
    else:
        print("{ERROR!!!} SINGLE HASH TEST FAILED.\n")
    
    if double_hex_dig == double_test:
        print("{HASH TEST} Double hash working.\n")
    else:
        print("{ERROR!!!} DOUBLE HASH TEST FAILED.\n")
    
    if triple_hex_dig == triple_test:
        print("{HASH TEST} Triple hash working.\n")
    else:
        print("{ERROR!!!} TRIPLE HASH TEST FAILED.\n")

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    connected = True
    
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            
            if msg == DISCONNECT_MESSAGE:
                connected = False
            
            print(f"[{addr}] {msg}")
            conn.send(f"MSG received. MSG: {msg}".encode(FORMAT))

            if msg.startswith("CPU ID"):
                break
            if msg.startswith("Motherboard Serial Number"):
                break
            if msg.startswith("Disk Serial Number"):
                break

    conn.close()

def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] server is starting...")
verifyHash()
start()
