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

class ChunkData(BaseModel):
    chunk_index: int
    chunk_id: str
    file_id: str
    text: str
    token_count: int
    page_number: Optional[int] = None


class ChunkStats(BaseModel):
    total_chunks: int
    total_tokens: int
    avg_tokens_per_chunk: float
    min_tokens: int
    max_tokens: int
    chunk_size_config: int
    chunk_overlap_config: int


class DocumentChunkResponse(BaseModel):
    file_id: str
    original_filename: str
    stats: ChunkStats
    chunks: List[ChunkData]
    status: str
    message: str
    chunked_at: datetime

class EmbedStats(BaseModel):
    chunks_embedded: int
    stored_count: int
    collection_name: str
    total_in_collection: int
    embedding_model: str
    embedding_dimensions: int


class DocumentEmbedResponse(BaseModel):
    file_id: str
    original_filename: str
    stats: EmbedStats
    status: str
    message: str
    embedded_at: datetime