use blake3::Hasher;
use std::env;
use std::process;

fn main() {
    // Get input from command-line arguments
    let args: Vec<String> = env::args().collect();

    // Check if there is an argument provided
    if args.len() < 2 {
        eprintln!("Usage: <program> <input_string>");
        process::exit(1); // Exit with an error code
    }

    let input = &args[1]; // The first argument is the input string

    // Hash the input using BLAKE3
    let hash = Hasher::new().update(input.as_bytes()).finalize();

    // Convert the hash to bytes and print it in hex manually
    let hash_bytes = hash.as_bytes();
    print!("BLAKE3 hash: ");
    for byte in hash_bytes {
        print!("{:02x}", byte); // Print each byte in hexadecimal format
    }
    println!(); // To add a newline at the end of the printed hash
}
