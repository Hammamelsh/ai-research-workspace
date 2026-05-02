import os
from fastapi import UploadFile, HTTPException

# Constants — defined once, used everywhere
ALLOWED_CONTENT_TYPES = ["application/pdf"]
ALLOWED_EXTENSIONS = [".pdf"]
MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


async def validate_upload(file: UploadFile) -> None:
    """
    Validate file type and size before processing.
    Raises HTTPException if validation fails.
    Returns None if everything is fine.
    """

    # --- Check content type ---
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Only PDFs are accepted."
        )

    # --- Check file extension ---
    # Content type can be spoofed. Always check extension too.
    if file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file extension: {ext}. Only .pdf files are accepted."
            )

    # --- Check file size ---
    # Read content, check size, then reset so the router can read it again
    content = await file.read()
    if len(content) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB."
        )

    # Reset file pointer so downstream code can read the file again
    await file.seek(0)