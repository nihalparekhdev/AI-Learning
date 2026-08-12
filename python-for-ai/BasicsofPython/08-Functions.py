#Functions : reusable pieces of code that perform a specific task.
# Functions
# Create reusable blocks of code


# Building with functions
# Functions are reusable blocks of code that do specific tasks. Instead of writing the same code multiple times, you write it once as a function and call it whenever needed.
# Think of functions like:
# A recipe you can follow multiple times
# A machine that takes input and produces output
# A named shortcut for complex operations

# Defining a function

def my_function(): 
    print("Hello from a function")
    pass

my_function()  # Calling the function

#fucntion with logic 
def weather_report():
    temprature = 25
    if temprature > 30:
        print("It's a hot day")
    else:
        print("It's a pleasant day")

weather_report()  # Calling the function



#Function with Local variable
def mylocal_fun():
    local_variable1 =10
    print("Local variable inside function:", local_variable1)

mylocal_fun()  # Calling the function
#Here the local variable cannot be accessed outside of the function. 
#print("Local variable outside function:", local_variable)


#Function with Global variable
global_variable =20 

def myglobal_fun():
    incremented_value = global_variable + 5
    print("Global variable inside function:", incremented_value)
myglobal_fun()  # Calling the function
print("Global variable outside function:", global_variable)  # Accessing the global variable outside the function

#Best way to use functions for global variable

universal_variable = 30
total = 0

def add_to_total(amount):
    global total
    total += amount

def myuniversal_function(universal_variable):
    return universal_variable + total

result = myuniversal_function(universal_variable)  # Calling the function and storing the result
print("Result after function call:", result)  # Printing the result


#function with parameters

def calculate_totalprice(price,tax_rate,discount):
    total_price = price + (price * tax_rate) - discount
    print("Total price after calculation:", total_price)
calculate_totalprice(price=1000, tax_rate=0.1, discount=50)  # Calling the function with parameters

#Function with return statement

def area_room(width, height):
    area = width * height
    return area
room_area = area_room(5, 4)  # Calling the function and storing the returned value
print(f"Area of the room: {room_area} sq. feet")  # Printing the area of the room


#function with resuable code
def my_multiply_function(a, b):
    return a * b

result = my_multiply_function(5, 3)  # Calling the function and storing the result
print("Result of multiplication:", result)  # Printing the result of multiplication

if my_multiply_function(5, 3) > 10:
    print("The result is greater than 10")



