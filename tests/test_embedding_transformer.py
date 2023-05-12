import asyncio
from embedding import embedding_transformer
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")


# Usage
async def main():
    title = "Document Title"
    section_name = "Section Name"
    text = """
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    This is a test text. It's meant to test the functionality of the embedding transformer.
    We're passing this along with a title and a section name to see how the model behaves.
    """
    embeddings = await embedding_transformer.async_encode(text, title, section_name)
    print(embeddings)
    # Tokenize the text and count tokens
    tokens = tokenizer.tokenize(text)
    num_tokens = len(tokens)

    print(f'The text contains {num_tokens} tokens.')

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
