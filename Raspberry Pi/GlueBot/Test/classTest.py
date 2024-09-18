class A:
    a= 2
    def __init__(self, i):
        nonlocal a 
        a=i
    def show_a(self, para_a= a):
        print("a is: ", para_a)

while True:
    i=int(input("enter a: "))
    objA= A(i)
    objA.show_a()

