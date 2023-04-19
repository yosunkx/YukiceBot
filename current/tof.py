import os
import asyncio
import datetime
from random import random
import CalendarModule
from dotenv import load_dotenv, set_key

load_dotenv()
raid_day = os.getenv('RAID_DAY') or '0'
void_day = os.getenv('VOID_DAY') or '4'
fch_day = os.getenv('FCH_DAY') or '5'

async def add_tof_dailies(prev_time):
    description = 'JJ'
    start_time = prev_time + datetime.timedelta(hours = 24)

    # Get the current day of the week as an integer (0=Monday, 6=Sunday)
    tomorrow = (datetime.datetime.utcnow().weekday() + 1) % 7

    if tomorrow == int(raid_day):
        description += '>raid'
        set_key('.env', 'RAID_DAY', None)

    if tomorrow == int(void_day):
        description += '>void'
        set_key('.env', 'VOID_DAY', None)

    if tomorrow == int(fch_day):
        description += '>fch'
        set_key('.env', 'FCH_DAY', None)

    CalendarModule.add_event(start_time, None, 'tower of fantasy dailies', description, 'ToF-d')

    return None

async def tof_change_date(activity,new_date):
    return None
