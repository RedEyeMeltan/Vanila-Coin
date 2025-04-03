from datetime import datetime
import socket
import threading
import hashlib
import pytz
import json
import mysql.connector
import blake3
from mysql.connector import Error
import pandas as pd
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
ID_CODE = "8e9acf8a6dd4ad6a5eed38bdd217a6e93d6b273ce74e886972c12dc58ceaea00"

# Hash test constants
verifyhash = 'test'
single_test = "4878ca0425c739fa427f7eda20fe845f6b2e46ba5fe2a14df5b1e32f50603215"
double_test = "55beb65d3293549b07cf215978375cf674d82de8657775da6c0f697b4e6b5e0b"
triple_test = "1af8e96926a936cce32a1e304a068a3379968fd28c0843dcb08186adfaba1441"

# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

def singleHash(content):
    singleHash = blake3(f"{content}".encode('utf-8')).hexdigest()
    return singleHash
    
def doubleHash(content):
    singleHash = blake3(f"{content}".encode('utf-8')).hexdigest()
    doubleHash = blake3(f"{singleHash}".encode('utf-8')).hexdigest()
    return doubleHash

def tripleHash(content):
    singleHash = blake3(f"{content}".encode('utf-8')).hexdigest()
    doubleHash = blake3(f"{singleHash}".encode('utf-8')).hexdigest()
    tripleHash = blake3(f"{doubleHash}".encode('utf-8')).hexdigest()
    return tripleHash

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

# Connect to database
mydb = mysql.connector.connect(
  host="localhost",
  user="yourusername",
  password="yourpassword"
)
mycursor = mydb.cursor()

# Create datebase
mycursor.execute("CREATE DATABASE mydatabase")

# Connect to database again
mydb = mysql.connector.connect(
  host="localhost",
  user="yourusername",
  password="yourpassword"
  database-"mydatabase"
)
mycursor = mydb.cursor()

# Create table
mycursor.execute("CREATE TABLE customer_info (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(256), password VARCHAR(256), cpu_id VARCHAR(256), ram_id VARCHAR(256), motherboard_id VARCHAR(256), time_acount_created VARCHAR(256))")

# Template for adding info to table
customerInfoAdd = "INSERT INTO customer_info (username, password, cpu_id, ram_id, motherboard_id, time_acount_created) VALUES (%s, %s, %s, %s, %s, %s)"

# Function for adding customer info to database
def AddCustomerInfo(username, password, cpu_id, ram_id, motherboard_id, time_acount_created):
    val = (f"{singleHash(username)}", f"{singleHash(password)}", f"{singleHash(cpu_id)}", f"{singleHash(ram_id)}", f"{singleHash(motherboard_id)}", f"{getTime()}")
    mycursor.execute(sql, val)

    # Won't excute without "mydb.commit()"
    mydb.commit()
    print("Added user to database")

# Actually run all the code here
verifyHash()
threading.Thread(target=start).start()
threading.Thread(target=shutdown_server).start()
