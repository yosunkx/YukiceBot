from collections import deque
import random
import string

def generate_random_ID():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

class MessageID(object):
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        if len(self.items) >= 10:
           self.dequeue()

        self.items.append(item)
    
    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        else:
            print("Queue is empty, cannot dequeue.")
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)
    
    def peek(self):
        if not self.is_empty():
            return self.items[0]
        else:
            print("Queue is empty, cannot peek.")

    def print(self):
        if self.is_empty():
            print('empty ID')
        else:
            for item in self.items:
                print(item)
    
    def contains(self, item):
        return item in self.items

