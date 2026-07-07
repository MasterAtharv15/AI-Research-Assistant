"""Upload routes."""

from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.services.chunk_service import chunk_text
from backend.services.file_service import save_uploaded_file
from backend.services.storage_service import save_chunks

router = APIRouter()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, object]:
    """Upload a file, save it, extract text from the PDF, and return results."""
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    saved_path = save_uploaded_file(file)
    try:
        from backend.services.pdf_service import PdfExtractionError, extract_text

        extracted_text = extract_text(saved_path)
        chunks = chunk_text(extracted_text)
        save_chunks(file.filename, chunks)
    except PdfExtractionError as exc:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {exc}") from exc
    except Exception as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=500, detail=f"Unexpected error during PDF extraction: {exc}") from exc

    return {
        "filename": file.filename,
        "extracted_text": extracted_text,
        "num_characters": len(extracted_text),
        "num_chunks": len(chunks),
        "first_chunk": chunks[0] if chunks else "",
    }
