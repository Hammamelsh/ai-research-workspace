from pydantic import BaseModel
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    """
    What the API returns after a successful upload.
    Pydantic ensures this shape is always correct.
    """
    file_id: str
    original_filename: str
    file_size_bytes: int
    content_type: str
    status: str
    message: str
    uploaded_at: datetime