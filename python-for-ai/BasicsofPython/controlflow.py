#Control Flow

#Else if condition
marks = 80

if marks >= 90:
    print("A grade!, Excellent work!")
elif marks >= 80:
    print("B grade!, Good job!")
elif marks >= 70:
    print("C grade!, You can do better!")
else:
    print("D grade!, Need some improvements")

#Operators with Else if condition
age = 100
has_license = True
if age < 13 and has_license:
    print("You are a child. You cannot drive.")
elif age < 20 and has_license:
    print("You are a teenager. You can drive with supervision.")
elif age < 65 and has_license:
    print("You are an adult. You can drive.")
else:
    print("You are a senior citizen. You can drive with assistance.")


#Loops

for i in range(10):
    print("*" * i)