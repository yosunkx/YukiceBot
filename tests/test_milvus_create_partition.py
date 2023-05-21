import asyncio
import socket
from pymilvus import connections, exceptions, CollectionSchema, FieldSchema, DataType, Collection, utility
import numpy as np

alias = "default"
server_ip = '192.168.0.133'  # IP of your server

# Get the IP address of the current machine
current_ip = socket.gethostbyname(socket.gethostname())

# If the current machine IP is the same as the server IP, set host to 'localhost'. Otherwise, set it to the server IP.
host = 'localhost' if current_ip == server_ip else server_ip
port = '19530'

try:
    connections.connect(
        alias="default",
        host=host,
        port=port
    )
    print(f"Connected to Milvus server at {host}:{port} with alias '{alias}'")

    try:
        collection_name = "sentence_transformer_collection"
        collection = Collection(collection_name)
        print(f"connected to collection: {collection_name}")
        partition_1_name = "message_log"
        partition_2_name = "documents"
        if collection.has_partition(partition_1_name):
            print(f"partition already exists: {partition_1_name}")
        else:
            collection.create_partition(partition_1_name)
            print(f"partition created: {partition_1_name}")
        if collection.has_partition(partition_2_name):
            print(f"partition already exists: {partition_2_name}")
        else:
            collection.create_partition(partition_2_name)
            print(f"partition created: {partition_2_name}")
    except Exception as e:
        print(f"Failed to list collections: {e}")

except Exception as e:
    print(f"Failed to connect to Milvus server at {host}:{port}")
    print(f"Error: {e}")

finally:
    try:
        connections.disconnect(alias)
        print(f"Disconnected from Milvus server with alias '{alias}'")
    except exceptions.ConnectionNotFoundError as e:
        print(f"Failed to disconnect because no connection with alias '{alias}' was found")
        print(f"Error: {e}")
