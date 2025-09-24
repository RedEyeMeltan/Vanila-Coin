import socket
import threading
import hashlib
import pytz
import json
import mysql.connector
import blake3
import smtplib
import pandas as pd
import os
from mysql.connector import Error
from datetime import datetime, timedelta
from random_word import RandomWords
import time

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

# Database configuration - UPDATE THESE WITH YOUR ACTUAL CREDENTIALS
DB_CONFIG = {
    'host': 'localhost',
    'user': '(user)',  # Change this to your MySQL username
    'password': '(Password)',  # Change this to your MySQL password (empty for XAMPP default)
    'database': '(Database)'
}

# Blockchain constants
BLOCK_TIME_TARGET = 10  # Target 10 seconds per block
DIFFICULTY_ADJUSTMENT_INTERVAL = 10  # Adjust difficulty every 10 blocks
INITIAL_DIFFICULTY = 2  # Start with "00" (2 zeros)
BLOCK_REWARD = 100

# Hash test constants
VERIFY_HASH = 'test'
SINGLE_TEST = "4878ca0425c739fa427f7eda20fe845f6b2e46ba5fe2a14df5b1e32f50603215"
DOUBLE_TEST = "55beb65d3293549b07cf215978375cf674d82de8657775da6c0f697b4e6b5e0b"
TRIPLE_TEST = "1af8e96926a936cce32a1e304a068a3379968fd28c0843dcb08186adfaba1441"

# Global variables
server_running = True
connected_clients = []
blockchain = []
current_difficulty = INITIAL_DIFFICULTY
mydb = None
mycursor = None

# Server setup
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(ADDR)

# Word list setup
r = RandomWords()

def setup_database():
    """Setup database and tables if they don't exist"""
    global mydb, mycursor
    
    try:
        # First, try to connect without specifying a database to create it
        connection_config = {
            'host': DB_CONFIG['host'],
            'user': DB_CONFIG['user'],
            'password': DB_CONFIG['password']
        }
        
        print(f"[DATABASE] Attempting to connect to MySQL server at {DB_CONFIG['host']} with user '{DB_CONFIG['user']}'...")
        
        # Connect without database first
        mydb = mysql.connector.connect(**connection_config)
        mycursor = mydb.cursor()
        
        # Create database if it doesn't exist
        mycursor.execute("CREATE DATABASE IF NOT EXISTS vanillacoin")
        print("[DATABASE] Database 'vanillacoin' created or already exists")
        
        # Close initial connection
        mycursor.close()
        mydb.close()
        
        # Reconnect to the specific database
        print("[DATABASE] Connecting to vanillacoin database...")
        mydb = mysql.connector.connect(**DB_CONFIG)
        mycursor = mydb.cursor()
        
        # Create tables if they don't exist
        print("[DATABASE] Creating tables...")
        
        # Customer info table
        mycursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_info (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(256) UNIQUE NOT NULL,
                password VARCHAR(256) NOT NULL,
                cpu_id VARCHAR(256),
                ram_id VARCHAR(256),
                motherboard_id VARCHAR(256),
                time_account_created VARCHAR(256),
                word_list JSON,
                balance DECIMAL(10,2) DEFAULT 0.00
            )
        """)
        
        # Blocks table
        mycursor.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                block_id INT UNIQUE NOT NULL,
                nonce VARCHAR(256) NOT NULL,
                previous_hash VARCHAR(256) NOT NULL,
                miner_id VARCHAR(256) NOT NULL,
                transactions TEXT,
                block_hash VARCHAR(256) NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                difficulty INT NOT NULL
            )
        """)
        
        # Wallets table
        mycursor.execute("""
            CREATE TABLE IF NOT EXISTS wallets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                address VARCHAR(256) UNIQUE NOT NULL,
                balance DECIMAL(10,2) DEFAULT 0.00,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        
        mydb.commit()
        print("[DATABASE] ✅ Database and tables setup complete")
        return True
        
    except Error as e:
        print(f"[DATABASE ERROR] ❌ {e}")
        print(f"[DATABASE ERROR] Error code: {e.errno}")
        if e.errno == 1045:
            print("[DATABASE ERROR] 🔒 Access denied - Please check your MySQL username and password in DB_CONFIG")
            print("[DATABASE ERROR] 💡 For XAMPP: username='root', password=''")
            print("[DATABASE ERROR] 💡 Make sure MySQL service is running")
        elif e.errno == 2003:
            print("[DATABASE ERROR] 🌐 Can't connect to MySQL server - Make sure MySQL is running")
        
        return False
    except Exception as e:
        print(f"[DATABASE ERROR] Unexpected error: {e}")
        return False

def singleHash(content):
    return blake3.blake3(f"{content}".encode('utf-8')).hexdigest()
    
def doubleHash(content):
    single = blake3.blake3(f"{content}".encode('utf-8')).hexdigest()
    double = blake3.blake3(f"{single}".encode('utf-8')).hexdigest()
    return double

def tripleHash(content):
    single = blake3.blake3(f"{content}".encode('utf-8')).hexdigest()
    double = blake3.blake3(f"{single}".encode('utf-8')).hexdigest()
    triple = blake3.blake3(f"{double}".encode('utf-8')).hexdigest()
    return triple

def verifyHash():
    """Verify hash functions are working correctly"""
    try:
        if singleHash(VERIFY_HASH) == SINGLE_TEST:
            print("{HASH TEST} ✅ Single hash working.")
        else:
            print("{ERROR!!!} ❌ SINGLE HASH TEST FAILED.")
            return False
        
        if doubleHash(VERIFY_HASH) == DOUBLE_TEST:
            print("{HASH TEST} ✅ Double hash working.")
        else:
            print("{ERROR!!!} ❌ DOUBLE HASH TEST FAILED.")
            return False
        
        if tripleHash(VERIFY_HASH) == TRIPLE_TEST:
            print("{HASH TEST} ✅ Triple hash working.")
        else:
            print("{ERROR!!!} ❌ TRIPLE HASH TEST FAILED.")
            return False
            
        return True
    except Exception as e:
        print(f"[ERROR] Hash verification failed: {e}")
        return False

def getTime():
    pst_timezone = pytz.timezone("America/Los_Angeles")
    current_pst_time = datetime.now(pst_timezone)
    return current_pst_time.strftime("%Y-%m-%d %H:%M:%S")

def load_blockchain():
    """Load blockchain from database"""
    global blockchain
    
    if not mydb or not mycursor:
        print("[BLOCKCHAIN ERROR] No database connection available")
        return
        
    try:
        mycursor.execute("SELECT * FROM blocks ORDER BY block_id")
        blocks = mycursor.fetchall()
        blockchain = []
        for block in blocks:
            blockchain.append({
                'block_id': block[1],
                'nonce': block[2],
                'previous_hash': block[3],
                'miner_id': block[4],
                'transactions': block[5],
                'block_hash': block[6],
                'timestamp': block[7],
                'difficulty': block[8]
            })
        print(f"[BLOCKCHAIN] ✅ Loaded {len(blockchain)} blocks")
    except Error as e:
        print(f"[BLOCKCHAIN ERROR] Failed to load blockchain: {e}")
        blockchain = []

def get_current_difficulty():
    """Calculate current mining difficulty"""
    global current_difficulty
    
    try:
        if len(blockchain) < DIFFICULTY_ADJUSTMENT_INTERVAL:
            return current_difficulty
        
        # Get last 10 blocks
        recent_blocks = blockchain[-DIFFICULTY_ADJUSTMENT_INTERVAL:]
        
        # Calculate average time between blocks
        time_taken = 0
        for i in range(1, len(recent_blocks)):
            try:
                # Handle both datetime objects and strings
                if isinstance(recent_blocks[i-1]['timestamp'], str):
                    prev_time = datetime.strptime(recent_blocks[i-1]['timestamp'], "%Y-%m-%d %H:%M:%S")
                else:
                    prev_time = recent_blocks[i-1]['timestamp']
                
                if isinstance(recent_blocks[i]['timestamp'], str):
                    curr_time = datetime.strptime(recent_blocks[i]['timestamp'], "%Y-%m-%d %H:%M:%S")
                else:
                    curr_time = recent_blocks[i]['timestamp']
                
                time_taken += (curr_time - prev_time).total_seconds()
                
            except (ValueError, TypeError, AttributeError) as e:
                print(f"[DIFFICULTY WARNING] Error processing timestamp: {e}")
                # Use default time if timestamp parsing fails
                time_taken += BLOCK_TIME_TARGET
        
        avg_time = time_taken / (len(recent_blocks) - 1)
        
        # Adjust difficulty
        if avg_time < BLOCK_TIME_TARGET:
            current_difficulty += 1  # Make it harder
        elif avg_time > BLOCK_TIME_TARGET * 2:
            current_difficulty = max(1, current_difficulty - 1)  # Make it easier
        
        print(f"[DIFFICULTY] Adjusted to {current_difficulty} (avg time: {avg_time}s)")
        return current_difficulty
        
    except (IndexError, KeyError, ZeroDivisionError) as e:
        print(f"[DIFFICULTY ERROR] Failed to calculate difficulty: {e}")
        return current_difficulty

def validate_block(block_data, block_hash):
    """Validate a mined block"""
    try:
        # Parse block data
        parts = block_data.split('.')
        if len(parts) < 5:
            return False, "Invalid block format"
        
        block_id = int(parts[0].split(': ')[1])
        nonce = parts[1].split(': ')[1]
        previous_hash = parts[2].split(': ')[1]
        miner_id = parts[3].split(': ')[1]
        transactions = parts[4].split(': ')[1]
        
        # Check if block already exists (only if database is available)
        if mydb and mycursor:
            mycursor.execute("SELECT * FROM blocks WHERE block_id = %s", (block_id,))
            if mycursor.fetchone():
                return False, "Block already exists"
        
        # Validate hash
        calculated_hash = blake3.blake3(block_data.encode('utf-8')).hexdigest()
        if calculated_hash != block_hash:
            return False, "Hash mismatch"
        
        # Check difficulty
        difficulty = get_current_difficulty()
        required_prefix = "0" * difficulty
        if not block_hash.startswith(required_prefix):
            return False, f"Hash doesn't meet difficulty requirement: {required_prefix}"
        
        # Validate previous hash (if not genesis block)
        if block_id > 1:
            if len(blockchain) == 0 or blockchain[-1]['block_hash'] != previous_hash:
                return False, "Invalid previous hash"
        
        return True, "Valid block"
        
    except Exception as e:
        return False, f"Validation error: {e}"

def store_block(block_data, block_hash, miner_id):
    """Store validated block in database and update balances"""
    if not mydb or not mycursor:
        print("[BLOCKCHAIN ERROR] No database connection available")
        return False
        
    try:
        # Parse block data
        parts = block_data.split('.')
        block_id = int(parts[0].split(': ')[1])
        nonce = parts[1].split(': ')[1]
        previous_hash = parts[2].split(': ')[1]
        transactions = parts[4].split(': ')[1]
        
        # Insert block
        insert_query = """
            INSERT INTO blocks (block_id, nonce, previous_hash, miner_id, transactions, block_hash, timestamp, difficulty)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (block_id, nonce, previous_hash, miner_id, transactions, block_hash, datetime.now(), get_current_difficulty())
        mycursor.execute(insert_query, values)
        
        # Update miner balance
        mycursor.execute("SELECT balance FROM customer_info WHERE username = %s", (miner_id,))
        result = mycursor.fetchone()
        if result:
            new_balance = float(result[0]) + BLOCK_REWARD
            mycursor.execute("UPDATE customer_info SET balance = %s WHERE username = %s", (new_balance, miner_id))
        else:
            print(f"[BLOCKCHAIN WARNING] Miner {miner_id} not found in customer_info table")
        
        mydb.commit()
        
        # Add to local blockchain
        blockchain.append({
            'block_id': block_id,
            'nonce': nonce,
            'previous_hash': previous_hash,
            'miner_id': miner_id,
            'transactions': transactions,
            'block_hash': block_hash,
            'timestamp': datetime.now(),
            'difficulty': get_current_difficulty()
        })
        
        print(f"[BLOCKCHAIN] ✅ Block {block_id} stored successfully. Miner {miner_id} rewarded {BLOCK_REWARD} coins")
        return True
        
    except Error as e:
        print(f"[BLOCKCHAIN ERROR] Failed to store block: {e}")
        return False

def broadcast_to_clients(message):
    """Broadcast message to all connected clients"""
    for client in connected_clients[:]:  # Copy list to avoid modification issues
        try:
            client.send(message.encode(FORMAT))
        except:
            connected_clients.remove(client)

def Add_User(username, password, cpu_id, ram_id, motherboard_id, word_list, hardware_info=None):
    """Add user to database with proper word list storage and hardware info"""
    if not mydb or not mycursor:
        return False, "No database connection"
        
    try:
        # Use real hardware if provided
        if hardware_info:
            cpu_id = hardware_info.get('cpu_id', '')
            ram_id = hardware_info.get('ram_id', '')
            # We store 'disk_serial' in the 'motherboard_id' column for consistency
            motherboard_id = hardware_info.get('disk_serial', '')

        # Check if user already exists
        mycursor.execute("SELECT 1 FROM customer_info WHERE username = %s", (username,))
        if mycursor.fetchone():
            return False, "Username already exists"
        
        # Hash the five security words
        hashed_words = [singleHash(word) for word in (word_list or [])]
        
        insert_query = """
            INSERT INTO customer_info (
                username, password, cpu_id, ram_id, motherboard_id, time_account_created, word_list, balance
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            username,
            doubleHash(password),
            singleHash(cpu_id or ''),
            singleHash(ram_id or ''),
            singleHash(motherboard_id or ''),
            getTime(),
            json.dumps(hashed_words),
            0.00
        )
        
        mycursor.execute(insert_query, values)
        mydb.commit()
        print(f"[USER] ✅ Added user: {username} to database. ID: {mycursor.lastrowid}")
        return True, "User created successfully"
        
    except Error as e:
        print(f"[USER ERROR] {e}")
        return False, str(e)

def verify_hardware_match(username, current_hardware):
    """Check if current hardware matches stored hardware (2/3 rule)"""
    if not mydb or not mycursor:
        return True  # Allow login if no database
        
    try:
        mycursor.execute("SELECT cpu_id, ram_id, motherboard_id FROM customer_info WHERE username = %s", (username,))
        result = mycursor.fetchone()
        
        if not result:
            return False  # User not found
            
        stored_cpu, stored_ram, stored_motherboard = result
        
        # Check matches
        matches = 0
        total_checks = 3
        
        if singleHash(current_hardware.get('cpu_id', '')) == stored_cpu:
            matches += 1
        if singleHash(current_hardware.get('ram_id', '')) == stored_ram:
            matches += 1
        if singleHash(current_hardware.get('disk_serial', '')) == stored_motherboard:
            matches += 1
            
        # Return True if 2/3 or more match
        return matches >= 2
        
    except Exception as e:
        print(f"[HARDWARE CHECK ERROR] {e}")
        return True  # Allow login on error

def verify_user_login(username, password, word_list=None, hardware_info=None):
    """Verify user login with username, password, and optional word list"""
    if not mydb or not mycursor:
        return False, "No database connection"
        
    try:
        # Get user data
        mycursor.execute("SELECT password, word_list, cpu_id, ram_id, motherboard_id FROM customer_info WHERE username = %s", (username,))
        result = mycursor.fetchone()
        
        if not result:
            return False, "User not found"
        
        stored_password, stored_word_list, stored_cpu, stored_ram, stored_motherboard = result
        
        # Verify password
        if doubleHash(password) != stored_password:
            return False, "Invalid password"
        
        # Check hardware if provided
        if hardware_info:
            hardware_matches = verify_hardware_match(username, hardware_info)
            
            if not hardware_matches:
                # Hardware mismatch - require security words
                if not word_list:
                    return False, "HARDWARE_MISMATCH"
                
                # Verify word list (now only 5 words)
                hashed_input_words = [singleHash(word) for word in word_list]
                stored_words = json.loads(stored_word_list)
                
                if hashed_input_words != stored_words:
                    return False, "Invalid security words"
                
                print(f"[LOGIN] ✅ User {username} authenticated with security words due to hardware changes")
            else:
                print(f"[LOGIN] ✅ User {username} authenticated with hardware verification")
        
        return True, "Login successful"
        
    except Exception as e:
        print(f"[LOGIN ERROR] {e}")
        return False, str(e)

def generate_word_security():
    """Generate 5 unique random words for security"""
    word_list = []
    attempts = 0
    max_attempts = 100
    
    while len(word_list) < 5 and attempts < max_attempts:  # Changed from 20 to 5
        try:
            word = r.get_random_word()
            if word and len(word) <= 6 and word not in word_list:
                word_list.append(word)
        except:
            pass  # Continue if random word generation fails
        attempts += 1
    
    if len(word_list) < 5:  # Changed from 20 to 5
        # Fallback words if random generation fails
        fallback_words = ['cat', 'dog', 'sun', 'moon', 'tree', 'rock', 'fish', 'bird', 'car', 'book']
        word_list.extend(fallback_words[:5-len(word_list)])  # Changed from 20 to 5
    
    return word_list[:5]  # Changed from 20 to 5

def shutdown_server():
    """Shutdown server when quit command is entered"""
    global server_running
    while server_running:
        try:
            command = input()
            if command.strip().lower() == SHUTDOWN_MESSAGE:
                server_running = False
                print("[SHUTDOWN] 🛑 Server is shutting down...")
                break
        except:
            break

def handle_client(conn, addr):
    """Handle individual client connections"""
    print(f"[NEW CONNECTION] 🔗 {addr} connected.")
    connected_clients.append(conn)
    connected = True
    
    try:
        while connected and server_running:
            msg_length = conn.recv(HEADER).decode(FORMAT)
            
            if msg_length:
                msg_length = int(msg_length.strip())
                msg = conn.recv(msg_length).decode(FORMAT)
                
                if msg == DISCONNECT_MESSAGE:
                    connected = False
                    break
                
                print(f"[{addr}] {msg}")
                
                # Handle username availability check
                if "CHECK_USERNAME|" in msg:
                    try:
                        username = msg.split("CHECK_USERNAME|")[1].strip()
                        print(f"[{addr}] 🔍 Checking username availability: {username}")
                        
                        # Check if username exists in database
                        if mydb and mycursor:
                            mycursor.execute("SELECT username FROM customer_info WHERE username = %s", (username,))
                            result = mycursor.fetchone()
                            if result:
                                response = f"USERNAME_TAKEN: {username} is already registered"
                            else:
                                response = f"USERNAME_AVAILABLE: {username} is available"
                        else:
                            # Check local files if no database
                            if os.path.exists(f"{username}_account.json"):
                                response = f"USERNAME_TAKEN: {username} is already registered"
                            else:
                                response = f"USERNAME_AVAILABLE: {username} is available"
                        
                        conn.send(response.encode(FORMAT))
                        
                    except Exception as e:
                        error_msg = f"USERNAME_CHECK_ERROR: {e}"
                        conn.send(error_msg.encode(FORMAT))
                        print(f"[ERROR] ❌ {error_msg}")
                
                # Handle user registration
                elif "REGISTER|" in msg:
                    try:
                        payload = msg.split("REGISTER|", 1)[1]
                        parts = payload.split("|")

                        if len(parts) >= 3:
                            username = parts[0]
                            password = parts[1]

                            # word list (required)
                            try:
                                word_list = json.loads(parts[2])
                            except Exception as e:
                                conn.send("REGISTRATION_FAILED: Invalid word list JSON".encode(FORMAT))
                                print(f"[ERROR] ❌ Registration word list parse: {e}")
                                continue

                            # optional hardware JSON at parts[3]
                            hardware_info = None
                            if len(parts) >= 4 and parts[3].strip():
                                try:
                                    hardware_info = json.loads(parts[3])
                                except Exception as e:
                                    print(f"[REGISTER PARSE] hardware JSON error: {e}")

                            success, message = Add_User(
                                username, password, None, None, None, word_list, hardware_info=hardware_info
                            )

                            if success:
                                response = f"REGISTRATION_SUCCESS: {message}"
                                print(f"[{addr}] ✅ User {username} registered successfully")
                            else:
                                response = f"REGISTRATION_FAILED: {message}"
                                print(f"[{addr}] ❌ Registration failed for {username}: {message}")

                            conn.send(response.encode(FORMAT))
                        else:
                            conn.send("REGISTRATION_FAILED: Invalid registration data".encode(FORMAT))

                    except Exception as e:
                        error_msg = f"REGISTRATION_ERROR: {e}"
                        conn.send(error_msg.encode(FORMAT))
                        print(f"[ERROR] ❌ Registration error: {e}")
                
                # Handle user login
                elif "LOGIN|" in msg:
                    try:
                        payload = msg.split("LOGIN|", 1)[1]
                        parts = payload.split("|")

                        if len(parts) >= 2:
                            username = parts[0]
                            password = parts[1]

                            word_list = None
                            hardware_info = None

                            # optional word list at parts[2]
                            if len(parts) >= 3 and parts[2].strip():
                                try:
                                    word_list = json.loads(parts[2])
                                except Exception as e:
                                    print(f"[LOGIN PARSE] word_list JSON error: {e}")

                            # optional hardware JSON at parts[3]
                            if len(parts) >= 4 and parts[3].strip():
                                try:
                                    hardware_info = json.loads(parts[3])
                                except Exception as e:
                                    print(f"[LOGIN PARSE] hardware JSON error: {e}")

                            success, message = verify_user_login(username, password, word_list, hardware_info)

                            if success:
                                response = f"LOGIN_SUCCESS: {message}"
                                print(f"[{addr}] ✅ User {username} logged in successfully")
                            else:
                                response = f"LOGIN_FAILED: {message}"
                                print(f"[{addr}] ❌ Login failed for {username}: {message}")

                            conn.send(response.encode(FORMAT))
                        else:
                            conn.send("LOGIN_FAILED: Invalid login data".encode(FORMAT))

                    except Exception as e:
                        error_msg = f"LOGIN_ERROR: {e}"
                        conn.send(error_msg.encode(FORMAT))
                        print(f"[ERROR] ❌ {error_msg}")
                
                # Handle hardware ID messages
                elif f"{ID_CODE}CPU ID:" in msg:
                    cpu_id = msg.split('CPU ID: ')[1]
                    print(f"[{addr}] 💻 CPU ID RECEIVED: {cpu_id}")
                    conn.send("CPU INFO RECEIVED".encode(FORMAT))
                
                elif f"{ID_CODE}Disk Serial Number:" in msg:
                    disk_serial = msg.split('Disk Serial Number: ')[1]
                    print(f"[{addr}] 💾 DISK SERIAL NUMBER RECEIVED: {disk_serial}")
                    conn.send("DISK INFO RECEIVED".encode(FORMAT))
                
                elif f"{ID_CODE}RAM ID:" in msg:
                    ram_id = msg.split('RAM ID: ')[1]
                    print(f"[{addr}] 🧠 RAM ID RECEIVED: {ram_id}")
                    conn.send("RAM INFO RECEIVED".encode(FORMAT))
                
                # Handle mined blocks
                elif "|||" in msg:
                    try:
                        block_data, block_hash = msg.split("|||")
                        
                        # Extract miner ID from block data
                        miner_id = block_data.split("MinerPublicID: ")[1].split(".")[0]
                        
                        is_valid, validation_msg = validate_block(block_data, block_hash)
                        
                        if is_valid:
                            if store_block(block_data, block_hash, miner_id):
                                response = f"BLOCK ACCEPTED: {validation_msg}"
                                # Broadcast new block to all clients
                                broadcast_to_clients(f"NEW_BLOCK|||{msg}")
                            else:
                                response = "BLOCK REJECTED: Storage failed"
                        else:
                            response = f"BLOCK REJECTED: {validation_msg}"
                        
                        conn.send(response.encode(FORMAT))
                        print(f"[MINING] ⛏️ {response}")
                        
                    except Exception as e:
                        error_msg = f"BLOCK PROCESSING ERROR: {e}"
                        conn.send(error_msg.encode(FORMAT))
                        print(f"[ERROR] ❌ {error_msg}")
                
                else:
                    conn.send(f"MSG received: {msg}".encode(FORMAT))
                    
    except Exception as e:
        print(f"[CONNECTION ERROR] ❌ {addr}: {e}")
    finally:
        if conn in connected_clients:
            connected_clients.remove(conn)
        conn.close()
        print(f"[DISCONNECTED] 🔌 {addr} disconnected.")

def start():
    """Start the server"""
    print("[STARTING] 🚀 Server is starting...")
    server.listen()
    print(f"[LISTENING] 👂 Server is listening on {SERVER}:{PORT}")
    print(f"[INFO] 💡 Type '{SHUTDOWN_MESSAGE}' and press Enter to stop the server")
    
    while server_running:
        try:
            server.settimeout(1.0)  # Allow checking server_running periodically
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.daemon = True
            thread.start()
            print(f"[ACTIVE CONNECTIONS] 📊 {threading.active_count() - 2}")  # -2 for main and shutdown threads
        except socket.timeout:
            continue
        except Exception as e:
            if server_running:
                print(f"[SERVER ERROR] ❌ {e}")
            break

def main():
    """Main function to initialize and start server"""
    global server_running
    
    print("=== VANILLA COIN BLOCKCHAIN SERVER v2.0 ===")
    print("🪙 Starting VanillaCoin blockchain server...")
    
    # Initialize database
    print("\n📊 Setting up database...")
    if not setup_database():
        print("❌ Database setup failed! Server will run with limited functionality.")
        print("⚠️ Blocks will not be persisted and user accounts will not work.")
        print("🔧 Please fix your MySQL connection and restart the server.")
        
        # Ask if user wants to continue
        response = input("\nDo you want to continue anyway? (y/n): ").strip().lower()
        if response != 'y' and response != 'yes':
            print("👋 Exiting server...")
            return
    
    # Verify hash functions
    print("\n🔍 Verifying hash functions...")
    if not verifyHash():
        print("❌ Hash verification failed! Exiting.")
        return
    
    # Load existing blockchain
    print("\n⛓️ Loading blockchain...")
    load_blockchain()
    
    # Start server threads
    server_thread = threading.Thread(target=start)
    server_thread.daemon = True
    server_thread.start()
    
    shutdown_thread = threading.Thread(target=shutdown_server)
    shutdown_thread.daemon = True
    shutdown_thread.start()
    
    try:
        # Keep main thread alive
        while server_running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] 🛑 Server interrupted by user")
        server_running = False
    finally:
        # Clean up database connection
        if mydb:
            try:
                mycursor.close()
                mydb.close()
                print("[DATABASE] 🔌 Database connection closed")
            except:
                pass
    
    print("[SHUTDOWN] 🛑 Server stopped")
    print("👋 Goodbye!")

if __name__ == "__main__":

    main()
