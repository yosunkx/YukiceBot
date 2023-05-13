from embedding.modules import wikipedia_scrape
import asyncio


async def main():
    data = await wikipedia_scrape.scrape_wikipedia('http://wiki.heroesofhammerwatch.com/Paladin')
    for item in data:
        print(f"Title: {item['title']}")
        print(f"Section: {item['section']}")
        print(f"Text: {item['text']}\n")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
