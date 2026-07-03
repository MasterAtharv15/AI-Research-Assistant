import shutil
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException

app = FastAPI(title="AI Research Assistant")

# Define the uploads directory
UPLOAD_DIR = Path(__file__).parent / "uploads"


@app.get("/")
def read_root() -> dict[str, str]:
    """Return the API welcome message."""
    return {"message": "AI Research Assistant API is running"}


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return the API health status."""
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    """
    Upload a PDF file to the server.

    Args:
        file: The uploaded file (must be PDF).

    Returns:
        Dictionary with filename and success message.

    Raises:
        HTTPException: 400 if file is not a PDF.
    """
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # Create uploads directory if it doesn't exist
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Save the file
    file_path = UPLOAD_DIR / file.filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "filename": file.filename,
        "message": "File uploaded successfully"
    }
