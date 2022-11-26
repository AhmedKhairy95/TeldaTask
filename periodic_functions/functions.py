import time


def func1():
    print("func1")
    raise Exception("Found an exception")


def print_string():
    print("print_string")


def blocking_task():
    time.sleep(60)
