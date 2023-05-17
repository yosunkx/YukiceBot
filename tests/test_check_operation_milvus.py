import asyncio
import socket
from pymilvus import connections, exceptions, CollectionSchema, FieldSchema, DataType, Collection, utility
import numpy as np

alias = "default"
server_ip = '192.168.0.110'  # IP of your server

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
        collections = utility.list_collections()
        print(f"Collections: {collections}")
    except Exception as e:
        print(f"Failed to list collections: {e}")

    test_vector1 = np.random.uniform(-1, 1, 384).tolist()
    test_vector2 = np.random.uniform(-1, 1, 384).tolist()
    test_vectors = [test_vector1, test_vector2]
    indexes = [100, 200]
    data = [
        indexes,
        test_vectors,
    ]
    try:
        collection_name = "sentence_transformer_collection"
        collection = Collection(collection_name)
        print(f"collection obtained: {collection_name}")
    except Exception as e:
        print(f"failed to get collection: {collection_name}")

    try:
        mr = collection.insert(data)
        collection.flush()
        print("data inserted")
    except Exception as e:
        print("failed to insert data")

    try:
        expr = "int_id in [100,200]"
        collection.delete(expr)
        print("data deleted")
    except Exception as e:
        print("failed to delete")


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
