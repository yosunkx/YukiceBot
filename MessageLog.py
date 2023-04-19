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


class MessageLogs:
    def __init__(self, token_limit=1000):
        self._data = {}
        self.token_limit = token_limit

    def _token_count(self, messages):
        return sum(len(message["content"].split()) for message in messages)

    def append(self, key, message):
        if key not in self._data:
            self._data[key] = deque()

        # Remove messages from the front of the deque if the token limit is exceeded
        while (self._token_count(self._data[key]) + len(message["content"].split())) > self.token_limit:
            self._data[key].popleft()

        self._data[key].append(message)

    def __getitem__(self, key):
        if key not in self._data:
            self._data[key] = deque()
        return self._data[key]

    def __repr__(self):
        return str(self._data)

