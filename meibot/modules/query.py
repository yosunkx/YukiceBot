from discord.ext import commands
import discord
import httpx
import os
import socket
import asyncio
from pymilvus import connections, exceptions, CollectionSchema, FieldSchema, DataType, Collection, utility
from . import ConsoleLog

logger = ConsoleLog.set_logging('mylog.log')

server_ip = '192.168.0.133'
local_host = 'localhost'
milvus_port = '19530'
milvus_alias = 'default'
current_ip = socket.gethostbyname(socket.gethostname())

# Get value of environment variable 'DOCKER'. If it doesn't exist, default to False.
docker = os.getenv('DOCKER', False)

milvus_host = os.getenv('EMBEDDING_HOST', server_ip if current_ip != server_ip else local_host)


@commands.command()
async def query(ctx, query_request: str = None):
    if query_request is None:
        await ctx.send("invalid request")
        return
    try:
        connections.connect(
            alias=milvus_alias,
            host=milvus_host,
            port=milvus_port
        )
        logger.debug(f"Connected to Milvus server at {milvus_host}:{milvus_port} with alias '{milvus_alias}'")

    except Exception as e:
        logger.debug(f"Failed to connect to Milvus server at {milvus_host}:{milvus_port}")
        logger.debug(f"Error: {e}")

    finally:
        try:
            connections.disconnect(milvus_alias)
            logger.debug(f"Disconnected from Milvus server with alias '{milvus_alias}'")
        except exceptions.ConnectionNotFoundError as e:
            logger.debug(f"Failed to disconnect because no connection with alias '{milvus_alias}' was found")
            logger.debug(f"Error: {e}")


def setup(bot):
    bot.add_command(query)

