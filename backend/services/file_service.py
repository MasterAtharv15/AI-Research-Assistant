"""File upload utilities."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from fastapi import UploadFile

__all__ = ["UploadFile", "save_uploaded_file"]

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
_FILENAME_NORMALIZATION_PATTERN = re.compile(r"[^\w\-. ]+")


class FileSaveError(Exception):
    """Raised when saving an uploaded file fails."""


def _normalize_filename(filename: str) -> str:
    normalized = Path(filename).name
    normalized = normalized.strip().replace(" ", "_")
    normalized = _FILENAME_NORMALIZATION_PATTERN.sub("_", normalized)

    if not normalized or normalized in {"..", "."}:
        raise ValueError("Uploaded filename is invalid or empty.")

    return normalized


def save_uploaded_file(upload_file: UploadFile) -> str:
    """Save an uploaded file to the uploads directory.

    The uploads directory is created automatically if needed. The file name is
    normalized to prevent path traversal vulnerabilities.

    Args:
        upload_file: The incoming uploaded file from FastAPI.

    Returns:
        The absolute path to the saved file.

    Raises:
        ValueError: If the uploaded file does not include a valid filename.
        FileSaveError: If saving the file fails.
    """
    if not upload_file.filename:
        raise ValueError("Uploaded file must include a filename.")

    safe_filename = _normalize_filename(upload_file.filename)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    destination_path = UPLOAD_DIR / safe_filename
    try:
        destination_path = destination_path.resolve()
        upload_dir_path = UPLOAD_DIR.resolve()
        if not destination_path.is_relative_to(upload_dir_path):
            raise ValueError("The resolved file path is outside of the uploads directory.")
    except AttributeError:
        # Python < 3.9 compatibility fallback for is_relative_to
        if str(destination_path).startswith(str(upload_dir_path) + str(Path("/") if not str(upload_dir_path).endswith("/") else "")) is False:
            raise ValueError("The resolved file path is outside of the uploads directory.")

    try:
        try:
            upload_file.file.seek(0)
        except OSError:
            pass

        with destination_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as exc:
        raise FileSaveError(
            f"Failed to save uploaded file '{upload_file.filename}' to '{destination_path}': {exc}"
        ) from exc

    return str(destination_path)
