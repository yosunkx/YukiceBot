import asyncio
import json
import os


class FailedDataList:
    def __init__(self):
        self._data = {"SQL": [], "Milvus": []}
        self.load_logs()
        self.lock = asyncio.Lock()

    async def append(self, key, data):
        assert key in self._data, f"Invalid key: {key}. Valid keys are {list(self._data.keys())}"
        async with self.lock:
            self._data[key].append(data)
            self.save_logs()

    def get_failed_data(self, key):
        assert key in self._data, f"Invalid key: {key}. Valid keys are {list(self._data.keys())}"
        return self._data[key]

    def remove_failed_data(self, key, index):
        assert key in self._data, f"Invalid key: {key}. Valid keys are {list(self._data.keys())}"
        del self._data[key][index]
        self.save_logs()

    def save_logs(self):
        if not os.path.exists('data'):
            os.mkdir('data')

        for key, data in self._data.items():
            with open(f'data/{str(key)}.json', 'w', encoding='utf-8') as f:
                json.dump(data, f)
                print(f"saved failed logs: {key}")

    def load_logs(self):
        if not os.path.exists('data'):
            return

        for filename in os.listdir('data'):
            if filename.endswith('.json'):
                key = filename[:-5]
                with open(f'data/{filename}', 'r', encoding='utf-8') as f:
                    self._data[key] = json.load(f)
                    print(f"loaded failed logs: {key}")

    def __repr__(self):
        return str(self._data)

    def __getitem__(self, key):
        assert key in self._data, f"Invalid key: {key}. Valid keys are {list(self._data.keys())}"
        return self._data[key]
