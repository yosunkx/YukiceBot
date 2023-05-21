import requests
import socket

server_ip = '192.168.0.133'  # IP of your server
port = '8000'
# Get the IP address of the current machine
current_ip = socket.gethostbyname(socket.gethostname())


host = 'localhost'


base_url = f"http://{server_ip}:{port}"

try:
    response = requests.get(f"{base_url}/healthcheck")
    response.raise_for_status()
    health_status = response.json()
except requests.exceptions.RequestException as e:
    print(f"Could not connect to the server: {e}")
    health_status = {"status": "server down"}

print(f"Health status: {health_status}")
