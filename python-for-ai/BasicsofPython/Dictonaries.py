#Dictionaries are a collection of Key : Value pairs. They are unordered, mutable and indexed.
#They are declared using curly braces {} and can contain elements of different data types.
# Dictionary examples

my_dict = {
    "Name" : "Nihal",
    "Age" : 24,
    "Has License" : False,
    "Is Happy" : True,
    "Height" : 5.9
}

print(my_dict)

#Another way to create a dictionary

my_dict1 = dict(Code = "Python", Course = True , Duration = 3.5, Level = "Beginner")
print(my_dict1)

#Accessing elements in a dictionary
print(my_dict["Name"])
print(my_dict1["Code"])

#Safer with get() method
print(my_dict1.get("Job Title"))  # This will return None if the key doesn't exist  
print(my_dict1.get("Job Title", "Not Found"))

#Add or Update elements in a dictionary
my_dict["Age"] = 25  # Update existing key
my_dict["Job Title"] = "Software Engineer"  # Add new key-value pair
print(my_dict)

#Deleting elements from a dictionary
del my_dict["Job Title"]  # Remove key-value pair
print(my_dict)

#Dictionary Methods
print(my_dict.keys())  # Returns a view of all keys in the dictionary
print(my_dict.values())  # Returns a view of all values in the dictionary
print(my_dict.items())  # Returns a view of all key-value pairs in the dictionary

#Nested Dictionaries
nested_dict = {
    "Person1": {
        "Name": "Nihal",
        "Age": 24
    },
    "Person2": {
        "Name": "Alice",
        "Age": 30
    }
}

print(nested_dict)