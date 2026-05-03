import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List


# Default chunking configuration
# These values are tuned for RAG over general documents
# You will want to experiment with these in Phase 2
DEFAULT_CHUNK_SIZE = 500        # tokens per chunk
DEFAULT_CHUNK_OVERLAP = 50      # tokens of overlap between chunks
ENCODING_MODEL = "cl100k_base"  # tokeniser used by OpenAI + most embedding models


def count_tokens(text: str) -> int:
    """
    Count the number of tokens in a string.
    
    Why not just use len(text.split())?
    Because word count ≠ token count.
    "ChatGPT" = 1 word, 3 tokens.
    Token-aware chunking respects model limits precisely.
    """
    encoding = tiktoken.get_encoding(ENCODING_MODEL)
    return len(encoding.encode(text))


def chunk_text(
    text: str,
    file_id: str,
    original_filename: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> List[dict]:
    """
    Split text into overlapping chunks with metadata.
    
    Uses RecursiveCharacterTextSplitter which tries to split on:
    1. Paragraphs (double newline)
    2. Sentences (single newline)  
    3. Words (space)
    4. Characters (last resort)
    
    This hierarchy preserves semantic boundaries as much as possible.
    It never splits mid-sentence if it can avoid it.
    """

    # Initialise the splitter
    # length_function=count_tokens means chunk_size is in TOKENS not chars
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=count_tokens,
        separators=["\n\n", "\n", " ", ""],
    )

    # Split the text
    raw_chunks = splitter.split_text(text)

    # Build enriched chunk objects with metadata
    chunks = []
    for index, chunk_text_content in enumerate(raw_chunks):

        # Extract page number from [Page N] markers if present
        page_number = _extract_page_number(chunk_text_content)

        token_count = count_tokens(chunk_text_content)

        chunks.append({
            "chunk_index": index,           # position in sequence
            "chunk_id": f"{file_id}_chunk_{index}",  # unique ID for vector store
            "file_id": file_id,
            "original_filename": original_filename,
            "text": chunk_text_content,
            "token_count": token_count,
            "page_number": page_number,
            "chunk_size_config": chunk_size,
            "chunk_overlap_config": chunk_overlap,
        })

    return chunks


def _extract_page_number(text: str) -> int | None:
    """
    Extract the most recent [Page N] marker from chunk text.
    
    When text is chunked, page markers from extraction flow in.
    This lets us tell the user which page a retrieved chunk came from.
    
    Example:
        "[Page 3]\nThe policy states that..." → returns 3
    """
    import re
    matches = re.findall(r'\[Page (\d+)\]', text)
    if matches:
        # Return the last page number found in this chunk
        return int(matches[-1])
    return None


def get_chunk_stats(chunks: List[dict]) -> dict:
    """
    Return summary statistics about a set of chunks.
    Useful for debugging and monitoring chunk quality.
    """
    if not chunks:
        return {"total_chunks": 0}

    token_counts = [c["token_count"] for c in chunks]

    return {
        "total_chunks": len(chunks),
        "total_tokens": sum(token_counts),
        "avg_tokens_per_chunk": round(sum(token_counts) / len(token_counts), 1),
        "min_tokens": min(token_counts),
        "max_tokens": max(token_counts),
        "chunk_size_config": chunks[0]["chunk_size_config"],
        "chunk_overlap_config": chunks[0]["chunk_overlap_config"],
    }
