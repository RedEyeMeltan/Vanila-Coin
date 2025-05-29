use blake3;
use std::io;
use std::sync::{Arc, atomic::{AtomicBool, Ordering}};
use std::thread;
use rand;
use std::net::TcpStream;
use std::io::{Write};


fn main() {
    println!("Blockchain Mining App Started!");
    println!("===============================================");
    
    let should_quit = Arc::new(AtomicBool::new(false));
    let show_logs = Arc::new(AtomicBool::new(false));
    
    let should_quit_clone = Arc::clone(&should_quit);
    let show_logs_clone = Arc::clone(&show_logs);
    
    // Start mining in a separate thread
    let mining_thread = thread::spawn(move || {
        Hash(should_quit_clone, show_logs_clone, "test_ID", "Test_Transaction")
    });
    
    // Handle user input in main thread
    println!("Welcome to the Vanilla CoinBlockchain Mining App!");
    println!("Mining is running in the background...");
    println!("Type '1' to toggle mining logs on/off");
    println!("Type 'q' and press Enter to stop the mining process.");
    
    loop {
        let mut input = String::new();
        match io::stdin().read_line(&mut input) {
            Ok(_) => {
                let input = input.trim().to_lowercase();
                if input == "q" {
                    println!("Stopping mining process...");
                    should_quit.store(true, Ordering::Relaxed);
                    break;
                } else if input == "1" {
                    let current_state = show_logs.load(Ordering::Relaxed);
                    show_logs.store(!current_state, Ordering::Relaxed);
                    if !current_state {
                        println!("Mining logs enabled!");
                    } else {
                        println!("Mining logs disabled!");
                    }
                }
            }
            Err(error) => {
                println!("Error reading input: {}", error);
                break;
            }
        }
    }
    
    // Wait for mining thread to finish
    if let Ok(result) = mining_thread.join() {
        println!("Mining stopped! Final result: {}", result);
    }
    println!("Goodbye! Thanks for using the Blockchain Mining App!");
}

fn createBlockTemplate(id: u32, nonce: &str, previous_hash: &str, miner_public_id: &str, transactions: &str) -> String {
    let block_template = format!(
        "ID: {}.\
         Nonce: {}.\
         PreviousHash: {}.\
         MinerPublicID: {}.\
         Transactions: {}.",
        id, nonce, previous_hash, miner_public_id, transactions
    );
    block_template
}

fn Hash(should_quit: Arc<AtomicBool>, show_logs: Arc<AtomicBool>, miner_public_id: &str, transactions: &str) -> String {
    let a = rand::random::<u128>();
    let b = rand::random::<u128>();
    let c = rand::random::<u128>();
    let mut in_nonce = format!("{}{}{}", a.to_string(), b.to_string(), c.to_string());

    let mut attempt = 0;
    
    loop {
        let a = rand::random::<u128>();
        let b = rand::random::<u128>();
        let c = rand::random::<u128>();
        in_nonce = format!("{}{}{}", a.to_string(), b.to_string(), c.to_string());
        // Check if user wants to quit
        if should_quit.load(Ordering::Relaxed) {
            println!("Mining stopped by user request!");
            return format!("Mining stopped at attempt {}", attempt);
        }

        let transaction_add = format!("{}+100, {}", miner_public_id, transactions);
        let input = createBlockTemplate(1, in_nonce.as_str(), "9182h3e9832h", "28932nx893", transaction_add.as_str());
        let hash1 = blake3::hash(input.as_bytes());
        let hash1 = hash1.to_hex().to_string();
    
        if hash1.starts_with("00") {
            println!("SUCCESSFULLY MINED A BLOCK. ATTEMPT: {}. HASH: {}", attempt, hash1);
            let server_send_back = format!("{}|||{}", input, hash1);
            println!("Sending to server: {}", server_send_back);
            tcp_send(server_send_back.as_str());
            return server_send_back;
        }
        
        if !hash1.starts_with("00") {
            // Only show logs if enabled
            if show_logs.load(Ordering::Relaxed) {
                println!("attempt: {}. HASH: {}", attempt, hash1);
            }
            attempt += 1;
        }

    }    
}

fn tcp_send(data: &str) -> io::Result<()>{
    // Establish a connection
    let mut stream = TcpStream::connect("127.0.0.1:34254")?;

    // Write some data
    let bytes_written = stream.write(b"{data}")?; //not sure this line works TEST LATER
    println!("{} bytes written", bytes_written);

    // Flush the stream
    stream.flush()?;

    Ok(())
}