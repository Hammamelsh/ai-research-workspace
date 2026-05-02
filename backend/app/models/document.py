from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class DocumentUploadResponse(BaseModel):
    file_id: str
    original_filename: str
    file_size_bytes: int
    content_type: str
    status: str
    message: str
    uploaded_at: datetime


# --- Add these below ---

class PageContent(BaseModel):
    page_number: int
    text: str
    char_count: int
    is_empty: bool


class DocumentMetadata(BaseModel):
    title: Optional[str] = ""
    author: Optional[str] = ""
    subject: Optional[str] = ""
    creator: Optional[str] = ""


class DocumentProcessResponse(BaseModel):
    file_id: str
    original_filename: str
    total_pages: int
    empty_pages: int
    total_characters: int
    extraction_quality: str
    metadata: DocumentMetadata
    pages: List[PageContent]
    status: str
    message: str
    processed_at: datetime
