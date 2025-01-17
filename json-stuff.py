import json

# Load JSON data from file
def load_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Save JSON data to file
def save_json_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Function to find a student's age by ID
def find_student_age(data, student_id):
    for student in data["students"]:
        if student["id"] == student_id:
            return student["age"]
    return None

# Function to add a new student
def add_student(file_path, new_student):
    # Load existing data
    data = load_json_file(file_path)
    
    # Check if student with the same ID already exists
    for student in data["students"]:
        if student["id"] == new_student["id"]:
            print(f"Student with ID #{new_student['id']} already exists.")
            return
    
    # Add new student to the list
    data["students"].append(new_student)
    
    # Save updated data back to the file
    save_json_file(file_path, data)
    print(f"Added new student: {new_student['name']} (ID #{new_student['id']})")

# File path to the JSON file
file_path = "info.json"

idtemp = 4
nametemp = "Alex"
agetemp = 12

# Example: Add a new student
new_student = {
    "id": idtemp,
    "name": nametemp,
    "age": agetemp,
    "full-time": True
}
add_student(file_path, new_student)

# Example: Find a student's age
data = load_json_file(file_path)
student_id = 2
age = find_student_age(data, student_id)

if age is not None:
    print(f"The age of the student with ID #{student_id} is {age}.")
else:
    print(f"Student with ID #{student_id} not found.")
