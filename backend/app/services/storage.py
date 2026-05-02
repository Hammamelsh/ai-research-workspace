import os
import uuid
import aiofiles
from fastapi import UploadFile

# Base directory for all uploads (relative to backend/)
UPLOAD_DIR = "uploads"


async def save_file_locally(file: UploadFile) -> dict:
    """
    Save an uploaded file to local disk.
    Returns metadata about the saved file.
    
    In Phase 4 this function gets replaced with save_file_to_s3()
    The router never changes. Only this service does.
    """

    # Generate a unique ID for this file
    # Why? Two users uploading "report.pdf" would overwrite each other
    file_id = str(uuid.uuid4())
    
    # Build a safe filename: {uuid}_{original_name}
    safe_filename = f"{file_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)

    # Write the file to disk asynchronously
    # async with means: open, do the work, close automatically
    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)

    # Get the file size from what we just wrote
    file_size = os.path.getsize(file_path)

    return {
        "file_id": file_id,
        "original_filename": file.filename,
        "stored_filename": safe_filename,
        "file_path": file_path,
        "file_size_bytes": file_size,
        "content_type": file.content_type,
    }
