"""Search utilities for chunked text."""

from __future__ import annotations

from typing import List, Tuple

__all__ = ["search_chunks"]


def search_chunks(chunks: List[str], query: str, top_k: int = 3) -> List[str]:
    """Find the best matching chunks for a query using keyword scoring.

    This search implementation is intentionally simple. It tokenizes the query
    by whitespace, lowercases terms, and then scores each chunk by counting how
    many distinct query words appear in the chunk.

    Args:
        chunks: A list of text chunks to search.
        query: The query string containing one or more keywords.
        top_k: The maximum number of top matches to return.

    Returns:
        A list of the best matching chunks, ordered by descending score.
        Chunks with a score of zero are excluded.

    Raises:
        TypeError: If arguments are the wrong type.
        ValueError: If `top_k` is less than 1.
    """
    if not isinstance(chunks, list):
        raise TypeError("`chunks` must be a list of strings")
    if not isinstance(query, str):
        raise TypeError("`query` must be a string")
    if not isinstance(top_k, int):
        raise TypeError("`top_k` must be an int")

    if top_k < 1:
        raise ValueError("`top_k` must be at least 1")

    normalized_query = query.lower().strip()
    if not normalized_query:
        return []

    query_words = {word for word in normalized_query.split() if word}
    if not query_words:
        return []

    scored_chunks: List[Tuple[int, int, str]] = []
    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, str):
            raise TypeError("All items in `chunks` must be strings")

        token_set = set(chunk.lower().split())
        score = sum(1 for word in query_words if word in token_set)
        if score > 0:
            scored_chunks.append((score, index, chunk))

    scored_chunks.sort(key=lambda item: (-item[0], item[1]))

    return [chunk for _, _, chunk in scored_chunks[:top_k]]
