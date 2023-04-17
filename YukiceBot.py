import os
import asyncio
import openai
from dotenv import load_dotenv
import discord
from discord.ext import commands

load_dotenv()  # Load the environment variables from the .env file
token = os.getenv['DISCORD_BOT_TOKEN']
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

async def alarm_clock():
    await bot.wait_until_ready()

    server_name = 'Image'
    server = None

    for guild in bot.guilds:
        if guild.name == server_name:
            server = guild
            break

    if server is None:
        print(f"Server '{server_name}' not found.")
        return

    role_name = 'tof'
    role = discord.utils.get(server.roles, name=role_name)

    if role is None:
        print(f"Role '{role_name}' not found.")
        return

    while not bot.is_closed() and not alarmSent:
        # Check the current time, and determine if it's time to send the alarm
        if should_send_alarm():
            channel = get_alarm_channel(server)
            users_to_ping = get_users_with_role(role)
            users_to_skip = get_users_to_skip()  # Implement this function to read the user's preferences

            for user in users_to_ping:
                if user not in users_to_skip:
                    await channel.send(f"{user.mention}, it's time for Tower of Fantasy!")

        await asyncio.sleep(60)  # Sleep for 60 seconds before checking again

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

def should_send_alarm():
    # Implement this function to check if it's the correct time to send the alarm
    pass

def get_alarm_channel(server):
    # Implement this function to get the channel where you want to send the alarm
    pass

def get_users_with_role(role):
    return [member for member in role.members if not member.bot]

def get_users_to_skip():
    # Implement this function to read the preferences of the users who want to skip the alarm
    pass

bot.loop.create_task(alarm_clock())
bot.run(token)