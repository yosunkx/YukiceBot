import socket
from pymilvus import connections, exceptions

alias = "milvus_connection"
server_ip = '192.168.0.110'  # IP of your server

# Get the IP address of the current machine
current_ip = socket.gethostbyname(socket.gethostname())

# If the current machine IP is the same as the server IP, set host to 'localhost'. Otherwise, set it to the server IP.
host = 'localhost' if current_ip == server_ip else server_ip
port = '19530'

try:
    connections.connect(
        alias=alias,
        host=host,
        port=port
    )
    print(f"Connected to Milvus server at {host}:{port} with alias '{alias}'")

except exceptions.ConnectionConnectError as e:
    print(f"Failed to connect to Milvus server at {host}:{port}")
    print(f"Error: {e}")

finally:
    try:
        connections.disconnect(alias)
        print(f"Disconnected from Milvus server with alias '{alias}'")
    except exceptions.ConnectionNotFoundError as e:
        print(f"Failed to disconnect because no connection with alias '{alias}' was found")
        print(f"Error: {e}")
