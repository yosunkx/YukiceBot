from pyexpat.errors import messages
import openai
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

model_engine = "gpt-3.5-turbo"
max_tokens = 100

personality = "you are a discord bot that is a fox girl called Mei, is slightly mean ,playful, likes to banter, and not very polite, provide concise responses without mentioning that you are an AI"

async def GPT_general(message):
    openai.api_key = OPENAI_API_KEY
    response = openai.ChatCompletion.create(
        model=model_engine,
        messages=[
            {"role": "system", "content": personality},
            {"role": "user", "content": message},
        ],
        max_tokens=max_tokens,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].message['content'].strip()
