from sentence_transformers import SentenceTransformer
from typing import List
from functools import lru_cache
from app.core.config import get_settings

settings = get_settings()


@lru_cache()
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model once and cache it.

    Why lru_cache here?
    Loading a model from disk takes 2-3 seconds.
    If we loaded it on every API request, every embed call
    would have a 3 second delay. Caching loads it once on
    first call and reuses the same object forever after.
    This is called model warming — standard in production.
    """
    print(f"Loading embedding model: {settings.embedding_model}")
    return SentenceTransformer(settings.embedding_model)


def embed_text(text: str) -> List[float]:
    """
    Convert a single string into an embedding vector.

    Returns a list of floats e.g. [0.23, -0.81, 0.45, ...]
    The length of this list is always 384 for all-MiniLM-L6-v2
    This fixed length is called the embedding dimension.
    """
    model = get_embedding_model()

    # encode() returns a numpy array — convert to plain Python list
    # Why? JSON serialisation doesn't know how to handle numpy arrays
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_chunks(chunks: List[dict]) -> List[dict]:
    """
    Embed a list of chunk dicts in one batch.

    Why batch? Embedding models process text in parallel.
    Embedding 100 chunks in one call is much faster than
    100 individual calls — the model amortises the overhead.
    """
    model = get_embedding_model()

    # Extract just the text from each chunk for batch processing
    texts = [chunk["text"] for chunk in chunks]

    print(f"Embedding {len(texts)} chunks in batch...")

    # encode() with a list processes all texts in one forward pass
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,   # shows progress for large docs
        batch_size=32,            # process 32 at a time
    )

    # Attach embedding back to each chunk dict
    enriched_chunks = []
    for chunk, embedding in zip(chunks, embeddings):
        enriched = {**chunk, "embedding": embedding.tolist()}
        enriched_chunks.append(enriched)

    return enriched_chunks