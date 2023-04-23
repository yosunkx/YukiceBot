from mailbox import Message
import os
import asyncio
import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext import tasks
import modules
import modules.CalendarModule as CalenderModule
import modules.tof as tof
import MessageLog
import chatGPT
import signal
import modules.news as news

load_dotenv()
DISCORD_API_KEY = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!', '<@!1097341747459272845>'), intents=intents)

message_logs = MessageLog.MessageLogs()

AUTHORIZED_USER_ID = 104055116897722368

modules.setup_all_modules(bot)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    print('You can invite the bot by using the following url: ' + discord.utils.oauth_url(bot.user.id))
    CalenderModule.check_events.start(bot)

@bot.event
async def on_message(message):
    #valid channel ids to store as memory
    valid_channel_ids = {370007994831863810, 1098848230118260746}

    if message.channel.id in valid_channel_ids:
        if message.author == bot.user:
            print("Appending assistant message:", message.content)  # Add this line
            await message_logs.append(message.guild.id, {"role": "assistant", "content": message.content})
            return
        else:
            print("Appending user message:", message.author.name + ": " + message.content)  # Add this line
            await message_logs.append(message.guild.id, {"role": "user", "content": message.author.name + ": " + message.content})

    ctx = await bot.get_context(message)

    # Check if the message is a reply to a bot message
    if message.reference:
        referenced_message = await message.channel.fetch_message(message.reference.message_id)
        if referenced_message.author == bot.user:
            # Split the message content into words
            words = message.content.split()

            # Check if the reply content starts with a valid command
            command_name = words[0]
            if command_name in bot.all_commands:
                # Set the message content to include the command arguments (excluding the command name)
                message.content = " ".join(words[1:]) if len(words) > 1 else ""

                # Create a new context and set the command prefix as the reply 
                ctx = await bot.get_context(message)
                ctx.prefix = ""
                ctx.command = bot.all_commands[command_name]

                # Invoke the command as if the user sent a normal command like `!event` or `/event`
                await bot.invoke(ctx)
                return
            else:
                await none_command(message, ctx, list(message_logs.get_messages(ctx.guild.id)['deque']))

    # Process other messages
    if ctx.command is None:
        # Check if the message starts with any command prefix
        prefixes = bot.command_prefix(bot, message)
        if isinstance(prefixes, str):
            prefixes = [prefixes]
        if any(message.content.startswith(prefix) for prefix in prefixes):
            # If the message starts with a mention of the bot
            mention_prefix = f"<@{bot.user.id}>"
            user_message = message.content
            if user_message.startswith(mention_prefix):
                user_message = user_message[len(mention_prefix):].strip()
            if user_message:
                await none_command(message, ctx, list(message_logs.get_messages(ctx.guild.id)['deque']))
            return
        else:
            # If the message starts with a mention of the bot
            mention_prefix = f"<@!{bot.user.id}>"
            if message.content.startswith(mention_prefix):
                stripped_message = message.content[len(mention_prefix):].strip()
                if stripped_message:
                    await none_command(message, ctx, list(message_logs.get_messages(ctx.guild.id)['deque']))
                    return
    else:
        # If the message starts with a valid command, process it 
        await bot.process_commands(message)


async def none_command(message, ctx, logs):
    generated_message = await chatGPT.GPT_command(message.content)

    if generated_message.strip().startswith("!"):
        #print("gpt output starts with !")
        command_message = generated_message.split()[0][1:]  # Remove the '!' from the command
        command_message = command_message[0] + command_message[1:].replace(".", "")
        words = command_message.split()
        command = words[0]
        args = generated_message.split()[1:]  # Get the arguments, if any
        # Check if the command exists and invoke it
        if command in bot.all_commands:
            cmd_obj = bot.get_command(command)
            ctx = await bot.get_context(message)
            #print("invoking command")
            await ctx.invoke(cmd_obj, *args)
        else:
            #print("not valid command, output as normal message")
            generated_none_command = await chatGPT.GPT_general(message.content, message.author.name, list(logs))
            await ctx.send(generated_none_command)
    else:
        #print("normal message")
        generated_none_command = await chatGPT.GPT_general(message.content, message.author.name, list(logs))
        await ctx.send(generated_none_command)


@bot.command(name="print_log")
async def print_log(ctx):
    guild_id = ctx.guild.id

    # Fetch the message logs for the current server
    logs = message_logs.get_messages(guild_id)['deque']

    # Print the message logs to the console
    print("Message logs for server:", guild_id)
    for message in logs:
        print(f"{message['role']}: {message['content']}")

        
def signal_handler(signal, frame):
    print("Stopping the bot...")
    loop = asyncio.get_event_loop()
    loop.stop()


@bot.command()
async def close_bot(ctx):
    # Check if the user's ID matches the authorized userID
    if ctx.author.id != AUTHORIZED_USER_ID:
        await ctx.send("You do not have permission to use this command.")
        return

    message_logs.save_logs()

    # Send a message to notify that the bot will be closed
    await ctx.send("The bot will now close.")

    await asyncio.sleep(1)

    # Use the custom signal handler to close the bot
    os.kill(os.getpid(), signal.SIGINT)

signal.signal(signal.SIGINT, signal_handler)
bot.run(DISCORD_API_KEY)