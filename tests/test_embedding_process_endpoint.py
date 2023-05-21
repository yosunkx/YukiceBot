import requests

url = "http://192.168.0.133:8000/process"

data = {
    "user_input": "https://en.wikipedia.org/wiki/GPT-4"
}

response = requests.post(url, json=data)

if response.status_code == 200:
    print("Request succeeded!")
    print(response.json())
else:
    print(f"Request failed with status code {response.status_code}")
    print(response.text)
