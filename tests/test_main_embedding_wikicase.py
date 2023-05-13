from embedding import main_embedding
import asyncio


async def main():
    url = 'http://wiki.heroesofhammerwatch.com/Paladin'
    data = await main_embedding.user_handler(url)
    for item in data:
        print(item['text_chunk'])
        embedding = item['embedding']
        print("embedding: ", embedding[:3].tolist(), '...', embedding[-3:].tolist())
        print("index: ", item['index'])


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
