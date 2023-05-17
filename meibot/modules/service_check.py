from discord.ext import commands
import discord
from pymilvus import connections, utility
import socket
import httpx

server_ip = '192.168.0.110'
milvus_port = '19530'
embedding_port = '8000'
SQLite_port = '8080'
host = 'localhost'


async def check_milvus_status():
    try:
        connections.connect(
            alias="default",
            host=host,  # replace with your host
            port=milvus_port  # replace with your port
        )
        status = utility.get_info()
        return status
    finally:
        connections.disconnect("default")


async def check_sqlite_status():
    base_url = f"http://{host}:{SQLite_port}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/healthcheck")
            response.raise_for_status()
            health_status = response.json()
    except httpx.HTTPError as e:
        health_status = {"status": "server down"}
    return health_status


async def check_embedding_status():
    base_url = f"http://{host}:{embedding_port}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/healthcheck")
            response.raise_for_status()
            health_status = response.json()
    except httpx.HTTPError as e:
        health_status = {"status": "server down"}
    return health_status


@commands.command()
async def service_check(ctx):
    milvus_status = await check_milvus_status()
    sqlite_status = await check_sqlite_status()
    embedding_status = await check_embedding_status()
    current_ip = socket.gethostbyname(socket.gethostname())

    all_status = f"Milvus status: {milvus_status}\nSQLite status: {sqlite_status}\nEmbedding service status: {embedding_status}\nCurrent ip: {current_ip}"
    await ctx.send(all_status)


def setup(bot):
    bot.add_command(service_check)