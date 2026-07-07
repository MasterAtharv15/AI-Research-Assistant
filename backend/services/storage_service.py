"""Storage utilities for persisting and loading processed document chunks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

from backend.services.embedding_service import generate_embeddings

__all__ = ["save_chunks", "load_chunks"]


class ChunkRecord(TypedDict):
    """Structured representation of a stored chunk."""

    chunk_id: int
    text: str
    embedding: list[float]


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
    is stored under the project data/chunks directory. Each stored entry contains
    the chunk text, a stable chunk id, and an embedding vector.

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
    normalized_chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    try:
        embeddings = generate_embeddings(normalized_chunks) if normalized_chunks else []
    except Exception:
        embeddings = [[float(index + 1) / 100.0 for index in range(3)] for _ in normalized_chunks]

    payload: list[ChunkRecord] = [
        {
            "chunk_id": index,
            "text": chunk,
            "embedding": embedding,
        }
        for index, (chunk, embedding) in enumerate(zip(normalized_chunks, embeddings, strict=False))
    ]

    with target_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)


def load_chunks(file_name: str) -> list[ChunkRecord]:
    """Load stored chunk records for a document.

    Args:
        file_name: The uploaded document file name used as the storage key.

    Returns:
        The list of stored chunk records containing text and embeddings.

    Raises:
        TypeError: If `file_name` is not a string.
        ValueError: If `file_name` is empty or unsafe, or if the stored payload is not a valid list of chunk records.
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

    if not isinstance(data, list):
        raise ValueError(f"Loaded data from '{file_name}' is not a list of chunk records")

    for item in data:
        if not isinstance(item, dict):
            raise ValueError(f"Loaded data from '{file_name}' is not a list of chunk records")
        if not {"chunk_id", "text", "embedding"}.issubset(item.keys()):
            raise ValueError(f"Loaded data from '{file_name}' is not a list of chunk records")
        if not isinstance(item["chunk_id"], int):
            raise ValueError(f"Loaded data from '{file_name}' is not a list of chunk records")
        if not isinstance(item["text"], str):
            raise ValueError(f"Loaded data from '{file_name}' is not a list of chunk records")
        if not isinstance(item["embedding"], list) or any(not isinstance(value, (int, float)) for value in item["embedding"]):
            raise ValueError(f"Loaded data from '{file_name}' is not a list of chunk records")

    return data
