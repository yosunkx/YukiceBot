from collections import deque
import random
import string
import chatGPT
import os
import json
import asyncio
import ConsoleLog
import logging

logger = ConsoleLog.set_logging('mylog.log')
#use it like this: logger.info('log message')


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
        self.load_logs()
        self.lock = asyncio.Lock()

    def _token_count(self, messages):
        return sum(len(message["content"].split()) for message in messages)

    async def _truncate_and_summarize(self, key):
        logger.info("summarizing")
        half_length = self.token_limit // 2
        messages_to_summarize = []
        while self._token_count(self._data[key]['deque']) > half_length:
            messages_to_summarize.append(self._data[key]['deque'].popleft())

        summary = await chatGPT.GPT_log_summary(messages_to_summarize)
        self._data[key]['deque'].appendleft({'role': 'system', 'content': summary})
        self.save_logs()

    async def append(self, key, message):
        if key not in self._data:
            self._data[key] = {'deque': deque()}

        if (self._token_count(self._data[key]['deque']) + len(message["content"].split())) > self.token_limit:
            await self._truncate_and_summarize(key)

        self._data[key]['deque'].append(message)

    def get_messages(self, key):
        if key not in self._data:
            self._data[key] = {'deque': deque()}

        return self._data[key]

    def __repr__(self):
        return str(self._data)

    def __getitem__(self, key):
        if key not in self._data:
            self._data[key] = {'deque': deque()}
        return self._data[key]

    def save_logs(self):
        if not os.path.exists('memory'):
            os.mkdir('memory')

        for key, data in self._data.items():
            with open(f'memory/{str(key)}.json', 'w', encoding='utf-8') as f:
                json.dump(list(data['deque']), f)


    def load_logs(self):
        if not os.path.exists('memory'):
            return

        for filename in os.listdir('memory'):
            if filename.endswith('.json'):
                key = int(filename[:-5])
                with open(f'memory/{filename}', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._data[key] = {'deque': deque(data)}
                    logger.info(f"loaded memory: {key}")


if __name__ == "__main__":
    pass


