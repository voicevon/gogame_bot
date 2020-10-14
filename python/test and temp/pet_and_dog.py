class Pet:
    def __init__(self, name):
        self.name = 'unknown'
        self._age = 10
    

    def speak(self):
        self.bark()

    def _reset_age(self):
        self._age = 10

class Dog(Pet):
    def __init__(self):
        Pet.__init__(self,'')

    def bark(self):
        print ('barking')

    def set_age(self, new_age):
        print(self._age)
        self._age = new_age
        print(self._age)
        self._reset_age()
        print(self._age)

my_dog = Dog()
my_dog.speak()
my_dog.set_age(22)
my_dog._reset_age()
