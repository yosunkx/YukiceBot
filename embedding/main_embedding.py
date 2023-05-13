from .modules import embedding_transformer, wikipedia_scrape


async def user_handler(user_input):
    data_list = []

    if 'wiki' in user_input:
        data = await wikipedia_scrape.scrape_wikipedia(user_input)
        for item in data:
            item_title = item['title']
            item_section = item['section']
            item_text = item['text']

            embeddings, texts, indexes = await embedding_transformer.async_encode(item_text, item_title, item_section)

            for i in range(len(embeddings)):
                data_dict = {
                    'embedding': embeddings[i],
                    'text_chunk': texts[i],
                    'index': indexes[i]
                }
                data_list.append(data_dict)

    return data_list
