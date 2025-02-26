from fastapi import FastAPI
import asyncio
import aiosqlite
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    int_id: int
    text_chunk: str


async def init_db():
    try:
        async with aiosqlite.connect('/var/lib/sqlite/my_database.db') as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS my_table (
                    int_id INTEGER PRIMARY KEY,
                    text_chunk TEXT
                )
            """)
            await db.commit()
    except Exception as e:
        print(f"An error occurred while initializing the database: {e}")


async def store_to_db(int_id: int, text_chunk: str):
    try:
        async with aiosqlite.connect('/var/lib/sqlite/my_database.db') as db:
            await db.execute("INSERT INTO my_table (int_id, text_chunk) VALUES (?, ?)", (int_id, text_chunk))
            await db.commit()
    except Exception as e:
        print(f"An error occurred while storing data: {e}")


async def retrieve_from_db(int_id: int):
    try:
        async with aiosqlite.connect('/var/lib/sqlite/my_database.db') as db:
            cursor = await db.execute("SELECT text_chunk FROM my_table WHERE int_id = ?", (int_id,))
            row = await cursor.fetchone()
            if row is None:
                return None
            return row[0]
    except Exception as e:
        print(f"An error occurred while retrieving data: {e}")


async def delete_from_db(int_id: int):
    try:
        async with aiosqlite.connect('/var/lib/sqlite/my_database.db') as db:
            await db.execute("DELETE FROM my_table WHERE int_id = ?", (int_id,))
            await db.commit()
    except Exception as e:
        print(f"An error occurred while deleting data: {e}")


async def check_storage():
    try:
        async with aiosqlite.connect('/var/lib/sqlite/my_database.db') as db:
            cursor = await db.execute("SELECT COUNT(*) FROM my_table")
            row_count = await cursor.fetchone()
        return row_count[0]
    except Exception as e:
        print(f"An error occurred while retrieving storage: {e}")
        return None


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.post("/store")
async def store(item: Item):
    await store_to_db(item.int_id, item.text_chunk)
    return {"message": "Data stored successfully"}


@app.get("/retrieve/{int_id}")
async def retrieve(int_id: int):
    result = await retrieve_from_db(int_id)
    if result is None:
        return {"message": "No data found for the given int_id"}
    else:
        return {"int_id": int_id, "text_chunk": result}


@app.delete("/delete/{int_id}")
async def delete(int_id: int):
    await delete_from_db(int_id)
    return {"message": "Data deleted successfully"}


@app.get("/healthcheck")
async def healthcheck():
    try:
        async with aiosqlite.connect('/var/lib/sqlite/my_database.db') as db:
            cursor = await db.execute("SELECT 1")
            await cursor.fetchone()
            storage = await check_storage()
        return {"status": "ok", "storage": storage}
    except Exception as e:
        print(f"An error occurred during health check: {e}")
        return {"status": "error"}, 500


@app.delete("/storage")
async def delete_all():
    try:
        async with aiosqlite.connect('/var/lib/sqlite/my_database.db') as db:
            await db.execute("DELETE FROM my_table")
            await db.commit()
        return {"status": "ok"}
    except Exception as e:
        print(f"An error occurred during deleting storage: {e}")
        return {"status": "error"}, 500
