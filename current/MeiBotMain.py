from mailbox import Message
import os
import asyncio
import datetime
from dotenv import load_dotenv
import discord
from discord.ext import commands
from discord.ext import tasks
import CalendarModule
import tof
import MessageID

load_dotenv()
DISCORD_API_KEY = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=commands.when_mentioned_or('!', '<@!1097341747459272845>'), intents=intents)

MessageID_log = MessageID.MessageID()

@bot.event
async def on_ready():
    print('Logged in as {0.user}'.format(bot))
    print('You can invite the bot by using the following url: ' + discord.utils.oauth_url(bot.user.id))
    check_events.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

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
                await none_command(message.content)

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
                await none_command(user_message)
            return
        else:
            # If the message starts with a mention of the bot
            mention_prefix = f"<@!{bot.user.id}>"
            if message.content.startswith(mention_prefix):
                stripped_message = message.content[len(mention_prefix):].strip()
                if stripped_message:
                    await none_command(stripped_message)
                    return
    else:
        # If the message starts with a valid command, process it normally
        await bot.process_commands(message)



@bot.command()
async def add_test_event(ctx):
    start_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
    await CalendarModule.add_test_event(start_time)
    await ctx.send(f"event added at {start_time.strftime('%Y-%m-%d %H:%M')}")


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

    events = await CalendarModule.get_events(end_time=end_time)
    if not events:
        await ctx.send('no upcomming events')
    else:
        formatted_strings = []
        for event in events:
            formatted_string = f"{event['summary']} on <t:{event['start_timestamp']}:f>"
            formatted_strings.append(formatted_string)

        output_string = '\n'.join(formatted_strings)
        await ctx.send(output_string) 


@tasks.loop(minutes=1)
async def check_events():
    print(f'checking events')
    now = datetime.datetime.utcnow()
    now_plus_2_minutes = now + datetime.timedelta(minutes=2)
    now_iso = now.isoformat() + 'Z'
    now_plus_2_minutes_iso = now_plus_2_minutes.isoformat() + 'Z'
    events = await CalendarModule.get_events(now_iso, now_plus_2_minutes_iso)

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
                    await channel.send(formatted_string)
                    MessageID_log.enqueue(start_ID)
                    if 'tower of fantasy dailies' in summary:
                        tof.add_tof_dailies(start_time)
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
                    await channel.send(formatted_string)
                    MessageID_log.enqueue(end_ID)
                    MessageID_log.print()


async def none_command(message):
    print(message)

bot.run(DISCORD_API_KEY)