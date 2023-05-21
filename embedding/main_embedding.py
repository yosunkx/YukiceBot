import asyncio
from modules import embedding_transformer, wikipedia_url_handler
from modules import failed_data_list as fdl
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, ValidationError
from pymilvus import connections, exceptions, Collection
import httpx
import socket

server_ip = '192.168.0.110'  # IP of your server


class UserInput(BaseModel):
    user_input: str


app = FastAPI()
failed_data_list = fdl.FailedDataList()
retry_task = None
current_ip = socket.gethostbyname(socket.gethostname())
host = 'localhost' if current_ip == server_ip else server_ip
milvus_port = '19530'

partition_1_name = "message_log"
partition_2_name = "documents"


async def send_to_sql(data_list):
    async with httpx.AsyncClient() as client:
        for data_dict in data_list:
            response = await client.post("http://sqlite:8080/store", json=data_dict)
            response.raise_for_status()  # Raises an HTTPError if the status is 4xx, 5xx
            print(f"Response: {response.json()}")  # log the response


async def send_to_milvus(data_list, milvus_partition):
    try:
        connections.connect(
            alias="default",
            host=host,
            port=milvus_port
        )
        print(f"Connected to Milvus server at {host}:{milvus_port} with alias 'default'")
        try:
            collection_name = "sentence_transformer_collection"
            collection = Collection(collection_name)
            print(f"collection obtained: {collection_name}")
            mr = collection.insert(data_list, milvus_partition)
            collection.flush()
            print("data inserted")
        except Exception as e:
            print("failed to insert data")
            raise e

    except Exception as e:
        print(f"Failed to connect to Milvus server at {host}:{milvus_port}")
        print(f"Error: {e}")

    finally:
        try:
            connections.disconnect("default")
            print(f"Disconnected from Milvus server with alias 'default'")
        except exceptions.ConnectionNotFoundError as e:
            print(f"Failed to disconnect because no connection with alias 'default' was found")
            print(f"Error: {e}")


async def retry_failed_requests():
    global retry_task
    sleep_timer = 20
    max_sleep_timer = 7200  # 2 hours
    while failed_data_list:
        for key in ["SQL", "Milvus"]:
            if failed_data_list.get_failed_data(key):
                for i, data_dict in enumerate(failed_data_list.get_failed_data(key)):
                    try:
                        if key == "SQL":
                            await send_to_sql(data_dict)
                        elif key == "Milvus":
                            await send_to_milvus(data_dict)
                        await failed_data_list.remove_failed_data(key, i)
                        sleep_timer = 20  # Reset the timer after a successful request
                    except httpx.HTTPError as exc:
                        print(f"Request failed: {exc}")
                        await asyncio.sleep(sleep_timer)
                        if sleep_timer < max_sleep_timer:  # doubles sleep timer on fail
                            sleep_timer = min(2 * sleep_timer, max_sleep_timer)
                        break  # Stop the current loop and wait for the next iteration
        await asyncio.sleep(20)  # Wait 20 seconds before retrying
    retry_task = None  # Reset the task when done


@app.on_event("startup")
async def startup_event():
    global retry_task
    if not failed_data_list.is_empty() and not retry_task:
        retry_task = asyncio.create_task(retry_failed_requests())


@app.post("/process")
async def process_data(user_input: str):
    try:
        data_list_sql, data_list_milvus, milvus_partition = await prepare_data(user_input)
    except ValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input format")

    if not data_list_sql:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid input format")

    try:
        await send_to_databases(data_list_sql, data_list_milvus, milvus_partition)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {exc}")

    return {"status": "success"}


async def prepare_data(user_input):
    data_list_sql = []
    milvus_list_vector = []
    milvus_list_id = []
    milvus_partition = ''

    if 'wiki' in user_input:
        milvus_partition = partition_2_name
        data = await wikipedia_url_handler.scrape_wikipedia(user_input)
        print('embedding')
        for item in data:
            item_title = item['title']
            item_section = item['section']
            item_text = item['text']

            embeddings, texts, indexes = await embedding_transformer.async_encode(item_text, item_title, item_section)

            for i in range(len(embeddings)):
                data_dict_sql = {
                    'index': indexes[i],
                    'text_chunk': texts[i]
                }
                milvus_list_vector.append(embeddings[i])
                milvus_list_id.append(indexes[i])
                data_list_sql.append(data_dict_sql)

        data_list_milvus = [milvus_list_id, milvus_list_vector]
        print('finished embedding')

    return data_list_sql, data_list_milvus, milvus_partition


async def send_to_databases(data_list_sql, data_list_milvus, milvus_partition):
    global retry_task
    try:
        await send_to_sql(data_list_sql)
    except Exception as exc:  # Catch general exceptions, not just httpx.HTTPError
        print(f"Request failed: {exc}")
        await failed_data_list.append('SQL', data_list_milvus)

    try:
        await send_to_milvus(data_list_milvus, milvus_partition)
    except Exception as exc:  # Catch general exceptions, not just httpx.HTTPError
        print(f"Request failed: {exc}")
        await failed_data_list.append('Milvus', data_list_milvus)

    if failed_data_list and not retry_task:
        retry_task = asyncio.create_task(retry_failed_requests())


@app.post("/clear_failed_tasks")
async def clear_failed_tasks():
    await failed_data_list.clear()
    return {"status": "Failed tasks cleared"}


@app.get("/healthcheck")
async def healthcheck():
    # The server is running if it reaches this point
    status = {
        "status": "running",
        "failed_task_count": {
            "SQL": len(failed_data_list.get_failed_data("SQL")),
            "Milvus": len(failed_data_list.get_failed_data("Milvus")),
        }
    }
    return status
