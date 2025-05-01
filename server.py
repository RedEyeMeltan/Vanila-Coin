import socket
import threading
import hashlib
import pytz
import json
import mysql.connector
import blake3
import smtplib
import pandas as pd
from mysql.connector import Error
from datetime import datetime
from functions import *
from random_word import RandomWords

# ALL CONST VAR GO HERE
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
VERIFY_HASH = 'test'
SINGLE_TEST = "4878ca0425c739fa427f7eda20fe845f6b2e46ba5fe2a14df5b1e32f50603215"
DOUBLE_TEST = "55beb65d3293549b07cf215978375cf674d82de8657775da6c0f697b4e6b5e0b"
TRIPLE_TEST = "1af8e96926a936cce32a1e304a068a3379968fd28c0843dcb08186adfaba1441"

# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Word list setup
r = RandomWords()

# SQL setup
mycursor = mydb.cursor()

def singleHash(content):
    singleHash = blake3.blake3(f"{content}".encode('utf-8')).hexdigest()
    return str(singleHash)
    
def doubleHash(content):
    singleHash = blake3.blake3(f"{content}".encode('utf-8')).hexdigest()
    doubleHash = blake3.blake3(f"{singleHash}".encode('utf-8')).hexdigest()
    return str(doubleHash)

def tripleHash(content):
    singleHash = blake3.blake3(f"{content}".encode('utf-8')).hexdigest()
    doubleHash = blake3.blake3(f"{singleHash}".encode('utf-8')).hexdigest()
    tripleHash = blake3.blake3(f"{doubleHash}".encode('utf-8')).hexdigest()
    return str(tripleHash)

# Verifys hash using: "single_hash", "double_hash", "triple_hash"
def verifyHash():
    singleHash(VERIFY_HASH)
    doubleHash(VERIFY_HASH)
    tripleHash(VERIFY_HASH)
    
    if singleHash() == SINGLE_TEST:
        print("{HASH TEST} Single hash working.\n")
    else:
        print("{ERROR!!!} SINGLE HASH TEST FAILED.\n")
    
    if doubleHash() == DOUBLE_TEST:
        print("{HASH TEST} Double hash working.\n")
    else:
        print("{ERROR!!!} DOUBLE HASH TEST FAILED.\n")
    
    if tripleHash() == TRIPLE_TEST:
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

def delete_user(user_name, password):
    sqlWhereUserName = f"SELECT * FROM customer_info WHERE user_name = %s"
    mycursor.execute(sqlWhereUserName, user_name)
    UserNameWhere = mycursor.fetchall()

    sqlWherePassword = f"SELECT * FROM customer_info WHERE password = %s"
    pswrd = doubleHash(password)
    mycursor.execute(sqlWherePassword, pswrd)
    UserWherePassword = mycursor.fetchall()

    if UserNameResult == UserWherePassword:
        sqlDeleteUser = "DELETE WHERE username = %s"
        mycursor.execute(sqlDeleteUser, user_name)
        mydb.commit()
        print(mycursor.rowcount, "user deleted")

# Func to reset password
def reset_pswrd(old_pswrd, new_pswrd):
    sqlResetPassword = "UPDATE customer_info SET password = %s WHERE address = %s"
    valResetPassword = (doubleHash(new_pswrd), doubleHash(old_pswrd))

    mycursor.execute(sqlResetPassword, valResetPassword)
    mydb.commit()

    print(mycursor.rowcount, "password(s) affected/changed")

# Func to turn array into string
def array_to_string(arry):
    return ','.join([str(element) for element in arry])

# Will shutdown server if "SHUTDOWN MESSAGE" is typed in terminal
def shutdown_server():
    global server_running
    while True:
        command = input()
        if command == SHUTDOWN_MESSAGE:
            server_running = False
            server.close()
            print("[SHUTDOWN] Server is shutting down...")
            break

# Func to handle a single client. When dealing with more then one client the "threading" module will be used
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

# Start up the server and the neccesary functions with this func
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

# Create table
mycursor.execute("CREATE TABLE customer_info (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(256), password VARCHAR(256), cpu_id VARCHAR(256), ram_id VARCHAR(256), motherboard_id VARCHAR(256), time_acount_created VARCHAR(256), word_list VARCHAR(1024))")

# Template for adding info to table
customerInfoAdd = "INSERT INTO customer_info (username, password, cpu_id, ram_id, motherboard_id, time_acount_created, word_list) VALUES (%s, %s, %s, %s, %s, %s, %s)"

# Function for adding customer info to database. NOTES: in DB username is not hashed and password is double hashed
def Add_User(username, password, cpu_id, ram_id, motherboard_id, time_acount_created):
    # Template for adding info to table
    customerInfoAdd = "INSERT INTO customer_info (username, password, cpu_id, ram_id, motherboard_id, time_acount_created, word_list) VALUES (%s, %s, %s, %s, %s, %s, %s)"

    val = (f"{username}", f"{doubleHash(password)}", f"{singleHash(cpu_id)}", f"{singleHash(ram_id)}", f"{singleHash(motherboard_id)}", f"{getTime()}", f"{array_to_string(hashWordSecurity(wordSecurityList))}")
    mycursor.execute(customerInfoAdd, val)

    # Won't excute without "mydb.commit()"
    mydb.commit()
    print(f"Added user: {username} to database. ID: {mycursor.lastrowid}") # Reminder: add ID as an f bracket

# Checks if a list contains any duplicate elements.
def hasDuplicates(arr):
    return len(arr) != len(set(arr))

# Generates 20 random words for added login security. NOTE: this function should be excuted before using "AddCustomerInfo" func because wordlist should be in DB
def wordSecurity():
    global wordSecurityList, testWordList
    wordSecurityList = []
    testWordList = []
    wordListCount = 0
    while wordListCount < 21:
        testWord = r.get_random_word()
        if len(testWord) <= 6:
          testWordList.append(testWord)
          if not hasDuplicates(testWordList):
              currentWord = testWord
              wordSecurityList.append(currentWord)
              wordListCount += 1
          else:
              testWordList = testWordList[:-1]
              testWord = r.get_random_word()
              testWordList.append(testWord)
              currentWord = testWord
              wordSecurityList.append(currentWord)
              wordListCount += 1

# Uses "singleHash" func to hash a wordlist in the form of a array
def hashWordSecurity(arr):
  for i in range(len(arr)):
    arr[i] = singleHash(arr[i])
  return arr

def checkWordList(userName, pswrd):
    global wordListMatch
    checkWordList = []
    forLoopLength = 20
    
    for i in range(forLoopLength):
        user_input = input(f"Enter word {i+1}: ")
        checkWordList.append(user_input)

    checkWordList = hashWordSecurity(checkWordList)
    
    sqlWhereUserName = f"SELECT * FROM customer_info WHERE user_name = %s"
    mycursor.execute(sqlWhereUserName, userName)
    UserNameResult = mycursor.fetchall()

    sqlWherePassword = f"SELECT * FROM customer_info WHERE password = %s"
    pswrd = doubleHash(pswrd)
    mycursor.execute(sqlWherePassword, pswrd)
    PasswordResult = mycursor.fetchall()

    sqlWhereWordlist = f"SELECT * FROM customer_info WHERE word_list = %s"
    mycursor.execute(sqlWhereWordlist, checkWordList)
    WordlistResult = mycursor.fetchall()

    if UserNameResult == PasswordResult:
        infoMatch = True

    if infoMatch == True:
        if WordlistResult == checkWordList:
            WordlistMatch = True
            return True

def emailAuth(message, receiver, ):
    
        
                
# Actually run all the code here
verifyHash()x
threading.Thread(target=start).start()
threading.Thread(target=shutdown_server).start()
