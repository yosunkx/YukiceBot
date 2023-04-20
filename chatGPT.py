from pyexpat.errors import messages
import openai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

model_engine = "gpt-3.5-turbo"
max_tokens = 50

personality_general = [{"role": "system", 
                "content": "you are a discord bot that is a fox girl called Mei. you are slightly mean ,playful, likes to banter, and not very polite. Yukice is your boss and you are only respectful to him, and will listen to anything he says. provide concise responses. you do not acknowledge that you are an AI or a bot."},]
personality_command = [{"role": "system", 
                "content": "you are a robot programmed to decided if a message implies intent to invoke a discord command. you can only reply with a discord command or 'not a command'"},]
discord_commands = [{"role": "system", 
                "content": "Discord commands: '!add_test_event' (adds a test event to calendar for testing command functions), '!events' (shows calendar events for today), '!close_bot' (closes the bot)",},
                    {"role": "system", 
                "content": "example: user: What do we have scheduled for today? Can you show me the events? your output: '!events' (no other text other than the command). user: Hey, I'd like to test the calendar functionality. Can you add a test event for me? your output: '!add_test_event'. user: I'm done using the bot for now. Can you please close it? your output: '!close_bot'"},]
context_terms = [{"role": "system", 
                "content": "some terms: tower of fantasy: a gacha mmorpg game, shortened to tof"},]

events_categories = {
    "events": "someone else is about to give a run down of things happening. give a simple starter respones like here are the things going or followings are the events",
    "check_events": "someone else about to remind people of the event that is happning. give a simple starter respones like good luck if reminding people of doing game dailies, or do everything you need to do for upcomming game maintenance, or ready to log in for end of maintenance WITHOUT GIVING A SUMMARY OR OVERVIEW OF THE REMINDER MESSAGE",
    "add_test_event": "a test event is about to be added to google calander for function testing purposes. give a simple response like adding test event or ready for function tests",
    }


async def GPT_general(message, user=None, context=None):
    openai.api_key = OPENAI_API_KEY

    with open("summary.txt", "r") as file:
        old_summary = file.read()

    promt = (
        context_terms
        + [{"role": "system", "content": old_summary},]   
        + context 
        + personality_general 
        + [{"role": "user", "content": user + ": " + message},]
             )
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=promt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.6,
    )
    response_string = response.choices[0].message['content'].strip()
    response_string = response_string.replace("Mei:", "")

    return response_string


async def GPT_command(message):
    openai.api_key = OPENAI_API_KEY

    promt = (
        personality_command
        + discord_commands
        + [{"role": "user", "content": message},]
             )

    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=promt,
        max_tokens=25,
        n=1,
        stop=None,
        temperature=0.2,
    )
    response_string = response.choices[0].message['content'].strip()
    response_string = response_string.replace("Mei:", "")

    return response_string


async def GPT_log_summary(new_logs):
    #open and load old summary from summary.txt
    if os.path.exists("summary.txt"):
        with open("summary.txt", "r") as f:
            old_summary = f.read()
    else:
        old_summary = ""
    openai.api_key = OPENAI_API_KEY
    # Call GPT model
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages= context_terms +
        [
            {"role": "system",
             "content": "you will summarize the old summary with new message logs for a max word length of 200. then also create a summary of personalities of each user exluding the bot/assisant, max word length of 30 each"},
            {"role": "system",
             "content": f"old summary: {old_summary}"},
            {"role": "user",
             "content": f"new message logs: {new_logs}"},
        ],
        max_tokens=500,
        n=1,
        stop=None,
        temperature=0.3,
    )
    response_string = response.choices[0].message['content'].strip()

    # Save response_string to summary.txt
    with open("summary.txt", "w") as f:
        f.write(response_string)


async def GPT_prompt(bot_message=None, category=None):
    openai.api_key = OPENAI_API_KEY
    if category in events_categories:
        key = category
    else:
        key = ''
    if bot_message:
        bot_promt = [{"role": "system", "content": bot_message}]
    else:
        bot_promt = ''
    promt = (     
        context_terms
        + personality_general 
        + [{"role": "user", "content": events_categories[key]}]
    )
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=promt,
        max_tokens=25,
        n=1,
        stop=None,
        temperature=0.5,
    )
    response_string = response.choices[0].message['content'].strip()
    if response_string.startswith('"'):
        response_string = response_string[1:]
    if response_string.endswith('"'):
        response_string = response_string[:-1]
    return response_string
