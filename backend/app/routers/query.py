from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from app.services.embedding import embed_text
from app.services.vector_store import search_similar_chunks
from app.services.llm import generate_answer
from app.models.query import QueryRequest, QueryResponse, SourceCitation
from app.core.config import get_settings, Settings

router = APIRouter()


@router.post(
    "/",
    response_model=QueryResponse,
    status_code=200,
    tags=["Query"],
    summary="Ask a question about your documents",
)
async def query_documents(
    request: QueryRequest,
    settings: Settings = Depends(get_settings),
):
    """
    The complete RAG pipeline in one endpoint:

    1. Embed the user's question
    2. Search ChromaDB for relevant chunks
    3. Send chunks + question to Gemini
    4. Return grounded answer with citations

    This is the endpoint your frontend chat UI will call.
    """

    # Validate query is not empty
    if not request.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    # Step 1 — Embed the query
    # Same model used for chunks = compatible vector space
    try:
        query_embedding = embed_text(request.query)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Embedding failed: {str(e)}"
        )

    # Step 2 — Retrieve relevant chunks
    try:
        retrieved_chunks = search_similar_chunks(
            query_embedding=query_embedding,
            file_id=request.file_id,   # None = search all docs
            top_k=request.top_k,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval failed: {str(e)}"
        )

    # Step 3 — Generate answer with Gemini
    try:
        result = generate_answer(
            query=request.query,
            retrieved_chunks=retrieved_chunks,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Generation failed: {str(e)}"
        )

    # Step 4 — Return structured response
    return QueryResponse(
        query=request.query,
        answer=result["answer"],
        sources=[SourceCitation(**s) for s in result["sources"]],
        model=result["model"],
        file_id=request.file_id,
        chunks_retrieved=len(retrieved_chunks),
        asked_at=datetime.utcnow(),
    )