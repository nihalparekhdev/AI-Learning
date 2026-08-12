#List examples : they are mutable, that means that it can be changed after creations.
#They are declared using square brackets [] and can contain elements of different data types.
has_license = False
my_list = ["Nihal", 24, has_license, True, 3.14]

print (my_list)

#Accessing elements
my_list[2] = True
print(my_list)

#Slicing 
print(my_list[1:])

#Appending elements
my_list.append("Python")
print(my_list)

#List Methods
my_list.remove(24)
print(my_list)

print(len(my_list))

