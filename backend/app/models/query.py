from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class QueryRequest(BaseModel):
    """
    What the user sends to ask a question.
    file_id is optional — None means search all documents.
    """
    query: str
    file_id: Optional[str] = None
    top_k: int = 5


class SourceCitation(BaseModel):
    source_number: int
    filename: str
    page_number: Optional[int] = None
    similarity_score: Optional[float] = None
    text_preview: str


class QueryResponse(BaseModel):
    query: str
    answer: str
    sources: List[SourceCitation]
    model: str
    file_id: Optional[str] = None
    chunks_retrieved: int
    asked_at: datetime
    