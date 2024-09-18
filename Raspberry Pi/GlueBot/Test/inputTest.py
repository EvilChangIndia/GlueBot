from threading import Thread
from time import sleep

def threaded_function(arg):
    while True:
        inp=input("enter: ")
        print("u said:", inp)


if __name__ == "__main__":
    thread = Thread(target = threaded_function, args = (10, ))
    thread.start()
    while True:
        print("hello")
        sleep(1)
        inp2=input("second in : ")
    thread.join()
    print("thread finished...exiting")