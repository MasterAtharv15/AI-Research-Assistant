"""Upload routes."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.services.file_service import save_uploaded_file

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    """Upload a file and save it using the shared file service."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    saved_path = save_uploaded_file(file)
    return {
        "filename": file.filename,
        "path": saved_path,
        "message": "File uploaded successfully",
    }
