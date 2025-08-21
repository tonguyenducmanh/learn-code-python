class Person:
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        print("Person __init__ called")

class Employee:
    def __init__(self, salary, **kwargs):
        super().__init__(**kwargs)
        self.salary = salary
        print("Employee __init__ called")

class Teacher(Person, Employee):
    def __init__(self, name, salary):
        super().__init__(name=name, salary=salary)
        print("Teacher __init__ called")

# Các lớp cha gọi super().__init__() để chuyển tiếp tham số cho lớp cha tiếp theo trong MRO

t = Teacher("John", 5000)
print(t.name)    
print(t.salary)
