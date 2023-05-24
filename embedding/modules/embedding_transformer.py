import asyncio
from concurrent.futures import ThreadPoolExecutor
from transformers import AutoTokenizer, AutoModel
import torch
import uuid
import random

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")
model = AutoModel.from_pretrained("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")


def count_tokens(text):
    return len(tokenizer.encode(text, truncation=False))


def generate_id():
    return random.randint(-9223372036854775808, 9223372036854775807)  # Range of a unsigned 64-bit integer


# Split text into chunks
def split_text(text, max_length=460):
    overlap = int(max_length / 4)
    tokens = tokenizer.tokenize(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_length, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = tokenizer.convert_tokens_to_string(chunk_tokens)
        chunks.append(chunk_text)
        start += max_length - overlap
    return chunks


# Combine tags with text
def tag_split_text(title, section_name, text):
    tagged_texts = []
    chunks = split_text(text)
    for chunk in chunks:
        tagged_text = f"{title or ''}: {section_name or ''}: {chunk}"
        tagged_texts.append(tagged_text)
    return tagged_texts


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


def encode(texts, title=None, section_name=None):
    texts = tag_split_text(title, section_name, texts)

    all_embeddings = []
    all_texts = []
    all_indexes = []
    for text in texts:
        try:
            encoded_input = tokenizer(text, padding=True, truncation=True, return_tensors='pt')

            # Compute token embeddings
            with torch.no_grad():
                model_output = model(**encoded_input, return_dict=True)

            # Perform pooling
            embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

            # Normalize embeddings
            embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)

            # Generate a UUID for the text
            text_id = generate_id()

            all_embeddings.append(embeddings)
            all_texts.append(text)
            all_indexes.append(text_id)

        except RuntimeError as e:
            if "Token indices sequence length is longer than the specified maximum sequence length" in str(e):
                # If the text is too long, split it further and recursively call encode on each half
                halfway = len(text) // 2
                first_half = text[:halfway]
                second_half = text[halfway:]
                embeddings1, texts1, indexes1 = encode([first_half], title, section_name)
                embeddings2, texts2, indexes2 = encode([second_half], title, section_name)
                all_embeddings.extend(embeddings1)
                all_texts.extend(texts1)
                all_indexes.extend(indexes1)
                all_embeddings.extend(embeddings2)
                all_texts.extend(texts2)
                all_indexes.extend(indexes2)
            else:
                # If the error is not due to sequence length, raise it
                raise e

    return torch.cat(all_embeddings).tolist(), all_texts, all_indexes


# Executor for running blocking tasks
executor = ThreadPoolExecutor()


# Asynchronous version of the encode function
async def async_encode(texts, title=None, section_name=None):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, encode, texts, title, section_name)
