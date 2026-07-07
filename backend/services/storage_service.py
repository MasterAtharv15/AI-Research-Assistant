"""Storage utilities for persisting and loading processed document chunks."""

from __future__ import annotations

import json
from pathlib import Path

__all__ = ["save_chunks", "load_chunks"]


def _chunk_storage_dir() -> Path:
    """Return the directory used to store chunk JSON files.

    Returns:
        The absolute path to the chunk storage directory.
    """
    return Path(__file__).resolve().parents[2] / "data" / "chunks"


def _resolve_chunk_path(file_name: str) -> Path:
    """Validate a supplied file name and return its chunk JSON path.

    Args:
        file_name: The uploaded document file name.

    Returns:
        The resolved chunk JSON path.

    Raises:
        TypeError: If the file name is not a string.
        ValueError: If the file name is empty or unsafe.
    """
    if not isinstance(file_name, str):
        raise TypeError("`file_name` must be a string")

    normalized_name = file_name.strip()
    if not normalized_name:
        raise ValueError("`file_name` must not be empty")

    path = Path(normalized_name)
    if path.is_absolute() or path.name != normalized_name or any(
        part in {"", ".", ".."} for part in path.parts
    ):
        raise ValueError("`file_name` must be a safe file name")

    storage_dir = _chunk_storage_dir()
    storage_dir.mkdir(parents=True, exist_ok=True)
    return storage_dir / f"{path.stem}.json"


def save_chunks(file_name: str, chunks: list[str]) -> None:
    """Persist a list of text chunks as JSON for a document.

    The chunk file uses the uploaded document's base name with a .json suffix and
    is stored under the project data/chunks directory.

    Args:
        file_name: The uploaded document file name used as the storage key.
        chunks: The list of text chunks to save.

    Raises:
        TypeError: If `file_name` is not a string or `chunks` is not a list of strings.
        ValueError: If `file_name` is empty or unsafe, or if `chunks` contains non-string items.
    """
    if not isinstance(chunks, list):
        raise TypeError("`chunks` must be a list of strings")
    if any(not isinstance(chunk, str) for chunk in chunks):
        raise TypeError("All items in `chunks` must be strings")

    target_path = _resolve_chunk_path(file_name)
    with target_path.open("w", encoding="utf-8") as handle:
        json.dump(chunks, handle, ensure_ascii=False, indent=2)


def load_chunks(file_name: str) -> list[str]:
    """Load a list of stored chunks for a document.

    Args:
        file_name: The uploaded document file name used as the storage key.

    Returns:
        The list of chunks stored in the corresponding JSON file.

    Raises:
        TypeError: If `file_name` is not a string.
        ValueError: If `file_name` is empty or unsafe, or if the stored payload is not a list of strings.
        FileNotFoundError: If the requested chunk file does not exist.
    """
    target_path = _resolve_chunk_path(file_name)
    try:
        with target_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Chunk file '{file_name}' does not exist") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"Chunk file '{file_name}' contains invalid JSON") from exc

    if not isinstance(data, list) or any(not isinstance(item, str) for item in data):
        raise ValueError(f"Loaded data from '{file_name}' is not a list of strings")

    return data
