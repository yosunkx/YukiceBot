import asyncio
import socket
from pymilvus import connections, exceptions, CollectionSchema, FieldSchema, DataType, Collection, utility

alias = "milvus_connection"
server_ip = '192.168.0.110'  # IP of your server

# Get the IP address of the current machine
current_ip = socket.gethostbyname(socket.gethostname())

# If the current machine IP is the same as the server IP, set host to 'localhost'. Otherwise, set it to the server IP.
host = 'localhost' if current_ip == server_ip else server_ip
port = '19530'


async def init_db():
    try:
        connections.connect(
            alias=alias,
            host=host,
            port=port
        )
        print(f"Connected to Milvus server at {host}:{port} with alias '{alias}'")

    finally:
        try:
            connections.disconnect(alias)
            print(f"Disconnected from Milvus server with alias '{alias}'")
        except exceptions.ConnectionNotFoundError as e:
            print(f"Failed to disconnect because no connection with alias '{alias}' was found")
            print(f"Error: {e}")


async def main():
    await init_db()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
# Please note that when you insert data into the collection, the vectors must be list of lists, where each inner list
# is a vector of 384 dimensions, and the IDs must be a list of INT64 numbers.
