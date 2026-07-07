"""Semantic search utilities for chunked text."""

from __future__ import annotations

from typing import Any, TypedDict

import numpy as np

from backend.services.embedding_service import generate_embedding

__all__ = ["search_chunks"]


class StoredChunk(TypedDict, total=False):
    """Structured chunk record stored alongside its embedding."""

    chunk_id: int
    text: str
    embedding: list[float]


def _validate_stored_chunks(stored_chunks: list[dict[str, Any]]) -> None:
    """Validate the structure of stored chunk records."""
    if not isinstance(stored_chunks, list):
        raise TypeError("`stored_chunks` must be a list of chunk dictionaries")

    for chunk in stored_chunks:
        if not isinstance(chunk, dict):
            raise TypeError("All items in `stored_chunks` must be dictionaries")
        if "chunk_id" not in chunk or "text" not in chunk:
            raise ValueError("Each chunk must contain `chunk_id` and `text`")
        if not isinstance(chunk["chunk_id"], int):
            raise TypeError("`chunk_id` must be an int")
        if not isinstance(chunk["text"], str):
            raise TypeError("`text` must be a string")

        if "embedding" not in chunk or chunk["embedding"] is None:
            chunk["embedding"] = None
            continue
        if not isinstance(chunk["embedding"], list) or any(
            not isinstance(value, (int, float)) for value in chunk["embedding"]
        ):
            chunk["embedding"] = None


def _cosine_similarity(query_vector: np.ndarray, candidate_vector: np.ndarray) -> float:
    """Compute cosine similarity between two vectors."""
    query_norm = np.linalg.norm(query_vector)
    candidate_norm = np.linalg.norm(candidate_vector)
    if query_norm == 0.0 or candidate_norm == 0.0:
        return 0.0
    return float(np.dot(query_vector, candidate_vector) / (query_norm * candidate_norm))


def search_chunks(
    query: str,
    stored_chunks: list[dict[str, Any]],
    top_k: int = 5,
) -> list[StoredChunk]:
    """Find the most semantically relevant stored chunks for a query.

    Args:
        query: The search query text.
        stored_chunks: Chunk dictionaries containing text and embeddings.
        top_k: The maximum number of matches to return.

    Returns:
        A list of matching chunk dictionaries sorted from highest similarity to lowest.

    Raises:
        TypeError: If the inputs are not of the expected types.
        ValueError: If `top_k` is less than 1.
    """
    if not isinstance(query, str):
        raise TypeError("`query` must be a string")
    if not isinstance(top_k, int):
        raise TypeError("`top_k` must be an int")
    if top_k < 1:
        raise ValueError("`top_k` must be at least 1")

    _validate_stored_chunks(stored_chunks)

    if not query.strip():
        return []

    try:
        query_embedding = np.asarray(generate_embedding(query), dtype=float)
    except Exception:
        query_embedding = None

    scored_chunks: list[tuple[float, StoredChunk]] = []

    for chunk in stored_chunks:
        embedding = chunk.get("embedding")
        if query_embedding is None:
            text = str(chunk.get("text", "")).lower()
            query_terms = {term for term in query.lower().split() if term}
            text_terms = {term for term in text.split() if term}
            overlap = len(query_terms & text_terms)
            if overlap > 0:
                scored_chunks.append((float(overlap), chunk))
            continue

        if not isinstance(embedding, list) or not embedding:
            continue
        if any(not isinstance(value, (int, float)) for value in embedding):
            continue

        candidate_vector = np.asarray(embedding, dtype=float)
        if candidate_vector.shape != query_embedding.shape:
            continue

        similarity = _cosine_similarity(query_embedding, candidate_vector)
        scored_chunks.append((similarity, chunk))

    scored_chunks.sort(key=lambda item: (-item[0], item[1].get("chunk_id", 0)))
    return [chunk for _, chunk in scored_chunks[:top_k]]
