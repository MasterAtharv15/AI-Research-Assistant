"""Answer generation utilities."""

from __future__ import annotations

from typing import List

__all__ = ["generate_answer"]


def generate_answer(query: str, matching_chunks: List[str]) -> str:
    """Generate a simple answer from matching document chunks.

    If no relevant chunks are available, return a polite fallback message.
    Otherwise the answer concatenates the matching chunks into a readable
    response prefixed with a summary sentence.

    Args:
        query: The user's query string.
        matching_chunks: A list of relevant text chunks returned by search.

    Returns:
        A generated answer string.

    Raises:
        TypeError: If argument types are invalid.
    """
    if not isinstance(query, str):
        raise TypeError("`query` must be a string")
    if not isinstance(matching_chunks, list):
        raise TypeError("`matching_chunks` must be a list of strings")
    if any(not isinstance(chunk, str) for chunk in matching_chunks):
        raise TypeError("All items in `matching_chunks` must be strings")

    if not matching_chunks:
        return "I couldn't find relevant information in the uploaded document."

    answer_body = "\n\n".join(chunk.strip() for chunk in matching_chunks if chunk.strip())
    if not answer_body:
        return "I couldn't find relevant information in the uploaded document."

    return f"Based on the uploaded document:\n\n{answer_body}"
