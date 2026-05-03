"""
Temporary test script — run once to verify search works
Delete after testing
"""
from app.services.embedding import embed_text
from app.services.vector_store import search_similar_chunks

# Embed a test query
query = "What is the main topic of this document?"
query_embedding = embed_text(query)

print(f"Query embedding dimensions: {len(query_embedding)}")

# Search
results = search_similar_chunks(query_embedding, top_k=3)

print(f"\nTop {len(results)} results:")
for r in results:
    print(f"\nScore: {r['similarity_score']}")
    print(f"Page: {r['metadata']['page_number']}")
    print(f"Text: {r['text'][:200]}...")