import os
import asyncio
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext import tasks
import modules
from modules import MessageLog, chatGPT, ConsoleLog
from datetime import datetime
import modules.CalendarModule as CalenderModule
import signal
import re

load_dotenv()
DISCORD_API_KEY = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!', '<@!1097341747459272845>'), intents=intents)

message_logs = MessageLog.MessageLogs()
message_logs_for_embedding = MessageLog.EmbeddingMessageLogs()

AUTHORIZED_USER_ID = 104055116897722368

modules.setup_all_modules(bot)

logger = ConsoleLog.set_logging('mylog.log')


@bot.event
async def on_ready():
    logger.info('Logged in as {0.user}'.format(bot))
    logger.info('You can invite the bot by using the following url: ' + discord.utils.oauth_url(bot.user.id))
    CalenderModule.check_events.start(bot)


@tasks.loop(hours=5)
async def periodic_save():
    message_logs.save_logs()
    message_logs_for_embedding.save_logs()


@bot.event
async def on_message(message_obj):
    # valid channel ids to store as memory
    valid_channel_ids = {370007994831863810, 1102494872356786227, 1097616064407408651}
    message_log_channel_ids = {370007994831863810, 1102494872356786227}
    processed_content = await process_message_content(message_obj)

    if message_obj.channel.id in valid_channel_ids:
        async with message_logs.lock:
            now = datetime.utcnow()
            timestamp = now.strftime("%Y-%m-%d-%H:%M") + " UTC"
            if message_obj.author == bot.user:
                logger.debug("Mei: " + processed_content)
                if message_obj.channel.id in message_log_channel_ids:
                    await message_logs.append(message_obj.guild.id, {"role": "assistant", "content": "Mei: " + processed_content})
                    await message_logs_for_embedding.append(message_obj.guild.id, f"{timestamp} UTC Mei: {processed_content}")
                return
            else:
                logger.debug(message_obj.author.name + ": " + processed_content)
                if message_obj.channel.id in message_log_channel_ids:
                    await message_logs.append(message_obj.guild.id, {"role": "user", "content": message_obj.author.name + ": " + processed_content})
                    await message_logs_for_embedding.append(message_obj.guild.id, f"{timestamp} UTC {message_obj.author.name}: {processed_content}")
    else:
        return

    ctx = await bot.get_context(message_obj)

    # Check if the message is a reply to a bot message
    if message_obj.reference:
        referenced_message = await message_obj.channel.fetch_message(message_obj.reference.message_id)
        if referenced_message.author == bot.user:
            # Split the message content into words
            words = message_obj.content.split()

            # Check if the reply content starts with a valid command
            command_name = words[0]
            if command_name in bot.all_commands:
                # Set the message content to include the command arguments (excluding the command name)
                message_obj.content = " ".join(words[1:]) if len(words) > 1 else ""

                # Create a new context and set the command prefix as the reply 
                ctx = await bot.get_context(message_obj)
                ctx.prefix = ""
                ctx.command = bot.all_commands[command_name]

                # Invoke the command as if the user sent a normal command like `!event` or `/event`
                await bot.invoke(ctx)
                return
            else:
                await none_command(message_obj, processed_content,
                                   list(message_logs.get_messages(ctx.guild.id)['deque'])[:-1])

    # Process other messages
    if ctx.command is None:
        # Check if the message starts with any command prefix
        prefixes = bot.command_prefix(bot, message_obj)
        if isinstance(prefixes, str):
            prefixes = [prefixes]
        if any(message_obj.content.startswith(prefix) for prefix in prefixes):
            # If the message starts with a mention of the bot
            mention_prefix = f"<@{bot.user.id}>"
            user_message = message_obj.content
            if user_message.startswith(mention_prefix):
                user_message = user_message[len(mention_prefix):].strip()
            if user_message:
                await none_command(message_obj, processed_content,
                                   list(message_logs.get_messages(ctx.guild.id)['deque'])[:-1])
            return
        else:
            # If the message starts with a mention of the bot
            mention_prefix = f"<@!{bot.user.id}>"
            if message_obj.content.startswith(mention_prefix):
                stripped_message = message_obj.content[len(mention_prefix):].strip()
                if stripped_message:
                    await none_command(message_obj, processed_content,
                                       list(message_logs.get_messages(ctx.guild.id)['deque'])[:-1])
                    return
    else:
        # If the message starts with a valid command, process it 
        await bot.process_commands(message_obj)


async def none_command(message_obj, message_text, logs):
    generated_message = await chatGPT.GPT_command(message_obj.content)
    gpt_message = message_obj.author.name + ": " + message_text
    ctx = await bot.get_context(message_obj)
    # print("Logs before passing to GPT_general: ", logs)

    if generated_message.strip().startswith("!"):
        logger.debug("gpt output starts with !")
        command_message = generated_message.split()[0][1:]  # Remove the '!' from the command
        command_message = command_message[0] + command_message[1:].replace(".", "")
        words = command_message.split()
        command = words[0]
        args = generated_message.split()[1:]  # Get the arguments, if any
        # Check if the command exists and invoke it
        if command in bot.all_commands:
            cmd_obj = bot.get_command(command)
            logger.debug("invoking command")
            await ctx.invoke(cmd_obj, *args)
        else:
            logger.debug("not valid command, output as normal message")
            generated_none_command = await chatGPT.GPT_mei(gpt_message, logs)
            # await gpt_time_out(bot, generated_none_command, message_obj)
            await ctx.send(generated_none_command)
    else:
        logger.debug("normal message")
        generated_none_command = await chatGPT.GPT_mei(gpt_message, logs)
        # await gpt_time_out(bot, generated_none_command, message_obj)
        await ctx.send(generated_none_command)


@bot.command()
async def time_out(ctx, member: discord.Member, timeout_duration=30, gpt_invoke=False):
    if not gpt_invoke and ctx.author.id != AUTHORIZED_USER_ID and ctx.author.id != ctx.bot.user.id:
        await ctx.send("You do not have permission to use this command.")
        return

    muted_role = discord.utils.get(ctx.guild.roles, name="muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)

    await member.add_roles(muted_role)
    await ctx.send(f"{member.mention} has been timed out for {timeout_duration} seconds.")
    await asyncio.sleep(timeout_duration)
    await member.remove_roles(muted_role)


"""async def gpt_time_out(bot_obj, mei_response_string, message_obj):
    prompt = [
        {"role": "system",
         "content": "You are now a robot that is only capable of outputting numbers. on a scale of 1 to 10 from not annoyed to very annoyed, how annoyed do you think is Mei? Answer your best guess and only respond with a number."},
        {"role": "user", "content": "Mei: " + mei_response_string}
    ]
    response_string = await chatGPT.chat_completion(messages=prompt, max_tokens=40, temperature=0.3)
    logger.info(f"annoyance: {response_string}")

    if any(str(num) in response_string for num in range(8, 11)):
        ctx = await bot_obj.get_context(message_obj)
        author = message_obj.author
        await time_out(ctx, author, gpt_invoke=True)
    else:
        return"""


@bot.command(name="print_log")
async def print_log(ctx):
    guild_id = ctx.guild.id

    # Fetch the message logs for the current server
    logs = message_logs.get_messages(guild_id)['deque']

    # Print the message logs to the console
    logger.info(f"Message logs for server: {guild_id}")
    for message in logs:
        print(f"{message['role']}: {message['content']}")


@bot.command(name="print_full_log")
async def print_full_log(ctx):
    # Iterate through all the keys and their associated message logs
    for key, data in message_logs.data.items():
        logs = data['deque']

        # Print the message logs for the current key
        logger.info(f"Message logs for key: {key}")
        for message in logs:
            print(f"{message['role']}: {message['content']}")
        print()  # Add an empty line to separate logs from different keys


async def process_message_content(message_obj):
    guild_obj = message_obj.guild
    message_text = message_obj.content

    def repl_user_id(match):
        user_id = int(match.group(1))
        member = guild_obj.get_member(user_id)
        if member is not None:
            if member.nick is not None:
                return f"@{member.nick}"
            else:
                return f"@{member.display_name}"
        else:
            return f"@{match.group(0)}"

    def repl_role_id(match):
        role_id = int(match.group(1))
        role = discord.utils.get(guild_obj.roles, id=role_id)
        return f"@{role.name}" if role is not None else f"@{match.group(0)}"

    def repl_channel_id_link(match):
        channel_id = int(match.group(1))
        channel = guild_obj.get_channel(channel_id)
        if channel is not None:
            return f"#{channel.name}"
        else:
            return f"#{match.group(0)}"

    def repl_channel_id_wrap(match):
        channel_id = int(match.group(1))
        channel = guild_obj.get_channel(channel_id)
        return f"#{channel.name}" if channel is not None else f"#{match.group(0)}"

    message_text = re.sub(r'<@(\d+)>', repl_user_id, message_text)
    message_text = re.sub(r'<@&(\d+)>', repl_role_id, message_text)
    message_text = re.sub(r'https?://discord.com/channels/\d+/(\d+)', repl_channel_id_link, message_text)
    message_text = re.sub(r'<#(\d+)>', repl_channel_id_wrap, message_text)
    message_text = re.sub(r'<:(\w+):\d+>', r':\1:', message_text)
    message_text = re.sub(r'<a:(\w+):\d+>', r':\1:', message_text)

    return message_text


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
    message_logs_for_embedding.save_logs()

    # Send a message to notify that the bot will be closed
    await ctx.send("The bot will now close.")

    await asyncio.sleep(1)

    # Use the custom signal handler to close the bot
    os.kill(os.getpid(), signal.SIGINT)


signal.signal(signal.SIGINT, signal_handler)
bot.run(DISCORD_API_KEY)
