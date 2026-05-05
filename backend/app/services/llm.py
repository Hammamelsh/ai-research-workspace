from groq import Groq
from typing import List
from functools import lru_cache
from app.core.config import get_settings

settings = get_settings()


@lru_cache()
def get_groq_client():
    return Groq(api_key=settings.groq_api_key)


def build_rag_prompt(query: str, retrieved_chunks: List[dict]) -> str:
    context_blocks = []
    for i, chunk in enumerate(retrieved_chunks):
        metadata = chunk.get("metadata", {})
        filename = metadata.get("original_filename", "Unknown")
        page = metadata.get("page_number", "Unknown")
        score = chunk.get("similarity_score", 0)

        block = f"""[Source {i + 1}]
File: {filename}
Page: {page}
Relevance Score: {score}
Content:
{chunk['text']}""".strip()
        context_blocks.append(block)

    context_section = "\n\n---\n\n".join(context_blocks)

    return f"""You are an expert research assistant.
Answer questions using ONLY the provided source documents.

STRICT RULES:
- Use ONLY the context below
- If the context lacks enough info, say: "I could not find sufficient information in the provided documents."
- Always cite which source you used (e.g. "According to Source 1, page 4...")
- Be concise but complete

---

CONTEXT FROM DOCUMENTS:

{context_section}

---

QUESTION:
{query}

---

ANSWER (cite your sources):"""


def generate_answer(query: str, retrieved_chunks: List[dict]) -> dict:
    if not retrieved_chunks:
        return {
            "answer": "No relevant documents found. Please upload and embed a document first.",
            "sources": [],
            "model": settings.groq_model,
            "prompt_preview": "",
        }

    prompt = build_rag_prompt(query, retrieved_chunks)
    client = get_groq_client()

    try:
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise research assistant. Answer only from provided context."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,   # low = more factual, less creative
            max_tokens=1024,
        )
        answer_text = response.choices[0].message.content

    except Exception as e:
        raise Exception(f"Groq API error: {str(e)}")

    sources = []
    for i, chunk in enumerate(retrieved_chunks):
        metadata = chunk.get("metadata", {})
        sources.append({
            "source_number": i + 1,
            "filename": metadata.get("original_filename", "Unknown"),
            "page_number": metadata.get("page_number"),
            "similarity_score": chunk.get("similarity_score"),
            "text_preview": chunk["text"][:200] + "...",
        })

    return {
        "answer": answer_text,
        "sources": sources,
        "model": settings.groq_model,
        "prompt_preview": prompt[:200] + "...",
    }