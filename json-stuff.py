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
    data = load_json_file(file_path)
    for student in data["students"]:
        if student["id"] == new_student["id"]:
            print(f"Student with ID #{new_student['id']} already exists.")
            return
    data["students"].append(new_student)
    save_json_file(file_path, data)
    print(f"Added new student: {new_student['name']} (ID #{new_student['id']})")

# Function to search for a student by name and print their details
def search_student_by_name(data, name):
    for student in data["students"]:
        if student["name"].lower() == name.lower():
            print(f"Found student: {json.dumps(student, indent=4)}")
            return
    print(f"No student found with the name {name}.")

# Function to delete a student by ID
def delete_student(file_path, student_id):
    data = load_json_file(file_path)
    for i, student in enumerate(data["students"]):
        if student["id"] == student_id:
            del data["students"][i]
            save_json_file(file_path, data)
            print(f"Deleted student with ID #{student_id}.")
            return
    print(f"No student found with ID #{student_id}.")

# Function to edit a student's information
def edit_student(file_path, student_id, key, new_value):
    data = load_json_file(file_path)
    for student in data["students"]:
        if student["id"] == student_id:
            if key in student:
                student[key] = new_value
                save_json_file(file_path, data)
                print(f"Updated {key} for student with ID #{student_id} to {new_value}.")
                return
            else:
                print(f"Invalid key: {key}. Student data remains unchanged.")
                return
    print(f"No student found with ID #{student_id}.")

# File path to the JSON file
file_path = "info.json"

# Example usage:
# Add a new student
new_student = {
    "id": 5,
    "name": "Charlie",
    "age": 19,
    "full-time": False
}
add_student(file_path, new_student)

# Search for a student by name
data = load_json_file(file_path)
search_student_by_name(data, "Joe")

# Delete a student by ID
delete_student(file_path, 3)

# Edit a student's information
edit_student(file_path, 2, "age", 34)
edit_student(file_path, 2, "full-time", True)
