class Pet:
    def __init__(self):
        self.name = 'unknown'
    

    def speak(self):
        self.bark()

class Dog(Pet):
    def bark(self):
        print ('barking')

import sys
print(sys.path)


import os
print (os.getcwd())
print(os.__file__)

import webbrowser
webbrowser.open('https://cn.bing.com')

my_dog = Dog()
my_dog.speak()