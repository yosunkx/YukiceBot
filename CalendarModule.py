import os
import asyncio
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

async def add_event(date, time):
    event_start = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    event_end = event_start + datetime.timedelta(hours=1)

    event = {
        'summary': 'Sample Event',
        'start': {
            'dateTime': event_start.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': event_end.isoformat(),
            'timeZone': 'America/Los_Angeles',
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

async def get_event(date_start, date_end)