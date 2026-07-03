"""PDF text extraction service."""

from __future__ import annotations

import fitz

__all__ = ["PdfExtractionError", "extract_text"]


class PdfExtractionError(Exception):
    """Raised when PDF extraction fails."""


def extract_text(pdf_path: str) -> str:
    """Extract all text from a PDF file using PyMuPDF.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        All extracted text from the PDF.

    Raises:
        ValueError: If pdf_path is empty or not a string.
        PdfExtractionError: If the PDF cannot be opened or text extraction fails.
    """
    if not isinstance(pdf_path, str) or not pdf_path.strip():
        raise ValueError("pdf_path must be a non-empty string.")

    try:
        with fitz.open(pdf_path) as document:
            text_fragments = [page.get_text("text") for page in document]
    except Exception as exc:
        raise PdfExtractionError(f"Unable to open or extract text from PDF '{pdf_path}': {exc}") from exc

    return "\n".join(fragment for fragment in text_fragments if fragment).strip()
