import requests
import socket

server_ip = '192.168.0.110'  # IP of your server
port = '8080'
local_host = 'localhost'
# Get the IP address of the current machine
current_ip = socket.gethostbyname(socket.gethostname())

# If the current machine IP is the same as the server IP, set host to 'localhost'. Otherwise, set it to the server IP.
#if current_ip == server_ip:
#    host = 'localhost'
#else:
#    host = server_ip

base_url = f"http://{local_host}:{port}"

data = {
    'int_id': 12345,
    'text_chunk': "Hello, World!"
}

try:
    store_response = requests.post(f"{base_url}/store", json=data)
    store_response.raise_for_status()
    print(f"Store response: {store_response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Could not store data: {e}")

try:
    retrieve_response = requests.get(f"{base_url}/retrieve/12345")
    retrieve_response.raise_for_status()
    print(f"Retrieve response: {retrieve_response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Could not retrieve data: {e}")

try:
    delete_response = requests.delete(f"{base_url}/delete/12345")
    delete_response.raise_for_status()
    print(f"Delete response: {delete_response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Could not delete data: {e}")

try:
    retrieve_response = requests.get(f"{base_url}/retrieve/12345")
    retrieve_response.raise_for_status()
    print(f"Retrieve response after delete: {retrieve_response.json()}")
except requests.exceptions.RequestException as e:
    print(f"Could not retrieve data after delete: {e}")

try:
    response = requests.get(f"{base_url}/healthcheck")
    response.raise_for_status()
    health_status = response.json()
except requests.exceptions.RequestException as e:
    print(f"Could not connect to the server: {e}")
    health_status = {"status": "server down"}

print(f"Health status: {health_status}")
