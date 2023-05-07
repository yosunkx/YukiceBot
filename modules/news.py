from ast import Delete
from calendar import calendar
from discord.ext import commands
from discord.ext import tasks
import discord
import datetime
import asyncio
import re
import requests
from apify_client import ApifyClient
from apify_client import ApifyClientAsync
import os
from dotenv import load_dotenv
from PIL import Image
from pytesseract import pytesseract
from io import BytesIO
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import httpx
import chatGPT
from . import CalendarModule
import logging

load_dotenv('.env')
APIFY_TOKEN = os.getenv('APIFY_API_KEY')

path_to_tesseract = os.getenv('path_to_tesseract')

async def on_message(message):
    task = asyncio.create_task(process_message(message))

async def process_message(message):
    news_category_id = 1053529567647768628
    bot_id = 1097341747459272845
    if message.channel.category.id == news_category_id and message.author != bot_id:
        channel_name = message.channel.name
        tag = channel_name.split('-')[1]
        print(f"converting news to text for: {tag}")
        news_text = await convert_to_text(message, tag)
        #print(news_text)
        summary_text = await news_text_to_summary(news_text)
        await news_summary_to_calendar(summary_text, tag)

def setup(bot):
    bot.add_listener(on_message)

async def convert_to_text(message, tag):
    lines = message.content.split('\n')
    output = []

    for line in lines:
        links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', line)

        if links:
            print("found links")
            for link in links:
                if 'twitter.com' in link:
                    print("found twitter link")
                    tweet_text = await extract_text_from_tweet(link, tag)
                    output.append(tweet_text)
                elif tag == 'tof':
                    print("found tof link")
                    link_text = await extract_text_from_link(link, tag)
                    output.append(link_text)
        else:
            output.append(line)

    # If the message contains an image
    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type.startswith('image/'):
                # Convert the image to text
                image_text = await convert_image_to_text(attachment)
                output.append(image_text)

    return '\n'.join(output)

async def extract_text_from_tweet(tweet_link, tag):
    print("extracting text from tweet")
    apify_client = ApifyClientAsync(APIFY_TOKEN)
    run_input = {
        "startUrls": [{"url": tweet_link}],
        "tweetsDesired": 1,
    }
    run = await apify_client.actor("quacker/twitter-url-scraper").call(run_input=run_input)
    full_text_output = ""
    photos = []

    async for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
        if 'full_text' in item:
            full_text_output += item['full_text']
        if 'url' in item and (tag == 'nikke' or tag == 'tof'):
            await extract_text_from_link(item['url'], tag)
        if 'media' in item:
            for media in item['media']:
                if media['type'] == 'photo':
                    photos.append(media['media_url'])

    for photo_url in photos:
        photo_text = await convert_image_to_text(photo_url)
        full_text_output += "\n"
        full_text_output += photo_text

    return full_text_output

async def extract_text_from_link(url, tag):
    print("extracting text from link")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = browser.new_context()
        page = await browser.new_page()
        await page.goto(url)
        texts = []

        if tag == 'nikke':
            content_elements = await page.query_selector_all('.document')

            for element in content_elements:
                text = await element.text_content()
                texts.append(text)
        elif tag == 'tof':
            iframe_element = await page.query_selector("div#detail > iframe")
            iframe_content = await iframe_element.content_frame()

            # Extract the desired text content
            text = await iframe_content.inner_text("body")
            texts.append(text)
        else:
            return ''


        await browser.close()
        return '\n'.join(texts)


async def convert_image_to_text(image_url):
    print("extracting text from image")
    pytesseract.tesseract_cmd = path_to_tesseract

    # Get the image from the URL
    async with httpx.AsyncClient() as client:
        response = await client.get(image_url)
    img = Image.open(BytesIO(response.content))
    text = pytesseract.image_to_string(img)
    return text


async def news_text_to_summary(raw_text):
    prompt = (     
        [{"role": "user", 
          "content": "extract the maintenance dates and new events and their dates from the following text"},]
        + [{"role": "user", 
            "content": raw_text},]
    )    
    summary_text = await chatGPT.GPT_general(prompt, 0.3)
    return summary_text

async def news_summary_to_calendar(summary, tag):
    prompt = (     
        [{"role": "user", 
          "content": ("For each maintenance and event listed, convert the given information into the format: "
"start_time, end_time, title. Use none for events that do not have a specific start time provided. Format start_time and end_time using Python's datetime.isoformat(). Please make sure to use the correct start date for each event, especially if it is not provided. Use 2023 for year if no year is provided."
"Example output:"
"2023-04-22T22:00:00,2023-04-23T22:00:00,Maintenance"
"none,2023-04-25T06:00:00,Heaven's Gate"
"2023-04-23T22:00:00,2023-04-30T20:00:00,Samir Limited Order")},]
        + [{"role": "user", 
            "content": summary},]
    )
    logging.info("Before GPT_generate() call")
    calendar_text = await chatGPT.GPT_general(prompt, 0.3)
    logging.info("After GPT_generate() call")
    #print("finished summary")
    #print(calendar_text)
    lines = calendar_text.split("\n")
    event_list = []
    maintenance_end_time = ''
    for line in lines:
        start_time, end_time, description = line.split(',')
        if "maintenance" in description.lower():
            if not maintenance_end_time:
                maintenance_end_time = end_time
        event_list.append((start_time, end_time, description))

    for event in event_list:
        start_time, end_time, description = event
        if start_time == 'none':
            if maintenance_end_time:
                start_time = maintenance_end_time
            else:
                now = datetime.datetime.utcnow()
                start_time = now.isoformat()
        await CalendarModule.add_event(start_time, end_time, description, description, tag)

#async def main():
#    test_link = 'https://www.toweroffantasy-global.com/news-detail.html?content_id=8231a552a7994a4c23a8b82aebe2539ee11b'
#    text = await extract_text_from_link(test_link, 'tof')
#    print(text)

#async def main():
#    raw_text = ''
#    with open('C:/Users/Kevin/Documents/YukiceBot/modules/test_text.txt') as f:
#        for line in f:
#            raw_text += line
#            raw_text += '\n'

#    #print("calling summarize")
#    summary = await news_text_to_summary(raw_text)
#    #print(summary)
#    #print("calling calendar")
#    await news_summary_to_calendar(summary, 'tof')

#if __name__ == '__main__':
#    import asyncio
#    asyncio.run(main())
