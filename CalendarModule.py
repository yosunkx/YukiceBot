import os
import asyncio
from pickle import NONE
import aiohttp
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import datetime

SERVICE_ACCOUNT_FILE = 'C:/Users/Kevin/Documents/YukiceBot/meibot-384017-177d6e3bc3bb.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
CALENDAR_ID = '44b8574254d7e3ea33fd3d7e113fd5c77929f013b314cb94edafa410d45def6d@group.calendar.google.com'

# Authenticate with the Google Calendar API using a service account
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

async def add_test_event(start_time):
    event = {
        'summary': 'Sample Event',
        'description': '0,test,bottesting',
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        }
    }

    try:
        service = build('calendar', 'v3', credentials=credentials)
        print("CALENDAR_ID:", CALENDAR_ID)
        event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')
    except HttpError as error:
        print(f'An error occurred: {error}')
        event = None

    return event



async def add_event(start_time, end_time=None, summary=None, description=None):
    if end_time is None:
        end_time = start_time

    event = {
        'summary': summary or '',
        'description': description or '',
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
        event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')
    except HttpError as error:
        print(f'An error occurred: {error}')
        event = None

    return event


async def get_events(start_time=None, end_time=None):
    loop = asyncio.get_event_loop()

    if start_time is None:
        start_time = datetime.datetime.utcnow().date().isoformat() + 'T00:00:00Z'  # 'Z' indicates UTC time

    if end_time is None:
        end_time = (datetime.datetime.utcnow() + datetime.timedelta(days=1)).date().isoformat() + 'T23:59:59.999999Z'

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
            event_list.append({"summary": event['summary'], "start_timestamp": start_timestamp, "end_timestamp": end_timestamp, "description": description})

        return event_list
    except HttpError as error:
        print(f'An error occurred: {error}')
        events = None
        return events
