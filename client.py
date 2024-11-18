import socket
import wmi
import hashlib

w = wmi.WMI() # Initialize WMI object

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.56.1"
ADDR = (SERVER, PORT)
ID_CODE = ":$z35$7LW$"

#  THE HASH IS TESTED WITH "test"
verifyhash = 'test'
single_test = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
double_test = "7b3d979ca8330a94fa7e9e1b466d8b99e0bcdea1ec90596c0dcc8d7ef6b4300c"
triple_test = "5b24f7aa99f1e1da5698a4f91ae0f4b45651a1b625c61ed669dd25ff5b937972"

cpu_id = w.Win32_Processor()[0].ProcessorId
disk_serial = w.Win32_DiskDrive()[0].SerialNumber
ram = w.Win32_PhysicalMemory()[0]
ram_id = ram.SerialNumber

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def hwidSend():
    print("Sending hardware info...")
    send(f"{ID_CODE}CPU ID: {cpu_id}")
    send(f"{ID_CODE}Disk Serial Number: {disk_serial}")
    send(f"{ID_CODE}RAM ID: {ram_id}")
    print("Hardware info sent successfully.")


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
    singleHash(verifyHash)
    doubleHash(verifyHash)
    tripleHash(verifyHash)
    try: # Single
        if single_hex_dig == single_test:
            print("{HASH TEST} Single hash working.\n")
    except:
        print("{ERROR!!!} SINGLE HASH TEST FAILED.\n")

    try: # Double
        if double_hex_dig == double_test:
            print("{HASH TEST} Double hash working.\n")
    except:
        print("{ERROR!!!} DOUBLE HASH TEST FAILED.\n")

    try: # Triple
        if triple_hex_dig == triple_test:
            print("{HASH TEST} Triple hash working.\n")
    except:
        print("{ERROR!!!} TRIPLE HASH TEST FAILED.\n")


def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    response = client.recv(2048).decode(FORMAT)  # Decode response
    print(f"{response}")




hwidSend()
print("Sending disconnect message...")
send(DISCONNECT_MESSAGE)
