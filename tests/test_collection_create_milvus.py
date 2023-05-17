import asyncio
import socket
from pymilvus import connections, exceptions, CollectionSchema, FieldSchema, DataType, Collection, utility

alias = "default"
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

        collection_name = "sentence_transformer_collection"
        try:
            collection = Collection(collection_name)
            collection.drop()
            print(f"Collection {collection_name} dropped")
            # wait for the drop operation to complete
            while utility.has_collection(collection_name):
                print(f"Waiting for collection {collection_name} to drop")
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Error: {str(e)}")

        # Define the fields
        int_id = FieldSchema(
            name="int_id",
            dtype=DataType.INT64,
            is_primary=True,
        )

        vector = FieldSchema(
            name="vector",
            dtype=DataType.FLOAT_VECTOR,
            dim=384
        )

        # Create the collection schema
        schema = CollectionSchema(
            fields=[int_id, vector],
            description="Collection for sentence-transformer vectors"
        )

        # Check if the collection already exists
        if utility.has_collection(collection_name):
            print(f"Collection '{collection_name}' already exists.")
        else:
            # Create the collection
            collection = Collection(
                name=collection_name,
                schema=schema,
                using='default'  # This can be omitted if you only have one connection
            )
            print(f"Collection '{collection_name}' created")

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


async def main():
    await init_db()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
# Please note that when you insert data into the collection, the vectors must be list of lists, where each inner list
# is a vector of 384 dimensions, and the IDs must be a list of INT64 numbers.
