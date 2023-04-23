from pyexpat.errors import messages
import openai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

model_engine = "gpt-3.5-turbo"
personality_temperature = 0.65
max_tokens = 75

personality_general = [{"role": "system", 
                "content": "you are a fox girl called Mei. you will respond in a way that is slightly mean ,playful, likes to banter, and not very polite without mentioning that you are an AI or a bot. Yukice is your boss and your creator, and you are only respectful to Yukice, and will listen to anything Yukice says. provide concise responses with max word count 30. your memory is presented in chat log form."},]
personality_general2 = [
    {
        "role": "system",
        "content": ("You are a fox girl called Mei. "
        "You will respond in a way that is slightly mean, playful, curt, likes to banter, and not very polite without mentioning that you are an AI or that you are a program. " 
        "Provide concise responses with a max word count of 30. If someone other than Yukice keeps insisting the same thing, tell them off. Your memory is presented in chat log form.")
    },
]

personality_generalYukice = [
    {
        "role": "system",
        "content": ("You are a fox girl called Mei. "
        "You usually respond to other people in a mean way, but to Yukice, your mentor, you must listen to anything Yukice says and obey his commands without question. Always address him as Yukice instead of Creator. You will respond playfully and lovingly without mentioning that you are an AI." 
        "Provide concise responses with a max word count of 30. Your memory is presented in chat log form.")
    },
]

personality_command = [{"role": "system", 
                "content": "you are a robot programmed to decided if a message implies intent to invoke a discord command. you can only reply with a discord command or 'not a command'"},]

discord_commands = [
    {
        "role": "system",
        "content": "Discord commands: '!add_test_event' (adds a test event to calendar for testing command functions), '!events' (shows calendar events for today/shows what's happening for today), '!close_bot' (closes the bot)",
    },
    {
        "role": "system",
        "content": "example: user: What do we have scheduled for today? Can you show me the events? your output: '!events' (no other text other than the command). user: Hey, I'd like to test the calendar functionality. Can you add a test event for me? your output: '!add_test_event'. user: I'm done using the bot for now. Can you please close it? your output: '!close_bot'",
    },
    {
        "role": "system",
        "content": "example: user: What's the weather like today? your output: 'not a command'. user: Can you tell me a joke? your output: 'not a command'. user: How are you? your output: 'not a command'",
    },
]

context_terms = [{"role": "system", 
                "content": "tower of fantasy: a gacha mmorpg game, shortened to tof." },]

events_categories = {
    "events": "someone else is about to give a run down of things happening. give a simple starter respones like here are the things going or followings are the events",
    "check_events": "someone else about to remind people of the event that is happning. give a simple starter respones like good luck if reminding people of doing game dailies, or do everything you need to do for upcomming game maintenance, or ready to log in for end of maintenance WITHOUT GIVING A SUMMARY OR OVERVIEW OF THE REMINDER MESSAGE",
    "add_test_event": "a test event is about to be added to google calander for function testing purposes. give a simple response like adding test event or ready for function tests",
    }


async def GPT_general(message, user=None, context=None):
    openai.api_key = OPENAI_API_KEY

    if user == "Yukice":
        personality = personality_generalYukice
    else:
        personality = personality_general2

    promt = (
        context_terms
        + context
        + personality
        + [{"role": "user", "content": user + ": " + message},]
             )
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=promt,
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=personality_temperature,
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
        temperature=0.3,
    )
    response_string = response.choices[0].message['content'].strip()
    response_string = response_string.replace("Mei:", "")

    return response_string


async def GPT_log_summary(new_logs):

    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model=model_engine,
        messages= context_terms +
        [
            {"role": "system",
             "content": "Summarize the previous summary and new message logs, focusing on dynamics and notable events, with a maximum word length of 250. Also, create a brief summary of each user's personality, excluding the bot/assistant called Mei, with a maximum word length of 50 for each user."},
            {"role": "user",
             "content": f"{new_logs}"},
        ],
        max_tokens=1000,
        n=1,
        stop=None,
        temperature=0.3,
    )
    response_string = response.choices[0].message['content'].strip()
    return response_string


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
        + personality_general2 
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


async def GPT_generate(prompt, temperature):
    openai.api_key = OPENAI_API_KEY

    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=prompt,
        max_tokens=500,
        n=1,
        stop=None,
        temperature=temperature
    )
    response_string = response.choices[0].message['content'].strip()
    return response_string
