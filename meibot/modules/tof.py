import os
import datetime
from discord.ext import commands
from . import CalendarModule, ConsoleLog

logger = ConsoleLog.set_logging('mylog.log')

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
print(DATA_DIR)
DATA_FILE = 'tof_config.txt'


@commands.command()
async def add_tof_dailies(ctx):
    daily_content = await add_tof_daily()
    logger.info(f"next daily added: {daily_content}")


def load_config():
    config_path = os.path.join(DATA_DIR, DATA_FILE)
    if not os.path.exists(config_path):
        return {}

    with open(config_path, 'r') as file:
        lines = file.readlines()

    config = {}
    for line in lines:
        key, value = line.strip().split('=')
        config[key] = value

    return config


def save_config(config):
    config_path = os.path.join(DATA_DIR, DATA_FILE)
    with open(config_path, 'w') as file:
        for key, value in config.items():
            file.write(f"{key}={value}\n")


def add_key_to_config(config, key, value):
    config[key] = value


def setup(bot):
    bot.add_command(add_tof_dailies)


async def add_tof_daily():
    config = load_config()
    raid_day = int(config.get('RAID_DAY', '1'))
    void_day = int(config.get('VOID_DAY', '5'))
    fch_day = int(config.get('FCH_DAY', '6'))
    description = 'check old man otherwise JJ'
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    start_time = now.replace(hour=3, minute=30, second=0, microsecond=0)
    if now >= start_time:
        start_time += datetime.timedelta(days=1)

    # Get the current day of the week as an integer (0=Monday, 6=Sunday)
    day_of_week = start_time.weekday()

    if day_of_week == raid_day:
        description += '>raid'
        add_key_to_config(config, 'RAID_DAY', '1')

    if day_of_week == void_day:
        description += '>void'
        add_key_to_config(config, 'VOID_DAY', '5')

    if day_of_week == fch_day:
        description += '>fch'
        add_key_to_config(config, 'FCH_DAY', '6')

    save_config(config)

    await CalendarModule.add_event(start_time, None, 'tower of fantasy dailies', description, 'ToF-d')
    return description


async def tof_change_date(activity, new_date):
    return None
