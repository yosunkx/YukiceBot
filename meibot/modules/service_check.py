from discord.ext import commands
import discord
from pymilvus import connections, utility
import httpx
import os
import socket

server_ip = '192.168.0.110'
local_host = 'localhost'
milvus_port = '19530'
embedding_port = '8000'
SQLite_port = '8080'
mei_version = '0.1.2'
current_ip = socket.gethostbyname(socket.gethostname())

# Get value of environment variable 'DOCKER'. If it doesn't exist, default to False.
docker = os.getenv('DOCKER', False)

milvus_host = os.getenv('MILVUS_HOST', server_ip if current_ip == server_ip else local_host)
embedding_host = os.getenv('EMBEDDING_HOST', server_ip if current_ip == server_ip else local_host)
SQLite_host = os.getenv('SQLITE_HOST', server_ip if current_ip == server_ip else local_host)


async def check_milvus_status():
    try:
        connections.connect(
            alias="default",
            host=milvus_host,  # replace with your host
            port=milvus_port  # replace with your port
        )
        status = 'Online'
    except Exception as e:
        status = f"Failed to connect to Milvus server at {milvus_host}:{milvus_port}\nError: {e}"
    finally:
        connections.disconnect("default")

    return status


async def check_sqlite_status():
    base_url = f"http://{SQLite_host}:{SQLite_port}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/healthcheck")
            response.raise_for_status()
            health_status = response.json()
    except httpx.HTTPError as e:
        health_status = {"status": "server down"}
    return health_status


async def check_embedding_status():
    base_url = f"http://{embedding_host}:{embedding_port}"
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

    all_status = f"Milvus status: {milvus_status}\nSQLite status: {sqlite_status}\nEmbedding service status: " \
                 f"{embedding_status}\nCurrent ip: {current_ip}"
    await ctx.send(all_status)


@commands.command()
async def mei_ver(ctx):
    await ctx.send(mei_version)


def setup(bot):
    bot.add_command(service_check)
    bot.add_command(mei_ver)
