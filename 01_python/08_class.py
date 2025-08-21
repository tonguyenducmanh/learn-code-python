class Person:
    def __init__(self):
        pass

    def __str__(self):
        return "Class Person"
    
    @property
    def age(self):
        return 115

jack= Person()

print(jack.age)