import os
import asyncio
import openai
from dotenv import load_dotenv
import discord
from discord.ext import commands
import CalendarModule

load_dotenv()  # Load the environment variables from the .env file
DISCORD_API_KEY = os.getenv('DISCORD_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!'), intents=intents)
openai.api_key = OPENAI_API_KEY

alarmSent = False

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    print('You can invite the bot by using the following url: ' + discord.utils.oauth_url(bot.user.id))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    print(f'Received message: {message.content}')

    # Check if the message is a command
    ctx = await bot.get_context(message)
    is_command = ctx.valid

    print(f'This message is a bot command: {is_command}')

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

bot.run(DISCORD_API_KEY)