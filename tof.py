import os
import asyncio
import datetime
import CalendarModule

countersfile = 'tof_counters.txt'

async def add_tof_dailies(prev_time):
    void_count, fch_count, raid_count = load_counters(countersfile)
    description = '1,JJ'
    start_time = prev_time + datetime.timedelta(hours = 24)

    # Get the current day of the week as an integer (0=Monday, 6=Sunday)
    today = datetime.datetime.utcnow().weekday()

    if today == 6:
        raid_count += 1

    if today == 6 or today == 1 or today == 3:
        void_count += 1

    if today == 0 or today == 2 or today == 4:
        fch_count += 1

    if raid_count == 1:
        description += '>raid'
        raid_count = 0

    if void_count == 3:
        description += '>voidx3'
        void_count = 0

    if fch_count == 3:
        description += '>fchx3'
        fch_count = 0

    description += ',tof'

    CalendarModule.add_event(start_time, None, 'tower of fantasy dailies', description)

    save_counters(void_count, fch_count, raid_count)
    return None

def load_counters(filename):
    void_count, fch_count, raid_count = 0, 0, 0
    with open(filename, 'r') as f:
        lines = f.readlines()
    for line in lines:
        name, value = line.strip().split(',')
        if name == 'tof_void_count':
            void_count = int(value)
        elif name == 'tof_fch_count':
            fch_count = int(value)
        elif name == 'tof_raid_count':
            raid_count = int(value)
    return void_count, fch_count, raid_count

def save_counters(void_count, fch_count, raid_count):
    with open(countersfile, 'w') as file:
        file.write(f'tof_void_count,{void_count}\n')
        file.write(f'tof_fch_count,{fch_count}\n')
        file.write(f'tof_raid_count,{raid_count}\n')
