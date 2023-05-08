import os
import asyncio
from pickle import NONE
from pydoc import describe
import aiohttp
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from discord.ext import commands
from discord.ext import tasks
import discord
import chatGPT
from datetime import datetime as dt
import datetime
import MessageLog
from . import tof
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SERVICE_ACCOUNT_FILE = 'C:/Users/Kevin/Documents/YukiceBot/meibot-384017-177d6e3bc3bb.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = '44b8574254d7e3ea33fd3d7e113fd5c77929f013b314cb94edafa410d45def6d@group.calendar.google.com'

# Authenticate with the Google Calendar API using a service account
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

MessageID_log = MessageLog.MessageID()

load_dotenv('.env')


@commands.command()
async def add_test_event(ctx):
    start_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
    await add_event(start_time, None, 'test event', 'test event body','bottesting')
    bot_message = f"event added at {start_time.strftime('%Y-%m-%d %H:%M')}"
    GPT_message = await chatGPT.GPT_prompt(None, "add_test_event")
    await ctx.send(GPT_message + "\n" + bot_message)


@commands.command()
async def events(ctx, end_date: str = None):
    if end_date is None:
        end_time = None
    else:
        try:
            end_date_obj = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            end_time = end_date_obj.isoformat() + 'T23:59:59.999999Z'
        except ValueError:
            end_time = None

    events = await get_events(end_time=end_time)
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
async def check_events(bot):
    now = datetime.datetime.utcnow()
    now_plus_2_minutes = now + datetime.timedelta(minutes=2)
    now_plus_30_minutes = now + datetime.timedelta(minutes=30)
    now_iso = now.isoformat() + 'Z'
    now_plus_2_minutes_iso = now_plus_2_minutes.isoformat() + 'Z'
    events = await get_events(now_iso, now_plus_30_minutes)

    if events:
        #print('event detected')
        channel_message = ''
        role_names = []
        message_header = ''
        for event in events:
            #print('event')
            start_timestamp = event.get('start_timestamp', '')
            end_timestamp = event.get('end_timestamp', '')
            summary = event.get('summary', '')
            start_ID = event.get('start_ID', '')
            message = event.get('message', '')
            role_name = event.get('role_name', '')
            end_ID = event.get('end_ID', '')
            if 'dail' in summary:
                check_time = now_plus_2_minutes
            else:
                check_time = now_plus_30_minutes
            role = discord.utils.get(bot.guilds[0].roles, name=role_name)
            if not start_timestamp or not end_timestamp:
                continue
            start_time = datetime.datetime.utcfromtimestamp(int(start_timestamp))
            end_time = datetime.datetime.utcfromtimestamp(int(end_timestamp))


            if start_time <= check_time and start_time > now:
                if MessageID_log.contains(start_ID) or not message:
                    continue
                if role:
                    channel_message += f"{message} starts <t:{start_timestamp}:R>"
                    channel_message += "\n"
                    if role_name not in role_names:
                        message_header += f"{role.mention} "
                        role_names.append(role_name)
                    MessageID_log.enqueue(start_ID)
                    if 'tower of fantasy dailies' in summary:
                        await tof.add_tof_dailies(start_time)
                    MessageID_log.print()

            if end_time <= check_time and end_timestamp != start_timestamp and end_time > now:
                if MessageID_log.contains(end_ID) or not message:
                    continue
                if role:
                    channel_message += f"{message} ends <t:{end_timestamp}:R>"
                    channel_message += "\n"
                    if role_name not in role_names:
                        message_header += f"{role.mention} "
                        role_names.append(role_name)
                    MessageID_log.enqueue(end_ID)
                    MessageID_log.print()

        if channel_message:
            if role_name == 'bottesting':
                channel_name = 'bot-testing'
            else:
                channel_name = 'general-chat'
            channel = discord.utils.get(bot.guilds[0].text_channels, name=channel_name)
            GPT_message = await chatGPT.GPT_prompt(channel_message, "check_events")
            print('sending event')
            await channel.send(message_header + "\n" + GPT_message + "\n" + channel_message)


async def add_event(start_time, end_time=None, summary=None, description=None, role=None):
    if end_time is None:
        end_time = start_time

    if isinstance(start_time, str):
        try:
            start_time = dt.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            print('Invalid start_time format. Please provide a valid datetime object or an ISO formatted string.')
            return None

    if isinstance(end_time, str):
        try:
            end_time = dt.strptime(end_time, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            end_time = start_time

    random_id1 = MessageLog.generate_random_ID()
    random_id2 = MessageLog.generate_random_ID()

    event_description = '{};{};{};{}'.format(random_id1, description, role, random_id2)

    event = {
        'summary': summary or '',
        'description': event_description or '',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC',
        }
    }

    try:
        service = build('calendar', 'v3', credentials=credentials)
        print("CALENDAR_ID:", CALENDAR_ID)
        #check if similar event already exists
        check_start_time = start_time - datetime.timedelta(hours=12)
        check_end_time = end_time + datetime.timedelta(hours=12)
        existing_events = await get_events(check_start_time, check_end_time)
        if existing_events:
            for existing_event in existing_events:
                start_timestamp = existing_event.get('start_timestamp', '')
                end_timestamp = existing_event.get('end_timestamp', '')
                check_event_summary = existing_event.get('summary', '')
                role_name = existing_event.get('role_name', '')
                if not start_timestamp or not end_timestamp:
                    continue
                if role != role_name:
                    continue
                event_start_time = datetime.datetime.utcfromtimestamp(int(start_timestamp))
                if start_time != event_start_time:
                    continue
                if await check_similar(summary, check_event_summary):
                    return

        #add event
        event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')
    except HttpError as error:
        print(f'An error occurred: {error}')
        event = None

    return event

async def change_event(summary, start_time, new_summary = None, new_message = None, new_start_time = None, new_end_time = None):
    return None

async def get_events(start_time=None, end_time=None):
    loop = asyncio.get_event_loop()

    if start_time is None:
        start_time = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
    elif isinstance(start_time, datetime.datetime):
        start_time = start_time.replace(microsecond=0).isoformat() + 'Z'

    if end_time is None:
        end_time = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).replace(microsecond=0).isoformat() + 'Z'
    elif isinstance(end_time, datetime.datetime):
        end_time = end_time.replace(microsecond=0).isoformat() + 'Z'

    try:
        # Wrap the synchronous call to 'build' in 'run_in_executor'
        service = await loop.run_in_executor(None, lambda: build('calendar', 'v3', credentials=credentials))

        # Wrap the synchronous API call in 'run_in_executor'
        events_result = await loop.run_in_executor(None, lambda: service.events().list(calendarId=CALENDAR_ID, timeMin=start_time,
                                      timeMax=end_time, singleEvents=True,
                                      orderBy='startTime').execute())
        events = events_result.get('items', [])

        if not events:
            return None

        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            start_timestamp = int(datetime.datetime.fromisoformat(start).timestamp())
            end_timestamp = int(datetime.datetime.fromisoformat(end).timestamp())
            description = event.get('description', '')
            if description:
                start_ID, message, role_name, end_ID = description.split(';')
            else:
                start_ID, message, role_name, end_ID = '', '', '', ''
            event_list.append({"summary": event['summary'], "start_timestamp": start_timestamp, "end_timestamp": end_timestamp,
                               "start_ID": start_ID, "message": message, "role_name": role_name, "end_ID": end_ID})

        return event_list
    except HttpError as error:
        print(f'An error occurred: {error}')
        events = None
        return events


async def check_similar(new_event_summary, old_event_summary):
    similarity_threshold=0.4

    summaries = [new_event_summary] + [old_event_summary]

    # Vectorize the summaries using TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(summaries)

    # Calculate cosine similarity between the new event summary and all other summaries
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)

    # Check if the cosine similarity is above the specified threshold
    if cosine_similarities[0][1] >= similarity_threshold:
        return True

    return False







def setup(bot):
    bot.add_command(add_test_event)
    bot.add_command(events)




if __name__ == "__main__":
    pass