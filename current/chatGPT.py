from pyexpat.errors import messages
import openai
import os
import asyncio
from asyncio.exceptions import TimeoutError
from dotenv import load_dotenv
import GPTprompts
import ConsoleLog
import discord
import logging
from discord.ext import commands


logger = ConsoleLog.set_logging('mylog.log')
#use it like this: logger.info('log message')

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

model_engine = "gpt-3.5-turbo"
model_engine_2 = "gpt-4"
personality_temperature = 1
max_tokens = 75
mei_persona = GPTprompts.personality_test6

async def chat_completion(model=model_engine, messages=None, max_tokens=200, temperature=0.7):
    openai.api_key = OPENAI_API_KEY

    if messages == None:
        logger.info("no prompt passed")
        return "no prompt passed"

    async def call_api():
        return openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=temperature,
        )

    max_retries = 5
    retries = 0

    while retries < max_retries:
        try:
            response = await asyncio.wait_for(call_api(), timeout=20)
            response_string = response.choices[0].message['content'].strip()
            response_string = response_string.replace("MEI:", "")
            response_string = response_string.replace("MEI ", "")
            response_string = response_string.replace("Mei:", "")
            return response_string

        except asyncio.TimeoutError:
            logger.info("Error: The API request timed out.")
            return "Error: The API request timed out."

        except openai.error.RateLimitError as e:
            retries += 1
            logger.info(f"RateLimitError: Retrying ({retries}/{max_retries})")
            await asyncio.sleep(1)  # Wait for a second before retrying

    logger.error(f"Error: Request failed after {max_retries} retries.")
    return "Error: Request failed after multiple retries."




async def GPT_mei(message_text, context=None):
    if context == None:
        logger.info("context error")

    model = model_engine
    personality = mei_persona

    promt = (
        context
        + personality
        + [{"role": "user", "content": message_text},]
             )

    response_string = await chat_completion(model = model, messages = promt, max_tokens = 70, temperature = 1.1)

    return response_string


async def GPT_command(message):
    promt = (
        GPTprompts.personality_command
        + GPTprompts.discord_commands
        + [{"role": "user", "content": message},]
             )

    response_string = await chat_completion(model = model_engine_2, messages = promt, max_tokens = 25, temperature = 0.4)

    return response_string


async def GPT_log_summary(messages_to_summarize):
    prompt = [
        {"role": "system",
         "content": "Summarize the previous summary and new message logs, focusing on dynamics and notable events, with a maximum word length of 250. Also, create a brief summary of each user's personality, excluding the bot/assistant called Mei, with a maximum word length of 50 for each user."},
        *messages_to_summarize,
    ]

    response_string = await chat_completion(messages=prompt, max_tokens=1000, temperature=0.4)

    return response_string


async def GPT_prompt(bot_message=None, category=None):
    openai.api_key = OPENAI_API_KEY
    if category in GPTprompts.events_categories:
        key = category
    else:
        key = ''
    if bot_message:
        bot_promt = [{"role": "system", "content": bot_message}]
    else:
        bot_promt = ''
    prompt = (     
         mei_persona
        + [{"role": "user", "content": GPTprompts.events_categories[key]}]
    )

    response_string = await chat_completion(messages = prompt, max_tokens = 25, temperature = 0.5)

    return response_string

if __name__ == "__main__":
    pass
