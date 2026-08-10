#Basic Python Concepts

#Variables
number = 42 - 10
print(number)

#String 
first_name = "Nihal"
last_name ="Parekh"

full_name = first_name + " " + last_name

long_dash = "-" * 15

print(full_name)
print(long_dash)

print(len(full_name))

#Boolean
is_happy = True
print(is_happy)
print(type(is_happy))

age = 18

can_vote = age >= 18
print(can_vote)


#Logical Operators
age = 25
has_license = True
drunk = False

# AND - both must be true
can_drive = age >= 16 and has_license and not drunk
print(can_drive)  # True

#Assignment Shortcuts
x = 10
x += 5  # Equivalent to x = x + 5
print(x)  # Output: 15

#String Manipulation
name = "Nihal"
print(name.upper())  # Output: NIHAL
print(name.lower())  # Output: nihal
intro = f"My name is {name}"
print(intro)  # Output: My name is Nihal

intro2 = intro.replace(name, "Nihal Parekh")
print(intro2)  # Output: My name is Nihal Parekh