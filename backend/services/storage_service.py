"""Storage utilities for persisting and loading chunked text."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

__all__ = ["save_chunks", "load_chunks"]

CHUNK_STORAGE_DIR = Path(__file__).resolve().parent.parent / "data" / "chunks"


def save_chunks(chunks: List[str], file_name: str) -> None:
    """Save a list of text chunks into a JSON file.

    The file is stored under `data/chunks/` using the provided file name.
    The target directory is created automatically if needed.

    Args:
        chunks: The list of text chunks to save.
        file_name: The name of the JSON file to create.

    Raises:
        TypeError: If the arguments are not of the expected types.
        ValueError: If `file_name` is empty.
    """
    if not isinstance(chunks, list):
        raise TypeError("`chunks` must be a list of strings")
    if any(not isinstance(chunk, str) for chunk in chunks):
        raise TypeError("All items in `chunks` must be strings")
    if not isinstance(file_name, str):
        raise TypeError("`file_name` must be a string")
    if not file_name.strip():
        raise ValueError("`file_name` must not be empty")

    CHUNK_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    target_path = CHUNK_STORAGE_DIR / file_name

    with target_path.open("w", encoding="utf-8") as handle:
        json.dump(chunks, handle, ensure_ascii=False, indent=2)


def load_chunks(file_name: str) -> List[str]:
    """Load chunks from a JSON file under `data/chunks/`.

    Args:
        file_name: The name of the JSON file to load.

    Returns:
        The list of chunks stored in the file.

    Raises:
        TypeError: If `file_name` is not a string.
        ValueError: If `file_name` is empty.
        FileNotFoundError: If the requested file does not exist.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    if not isinstance(file_name, str):
        raise TypeError("`file_name` must be a string")
    if not file_name.strip():
        raise ValueError("`file_name` must not be empty")

    target_path = CHUNK_STORAGE_DIR / file_name
    with target_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, list) or any(not isinstance(item, str) for item in data):
        raise ValueError(f"Loaded data from '{file_name}' is not a list of strings")

    return data
