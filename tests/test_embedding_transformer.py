import asyncio
from embedding.modules import embedding_transformer
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/multi-qa-MiniLM-L6-cos-v1")


# Usage
async def main():
    title = "The Last Symphony of Epsilon IV"
    section_name = None
    text = """
In the silent reaches of the cosmos, where the light of distant stars flickered like a forgotten memory, lay the planet Epsilon IV. The inhabitants, Epsilonians, were beings of energy, communicating through luminescent patterns that danced in the air like celestial poetry.

Astria, an Epsilonian, was a composer of light. Her symphonies were vibrant tales, glowing sonnets of radiant energy that spoke of love, loss, joy, and despair. As a young energy-being, she was renowned for her genius, her works illuminating the sky in a spectacle of color and motion.

However, Astria was nearing the end of her energy cycle. It was time for her final composition, and it was to be her magnum opus. She traveled to the highest peak of Epsilon IV, where the energy fields were strongest. Here, she would shape her grand symphony, an opus to echo across the cosmos.

Astria began with a soft, turquoise ripple, a lullaby that her mother had hummed in her infancy. It spread across the sky, a comforting blanket of light. Then, she introduced a vivid violet wave, a memory of her first love, a poignant melody of joy and heartbreak. The sky pulsated with her story, the cosmos a captive audience to her spectral recital.

She spoke of her people's history, an amber storm roiling across the sky, a testament to their resilience. She wove a narrative of the ancient Epsilonian wars, the crimson chaos that had once consumed their world, yet also marked their evolution. She created a green spiral, a sign of their enlightenment, their harmonious co-existence with the universe.

The symphony evolved, merging with the cosmic rhythm. Astria's energy, her very essence, was poured into each radiant note, each luminous chord. The sky became a radiant tapestry, reflecting the story of her life, her people, her world.

As she reached the climax, she painted a silvery crescendo, a testament to her hope for the future. It was a promise of peace, a lullaby for the generations to come. Then, she ended the symphony with a soft, white pulse, a symbol of her surrender to the cosmic cycle.

The symphony faded, but its echo lingered, a haunting melody in the silent void. And as the last notes dissolved into the ether, so too did Astria. Her energy dissipated, returning to the universal canvas from which it had sprung.

Epsilon IV mourned her loss, yet celebrated her life. They remembered her in every celestial tune, every cosmic rhythm. The echoes of her symphony remained, a testament to her genius, her spirit, and her undeniable legacy. Astria's opus was more than a farewell; it was a harmonious thread woven into the cosmic tapestry, a radiant note in the grand orchestra of the universe.

Astria may have ceased to exist in her physical form, but her music, her stories, resonated throughout the cosmos, a beacon of beauty in the void. Her luminary symphony was her immortality, a celebration of life and its inevitable return to the cosmic dance.

From a distant corner of the universe, an alien civilization picked up the remnants of the symphony. They marveled at the strange, beautiful patterns, a language they didn't understand, but a sentiment they did. And so, Astria's music lived on, reaching out to distant corners of the universe, a testament to a life well-lived and a legacy well-left.

The Last Symphony of Epsilon IV was a grand opus that reverberated through the cosmos, a story of life, love, loss, and hope. This composition was an eternal testament to the spirit of Epsilon IV, a narrative of a civilization that had risen, evolved, and returned to the cosmic canvas.

Astria's final note was a gentle, serene hum, embodying the wisdom of her age, the tranquility of acceptance, and the promise of new beginnings. It was her final farewell, her last love letter to her home, her people, and the universe that had cradled her existence.

The tale of her symphony spread across the galaxies, touching the hearts and souls of countless civilizations. It inspired poets to pen verses about the beauty of existence, scientists to ponder the mysteries of the universe, and dreamers to gaze at the stars and wonder.

Even as time marched on, as stars flickered out and new ones ignited, the echo of Astria's symphony lived on. It served as a reminder of the fleeting beauty of existence, the power of expression, and the enduring legacy one can leave behind.

Epsilon IV was silent now, its light composer returned to the cosmos. But the silence was not empty. It was filled with the echoes of a symphony that had once lit up the skies, a symphony that told a tale of life's beautiful impermanence.

And so, Astria lived on. Not as a physical being, not as a flicker in the sky, but as a melody in the hearts of the universe. The Last Symphony of Epsilon IV would forever be a part of the cosmic orchestra, an everlasting melody amidst the celestial silence. In every pulse of light, in every wave of energy, her spirit danced, her music played, her story unfolded – a symphony of existence, a song of the cosmos.
    """
    embeddings, all_texts, all_indexes = await embedding_transformer.async_encode(text, title, section_name)
    for i in range(len(embeddings)):
        embedding = embeddings[i]
        text_chunk = all_texts[i]
        index = all_indexes[i]
        # print(text_chunk)
        print(index)
        # print(embedding[:3], '...', embedding[-3:])

    # Tokenize the text and count tokens
    tokens = tokenizer.tokenize(text)
    num_tokens = len(tokens)

    print(f'The text contains {num_tokens} tokens.')


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
