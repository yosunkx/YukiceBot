import random
import string

def generate_random_ID():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))

class MessageID(object):
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        if len(self.items) < 5:
            self.items.append(item)
        else:
            print("Queue is full, cannot enqueue more items.")
    
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
    
    def contains(self, item):
        return item in self.items

