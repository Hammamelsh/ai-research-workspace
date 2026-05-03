import chromadb
from chromadb.config import Settings as ChromaSettings
from typing import List
from app.core.config import get_settings
from functools import lru_cache

settings = get_settings()


@lru_cache()
def get_chroma_client():
    """
    Initialise ChromaDB client once and cache it.
    Data is persisted to disk at chroma_db_path.
    """
    client = chromadb.PersistentClient(
        path=settings.chroma_db_path,
    )
    return client


def get_or_create_collection(collection_name: str = "documents"):
    """
    Get an existing ChromaDB collection or create a new one.

    A collection is like a table in a database — it holds a
    set of related vectors. We use one collection for all documents.
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"},  # use cosine similarity
    )
    return collection


def store_embeddings(chunks_with_embeddings: List[dict]) -> dict:
    """
    Store embedded chunks in ChromaDB.

    ChromaDB needs four things per chunk:
    - ids        unique string ID for each chunk
    - embeddings the vector (list of floats)
    - documents  the raw text (so we can return it on retrieval)
    - metadatas  any extra info (filename, page number, etc.)
    """
    collection = get_or_create_collection()

    ids = []
    embeddings = []
    documents = []
    metadatas = []

    for chunk in chunks_with_embeddings:
        ids.append(chunk["chunk_id"])
        embeddings.append(chunk["embedding"])
        documents.append(chunk["text"])
        metadatas.append({
            "file_id": chunk["file_id"],
            "original_filename": chunk["original_filename"],
            "chunk_index": chunk["chunk_index"],
            "page_number": chunk.get("page_number") or 0,
            "token_count": chunk["token_count"],
        })

    # Upsert = insert if new, update if ID already exists
    # This means re-embedding the same file is safe — no duplicates
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas,
    )

    return {
        "stored_count": len(ids),
        "collection_name": collection.name,
        "total_in_collection": collection.count(),
    }


def search_similar_chunks(
    query_embedding: List[float],
    file_id: str = None,
    top_k: int = 5,
) -> List[dict]:
    """
    Find the top_k most similar chunks to a query embedding.

    file_id filter: optionally restrict search to one document.
    If None, searches across ALL documents in the collection.
    """
    collection = get_or_create_collection()

    # Build optional filter
    where_filter = {"file_id": file_id} if file_id else None

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    # Reformat ChromaDB's response into clean dicts
    chunks = []
    for i in range(len(results["ids"][0])):
        chunks.append({
            "chunk_id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i],
            # Distance → similarity: closer to 1.0 = more similar
            "similarity_score": round(1 - results["distances"][0][i], 4),
        })

    return chunks
