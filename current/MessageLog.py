from collections import deque
import random
import string
import chatGPT
import os

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

    def _overall_token_count(self):
        return sum(self._token_count(channel_data['deque']) for channel_data in self._data.values())


    def _truncate_and_summarize(self, key):
        half_length = self.token_limit // 2
        messages_to_summarize = []
        for key in self._data:
            # Dequeue messages until roughly half of the token limit is reached
            while self._token_count(self._data[key]['deque']) > half_length // len(self._data):
                messages_to_summarize.append(self._data[key]['deque'].popleft())

        chatGPT.GPT_log_summary(messages_to_summarize)

    def append(self, key, message):
        if key not in self._data:
            self._data[key] = {'deque': deque()}

        # Check if the overall token count exceeds the token limit
        if (self._overall_token_count() + len(message["content"].split())) > self.token_limit:
            self._truncate_and_summarize()

        self._data[key]['deque'].append(message)

    def get_messages(self, key):
        if key not in self._data:
            self._data[key] = {'deque': deque()}
        return self._data[key]

    def __repr__(self):
        return str(self._data)

    def __getitem__(self, key):
        if key not in self._data:
            self._data[key] = deque()
        return self._data[key]