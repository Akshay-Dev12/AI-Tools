print("Hello, World! Akshay")

if 1 > 2:
    print("Output is correct")
else:
    print("Out is in correct .")

# Variables in python
x = 5
y = "Name is Akshay"

"""
More than One line comment
Samples
"""

# casting examples
x = str (3)
print(x)

print(type(x))


# unpacking a Array
fruits = ["Apple", "Banana", "Grape"]
fr1, fr2, fr3 = fruits

print ("Ans " + "is: ", 5 + 6 )

# func samples, Global variable usage.
num1 = 10
num2 = 100
def cal (num2):
    return num1 + num2

print(cal(10))

# complex 
p = 11j

p = range(6)

# Dict
p = {
    "Name": "Aju",
    "Age": 23
}

# Set ex
p = {1, 1, 2, 3}

# Specific data type setting is possible
print(p)

thislist = ["apple", "banana", "cherry", "orange", "kiwi", "melon", "mango"]
print(thislist[2:5])

thislist.insert(2, "watermelon")


#This will return the items from position 2 to 5.

# Tuples are unchangeable, meaning that we cannot change, add or remove items after the tuple has been created.

fruits = ["apple", "banana", "cherry"]
for x in fruits:
  print(x)


# n, no.of arguments and one exp.
x = lambda a, b: a + 10 + b
print(x(5, 10))


# OOPs
class Person:
  def __init__(self, name, age):
    self.name = name
    self.age = age

p1 = Person("Aksahy", 23)
print(p1.name, p1.age)

# inheritance
class Student(Person):
  pass

x = Student("Akshay", 23)
print(x.name)

class Student(Person):
  def __init__(self, fname, lname):
    super().__init__(fname, lname)

