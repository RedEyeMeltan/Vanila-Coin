import subprocess

# The input string you want to hash
input_string = "hi"

# Run the Rust program with the input string as an argument
result = subprocess.run(["./target/debug/blake3-sha256-bench.exe", input_string], capture_output=True, text=True)

# Print the output from the Rust program
print(result.stdout)
