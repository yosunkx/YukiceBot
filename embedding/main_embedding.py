import asyncio
from .modules import embedding_transformer, wikipedia_url_handler
from .modules import failed_data_list as fdl
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx


class UserInput(BaseModel):
    user_input: str


app = FastAPI()
failed_data_list = fdl.FailedDataList()
retry_task = None


async def retry_failed_requests():
    global retry_task
    while failed_data_list:
        for key in ["SQL", "Milvus"]:
            if failed_data_list.get_failed_data(key):
                async with httpx.AsyncClient() as client:
                    for i, data_dict in enumerate(failed_data_list.get_failed_data(key)):
                        try:
                            # Define the URL based on the database
                            url = "http://sqlite:8000" if key == "SQL" else "http://milvus:8000"
                            response = await client.post(url, json=data_dict)
                            response.raise_for_status()
                            failed_data_list.remove_failed_data(key, i)
                        except httpx.HTTPError as exc:
                            print(f"Request failed: {exc}")
                            await asyncio.sleep(20)
                            break  # Stop the current loop and wait for the next iteration
        await asyncio.sleep(20)  # Wait 20 seconds before retrying
    retry_task = None  # Reset the task when done


@app.on_event("startup")
async def startup_event():
    global retry_task
    if failed_data_list and not retry_task:
        retry_task = asyncio.create_task(retry_failed_requests())


@app.post("/process")
async def process_data(user_input):
    data_list_sql, data_list_milvus = await prepare_data(user_input)

    if not data_list_sql:
        print('invalid input format')
        raise HTTPException(status_code=400, detail="Invalid input format")

    await send_to_databases(data_list_sql, data_list_milvus)


async def prepare_data(user_input):
    data_list_sql = []
    data_list_milvus = []

    if 'wiki' in user_input:
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
                data_dict_milvus = {
                    'embedding': embeddings[i],
                    'index': indexes[i]
                }
                data_list_sql.append(data_dict_sql)
                data_list_milvus.append(data_dict_milvus)

        print('finished embedding')

    return data_list_sql, data_list_milvus


async def send_to_databases(data_list_sql, data_list_milvus):
    global retry_task
    async with httpx.AsyncClient() as client:
        for data_dict in data_list_sql:
            try:
                response = await client.post("http://sqlite:8000/store", json=data_dict)
                response.raise_for_status()  # Raises an HTTPError if the status is 4xx, 5xx
                print(f"Response: {response.json()}")  # log the response
            except httpx.HTTPError as exc:
                print(f"Request failed: {exc}")
                await failed_data_list.append('SQL', data_dict)
        for data_dict in data_list_milvus:
            pass
            #try:
            #except:
                #await failed_data_list.append('Milvus', data_dict)

    if failed_data_list and not retry_task:
        retry_task = asyncio.create_task(retry_failed_requests())
