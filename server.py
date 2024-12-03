from datetime import datetime
import socket
import threading
import hashlib
import pytz
import json

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

def getTime():
    # Define the timezone for PST
    pst_timezone = pytz.timezone("America/Los_Angeles")

    # Get the current time in PST
    current_pst_time = datetime.now(pst_timezone)

    # Display the result
    return current_pst_time.strftime("%Y-%m-%d %H:%M:%S")

def add_user(user_name, password, cpu_info, disk_info, ram_info):
    try:
        with open('info.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    user_data = {
        "user_name": user_name,
        "password": password,
        "cpu_info": cpu_info,
        "disk_info": disk_info
        "ram_info": ram_info
    }

    data[user_name] = user_data

    with open('info.json', 'w') as file:
        json.dump(data, file, indent=4)

    print(f"Data added for {user_name}\n")

def view_all_user_data():
    try:
        with open('info.json', 'r'):
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    if not data:
        print("{ERROR} NO USER DATA FOUND")
        return

    for user, details in data.items():
        print(f"User: {user}")
        for key, value in details.items():
            print(f"    {key}: {value}")
        print() # Newline for readability

def delete_user(user_name):
    try:
        with open('info.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("No User Data Found")
        return

    if user_name in data:
        del data[user_name]
        with open('info.json', 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Deleted User_Data for: {user_name}")
    else:
        print(f"No Info Found For {user_name}")
    
def shutdown_server():
    global server_running
    while True:
        command = input()
        if command == SHUTDOWN_MESSAGE:
            server_running = False
            server.close()
            print("[SHUTDOWN] Server is shutting down...")
            break

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


            if f"{ID_CODE}CPU ID:" in msg:
                print(f"[{addr}] CPU ID RECEIVED: {msg.split('CPU ID: ')[1]}")
                conn.send("CPU INFO RECEIVED".encode(FORMAT))

            elif f"{ID_CODE}Disk Serial Number:" in msg:
                print(f"[{addr}] DISK SERIAL NUMBER RECEIVED: {msg.split('Disk Serial Number: ')[1]}")
                conn.send("DISK INFO RECEIVED".encode(FORMAT))

            elif f"{ID_CODE}RAM ID:" in msg:
                print(f"[{addr}] RAM ID RECEIVED: {msg.split('RAM ID: ')[1]}")
                conn.send("RAM INFO RECEIVED".encode(FORMAT))
                
            else:
                print(f"[{addr}] {msg}")
                conn.send(f"MSG received. MSG: {msg}".encode(FORMAT))


    conn.close()

def start():
    print("[STARTING] server is starting...")
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


verifyHash()
threading.Thread(target=start).start()
threading.Thread(target=shutdown_server).start()
