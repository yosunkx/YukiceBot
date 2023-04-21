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

load_dotenv()
DISCORD_API_KEY = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!', '<@!1097341747459272845>'), intents=intents)

MessageID_log = MessageLog.MessageID()
message_logs = MessageLog.MessageLogs()

AUTHORIZED_USER_ID = 104055116897722368

modules.setup_all_modules(bot)

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    print('You can invite the bot by using the following url: ' + discord.utils.oauth_url(bot.user.id))
    check_events.start()

@bot.event
async def on_message(message):
    blacklisted_category_ids = [1053529567647768628]  # Replace with actual category IDs

    if message.channel.category_id not in blacklisted_category_ids:
        if message.author == bot.user:
            message_logs[message.guild.id].append({"role": "assistant", "content": message.content})
            return
        else:
            message_logs[message.guild.id].append({"role": "user", "content": message.author.name + ": " + message.content})

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
                await none_command(message, ctx, message_logs[ctx.channel.id])

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
                await none_command(message, ctx, message_logs[ctx.channel.id])
            return
        else:
            # If the message starts with a mention of the bot
            mention_prefix = f"<@!{bot.user.id}>"
            if message.content.startswith(mention_prefix):
                stripped_message = message.content[len(mention_prefix):].strip()
                if stripped_message:
                    await none_command(message, ctx, message_logs[ctx.channel.id])
                    return
    else:
        # If the message starts with a valid command, process it 
        await bot.process_commands(message)



@bot.command()
async def add_test_event(ctx):
    start_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
    await CalenderModule.add_test_event(start_time)
    bot_message = f"event added at {start_time.strftime('%Y-%m-%d %H:%M')}"
    GPT_message = await chatGPT.GPT_prompt(None, "add_test_event")
    await ctx.send(GPT_message + "\n" + bot_message)


@bot.command()
async def events(ctx, end_date: str = None):
    if end_date is None:
        end_time = None
    else:
        try:
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            end_time = end_date_obj.isoformat() + 'T23:59:59.999999Z'
        except ValueError:
            end_time = None

    events = await CalenderModule.get_events(end_time=end_time)
    if not events:
        await ctx.send('no upcomming events')
    else:
        formatted_strings = []
        for event in events:
            formatted_string = f"{event['summary']} on <t:{event['start_timestamp']}:f>"
            formatted_strings.append(formatted_string)

        output_string = '\n'.join(formatted_strings)
        GPT_message = await chatGPT.GPT_prompt(None, "events")
        await ctx.send(GPT_message + "\n" + output_string)


@tasks.loop(minutes=1)
async def check_events():
    now = datetime.datetime.utcnow()
    now_plus_2_minutes = now + datetime.timedelta(minutes=2)
    now_iso = now.isoformat() + 'Z'
    now_plus_2_minutes_iso = now_plus_2_minutes.isoformat() + 'Z'
    events = await CalenderModule.get_events(now_iso, now_plus_2_minutes_iso)

    if events:
        print('event detected')
        for event in events:
            start_timestamp = event.get('start_timestamp', '')
            end_timestamp = event.get('end_timestamp', '')
            summary = event.get('summary', '')
            start_ID = event.get('start_ID', '')
            message = event.get('message', '')
            role_name = event.get('role_name', '')
            end_ID = event.get('end_ID', '')
            if not start_timestamp or not end_timestamp:
                continue
            role = discord.utils.get(bot.guilds[0].roles, name=role_name)
            start_time = datetime.datetime.utcfromtimestamp(int(start_timestamp))
            end_time = datetime.datetime.utcfromtimestamp(int(end_timestamp))
            if start_time <= now_plus_2_minutes:
                if MessageID_log.contains(start_ID) or not message:
                    continue
                if role:
                    formatted_string = f"{role.mention} {message} starts <t:{start_timestamp}:R>"
                    if role_name == 'bottesting':
                        channel_name = 'bot-testing'
                    else:
                        channel_name = 'general-chat'
                    channel = discord.utils.get(bot.guilds[0].text_channels, name=channel_name)
                    GPT_message = await chatGPT.GPT_prompt(formatted_string, "check_events")
                    await channel.send(GPT_message + "\n" + formatted_string)
                    MessageID_log.enqueue(start_ID)
                    if 'tower of fantasy dailies' in summary:
                        await tof.add_tof_dailies(start_time)
                    MessageID_log.print()

            if end_time <= now_plus_2_minutes and end_timestamp != start_timestamp:
                if MessageID_log.contains(end_ID) or not message:
                    continue
                if role:
                    formatted_string = f"{role.mention} {message} ends <t:{end_timestamp}:R>"
                    if role_name == 'bottesting':
                        channel_name = 'bot-testing'
                    else:
                        channel_name = 'general-chat'
                    channel = discord.utils.get(bot.guilds[0].text_channels, name=channel_name)
                    GPT_message = await chatGPT.GPT_prompt(formatted_string, "check_events")
                    await channel.send(GPT_message + "\n" + formatted_string)
                    MessageID_log.enqueue(end_ID)
                    MessageID_log.print()


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


def signal_handler(signal, frame):
    print("Stopping the bot...")
    loop = asyncio.get_event_loop()
    loop.stop()

@bot.command(name="print_log")
async def print_log(ctx):
    channel_id = ctx.channel.id

    # Fetch the message logs for the current channel
    logs = message_logs[channel_id]

    # Print the message logs to the console
    print("Message logs for channel:", channel_id)
    for message in logs:
        print(f"{message['role']}: {message['content']}")


@bot.command()
async def close_bot(ctx):
    # Check if the user's ID matches the authorized userID
    if ctx.author.id != AUTHORIZED_USER_ID:
        await ctx.send("You do not have permission to use this command.")
        return

    message_logs.save_logs

    # Send a message to notify that the bot will be closed
    await ctx.send("The bot will now close.")

    # Use the custom signal handler to close the bot
    os.kill(os.getpid(), signal.SIGINT)

signal.signal(signal.SIGINT, signal_handler)
bot.run(DISCORD_API_KEY)