from discord.ext import commands
import discord
import httpx
import os
import socket

server_ip = '192.168.0.133'
local_host = 'localhost'
embedding_port = '8000'
current_ip = socket.gethostbyname(socket.gethostname())

# Get value of environment variable 'DOCKER'. If it doesn't exist, default to False.
docker = os.getenv('DOCKER', False)

embedding_host = os.getenv('EMBEDDING_HOST', server_ip if current_ip != server_ip else local_host)


@commands.command()
async def embed(ctx, embed_request: str = None):
    if embed_request is None:
        await ctx.send("invalid request")
        return
    base_url = f"http://{embedding_host}:{embedding_port}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{base_url}/process", json={'user_input': embed_request})
            response.raise_for_status()
            status = response.json()
    except httpx.HTTPStatusError as exc:
        status = {"status": f"HTTP error occurred: {exc}"}
    except httpx.RequestError as exc:
        status = {"status": f"An error of type {type(exc).__name__} occurred while requesting: {exc}"}

    except Exception as exc:
        status = {"status": f"An unexpected error occurred: {exc}"}

    await ctx.send(status["status"])


def setup(bot):
    bot.add_command(embed)

