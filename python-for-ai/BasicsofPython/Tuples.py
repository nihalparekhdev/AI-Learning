#Tuples : they are immutable, that means that it cannot be changed after creations.
#They are declared using parentheses () and can contain elements of different data types.

empty_tuple = ()
print(empty_tuple)

my_tuple = ("Nihal", 24, False, True, 3.14)
print(my_tuple)

#Single Tuple : you need to add a comma to create a single tuple or else it is only considered as a string or integer.
single_tuple  = ("Test",)
print(single_tuple)

#Without parentheses, you can create a tuple by separating values with commas.
another_tuple = "Hello", 42, True
print(another_tuple)

#Accessing elements
print(my_tuple[0])  # Output: Nihal
print(my_tuple[1])  # Output: 24

#Slicing the tuple
print(my_tuple[1:4])  # Output: (24, False, True)
print(another_tuple[1:])

#Tuple Unpacking : you can unpack the values of a tuple into separate variables.
point = (10, 20, 30)
x, y, z = point
print(x)  # Output: 10

#Multiple assignment 
a, b, c = 1, "Nihal", True
print(a)  # Output: 1
print(b)  # Output: Nihal
print(c)  # Output: True

#Swap values 
x, y = y, x
print(x)  # Output: True
print(y)  # Output: 10
