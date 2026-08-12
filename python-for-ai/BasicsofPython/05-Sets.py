#Set : collection that only stores unique values. 
#They also remove duplicate values automatically.

#empty set 
my_set = set()

#Setting values both the ways works
numbers = {1, 2, 3, 4, 5}
fruits = set(["apple", "banana", "cherry", "apple", "banana"]) 
print(fruits) 

#Basic operations
#Adding values to a set
fruits.add("orange")
print(fruits)  # Output: {'banana', 'cherry', 'apple', 'orange'}

#Removing values from a set
fruits.remove("banana")
print(fruits)  # Output: {'cherry', 'apple', 'orange'}

#Fast Check membership
if "orange" in fruits:
    print("Orange can be eaten.")


#

