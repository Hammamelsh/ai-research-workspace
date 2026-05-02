from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from datetime import datetime
import os

from app.services.storage import save_file_locally
from app.services.validation import validate_upload
from app.services.extraction import extract_text_from_pdf
from app.models.document import (
    DocumentUploadResponse,
    DocumentProcessResponse,
    PageContent,
    DocumentMetadata,
)
from app.core.config import get_settings, Settings

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=201,
    tags=["Documents"],
    summary="Upload a PDF document",
)
async def upload_document(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    await validate_upload(file)
    file_metadata = await save_file_locally(file)

    return DocumentUploadResponse(
        file_id=file_metadata["file_id"],
        original_filename=file_metadata["original_filename"],
        file_size_bytes=file_metadata["file_size_bytes"],
        content_type=file_metadata["content_type"],
        status="uploaded",
        message="File uploaded successfully. Ready for processing.",
        uploaded_at=datetime.utcnow()
    )


@router.post(
    "/{file_id}/process",
    response_model=DocumentProcessResponse,
    status_code=200,
    tags=["Documents"],
    summary="Extract text from an uploaded PDF",
)
async def process_document(
    file_id: str,
    settings: Settings = Depends(get_settings)
):
    """
    Find the uploaded file by ID and extract its text.
    
    Why is this a separate endpoint from upload?
    
    Because upload and processing are different concerns
    with different failure modes and different durations.
    Upload is fast (seconds). Processing could be slow (minutes
    for large docs). Separating them lets the frontend show
    progress and retry independently.
    """

    # Find the file in uploads/ directory
    # Remember: stored as {uuid}_{original_name}.pdf
    upload_dir = "uploads"
    matching_files = [
        f for f in os.listdir(upload_dir)
        if f.startswith(file_id)
    ]

    if not matching_files:
        raise HTTPException(
            status_code=404,
            detail=f"No file found with ID: {file_id}"
        )

    file_path = os.path.join(upload_dir, matching_files[0])
    original_filename = matching_files[0][len(file_id) + 1:]  # strip uuid_ prefix

    # Extract text
    try:
        result = extract_text_from_pdf(file_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found on disk")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}"
        )

    # Warn but don't fail on scanned PDFs
    if result["extraction_quality"] == "scanned_pdf_no_text":
        message = (
            "Warning: This PDF appears to be scanned. "
            "No text could be extracted. OCR support coming in Phase 2."
        )
    else:
        message = (
            f"Extraction complete. "
            f"Quality: {result['extraction_quality']}. "
            f"{result['total_characters']} characters extracted."
        )

    return DocumentProcessResponse(
        file_id=file_id,
        original_filename=original_filename,
        total_pages=result["total_pages"],
        empty_pages=result["empty_pages"],
        total_characters=result["total_characters"],
        extraction_quality=result["extraction_quality"],
        metadata=DocumentMetadata(**result["metadata"]),
        pages=[PageContent(**p) for p in result["pages"]],
        status="processed",
        message=message,
        processed_at=datetime.utcnow()
    )