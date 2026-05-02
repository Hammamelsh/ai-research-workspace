from fastapi import APIRouter, UploadFile, File, Depends
from datetime import datetime
from app.services.storage import save_file_locally
from app.services.validation import validate_upload
from app.models.document import DocumentUploadResponse
from app.core.config import get_settings, Settings

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=201,
    tags=["Documents"],
    summary="Upload a PDF document",
    description="Upload a PDF file for processing. Max size 20MB."
)
async def upload_document(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    """
    Upload flow:
    1. Validate the file (type, size)
    2. Save to storage
    3. Return metadata
    
    Processing (chunking, embedding) happens separately.
    This endpoint only handles the upload concern.
    """

    # Step 1 — Validate
    await validate_upload(file)

    # Step 2 — Save
    file_metadata = await save_file_locally(file)

    # Step 3 — Return structured response
    return DocumentUploadResponse(
        file_id=file_metadata["file_id"],
        original_filename=file_metadata["original_filename"],
        file_size_bytes=file_metadata["file_size_bytes"],
        content_type=file_metadata["content_type"],
        status="uploaded",
        message="File uploaded successfully. Ready for processing.",
        uploaded_at=datetime.utcnow()
    )
