import os
import asyncio
import datetime
from discord.ext import commands
from random import random
from . import CalendarModule
from dotenv import load_dotenv, set_key
import ConsoleLog
import logging

logger = ConsoleLog.set_logging('mylog.log')
#use it like this: logger.info('log message')

load_dotenv()
raid_day = os.getenv('RAID_DAY') or '1'
void_day = os.getenv('VOID_DAY') or '5'
fch_day = os.getenv('FCH_DAY') or '6'

@commands.command()
async def add_tof_dailies(ctx):
    daily_content = await add_tof_daily()
    print (f"next daily added: {daily_content}")

def setup(bot):
    bot.add_command(add_tof_dailies)

async def add_tof_daily():
    description = 'check old man otherwise JJ'
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    start_time = now.replace(hour=3, minute=30, second=0, microsecond=0)
    if now >= start_time:
        start_time += datetime.timedelta(days=1)

    # Get the current day of the week as an integer (0=Monday, 6=Sunday)
    day_of_week = start_time.weekday()

    if day_of_week == int(raid_day):
        description += '>raid'
        set_key('.env', 'RAID_DAY', '')

    if day_of_week == int(void_day):
        description += '>void'
        set_key('.env', 'VOID_DAY', '')

    if day_of_week == int(fch_day):
        description += '>fch'
        set_key('.env', 'FCH_DAY', '')

    await CalendarModule.add_event(start_time, None, 'tower of fantasy dailies', description, 'ToF-d')
    return description

async def tof_change_date(activity,new_date):
    return None



if __name__ == "__main__":
    pass