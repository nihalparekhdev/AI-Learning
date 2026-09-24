import os 
import json
# Get the current working directory
cwd = os.getcwd()
print("Current Working Directory:", cwd)

# Working with JSON
data = {
    "name": "John",
    "age": 30,
    "city": "New York"
}
json_string = json.dumps(data)
print("JSON String:", json_string)