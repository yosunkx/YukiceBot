from collections import deque
import random
import string
from . import ConsoleLog, chatGPT
import os
import json
import asyncio

logger = ConsoleLog.set_logging('mylog.log')


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
            logger.debug("Queue is empty, cannot dequeue.")

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def peek(self):
        if not self.is_empty():
            return self.items[0]
        else:
            logger.debug("Queue is empty, cannot peek.")

    def print(self):
        if self.is_empty():
            logger.debug('empty ID')
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
        if not os.path.exists('data/memory'):
            os.mkdir('data/memory')

        for key, data in self._data.items():
            with open(f'data/memory/{str(key)}.json', 'w', encoding='utf-8') as f:
                json.dump(list(data['deque']), f)
                logger.info(f"saved memory: {key}")

    def load_logs(self):
        if not os.path.exists('data/memory'):
            return

        for filename in os.listdir('data/memory'):
            if filename.endswith('.json'):
                key = int(filename[:-5])
                with open(f'data/memory/{filename}', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._data[key] = {'deque': deque(data)}
                    logger.info(f"loaded memory: {key}")

    @property
    def data(self):
        return self._data


class EmbeddingMessageLogs:
    def __init__(self):
        self._data = {}
        self.load_logs()
        self.lock = asyncio.Lock()

    async def append(self, key, message):
        if key not in self._data:
            self._data[key] = deque()  # Initialize a new deque for this key
        self._data[key].append(message)

    def get_messages(self, key):
        if key not in self._data:
            self._data[key] = deque()  # Initialize a new deque for this key
        return list(self._data[key])

    def __repr__(self):
        return str(self._data)

    def __getitem__(self, key):
        if key not in self._data:
            self._data[key] = deque()  # Initialize a new deque for this key
        return list(self._data[key])

    def save_logs(self):
        if not os.path.exists('data/embedding_memory'):
            os.mkdir('data/embedding_memory')

        for key, data in self._data.items():
            with open(f'data/embedding_memory/{str(key)}.json', 'w', encoding='utf-8') as f:
                json.dump(list(data), f)
                logger.info(f"saved embed logs: {key}")

    def load_logs(self):
        if not os.path.exists('data/embedding_memory'):
            return

        for filename in os.listdir('data/embedding_memory'):
            if filename.endswith('.json'):
                key = int(filename[:-5])
                with open(f'data/embedding_memory/{filename}', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._data[key] = deque(data)
                    logger.info(f"loaded embed logs: {key}")
