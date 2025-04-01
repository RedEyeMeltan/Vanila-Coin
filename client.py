import socket
import wmi
import hashlib
import blake3

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
single_test = "4878ca0425c739fa427f7eda20fe845f6b2e46ba5fe2a14df5b1e32f50603215"
double_test = "55beb65d3293549b07cf215978375cf674d82de8657775da6c0f697b4e6b5e0b"
triple_test = "1af8e96926a936cce32a1e304a068a3379968fd28c0843dcb08186adfaba1441"

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
    try: # Single
        if singleHash(verifyHash) == single_test:
            print("{HASH TEST} Single hash working.\n")
    except:
        print("{ERROR!!!} SINGLE HASH TEST FAILED.\n")

    try: # Double
        if doubleHash(verifyHash) == double_test:
            print("{HASH TEST} Double hash working.\n")
    except:
        print("{ERROR!!!} DOUBLE HASH TEST FAILED.\n")

    try: # Triple
        if tripleHash(verifyHash) == triple_test:
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
