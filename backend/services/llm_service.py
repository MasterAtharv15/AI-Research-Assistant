"""Ollama-backed LLM utilities for answer generation."""

from __future__ import annotations

from typing import Any, Final

import requests

__all__ = ["generate_answer"]

_OLLAMA_URL: Final[str] = "http://localhost:11434/api/generate"


def generate_answer(
    query: str,
    context_chunks: list[str],
    history: list[dict[str, str]] | None = None,
) -> str:
    """Generate an answer from the supplied context using the Ollama API.

    Args:
        query: The user's question.
        context_chunks: The relevant context chunks to use as evidence.
        history: Optional prior conversation history to include.

    Returns:
        The generated answer text returned by Ollama.

    Raises:
        TypeError: If ``query`` is not a string or ``context_chunks`` is not a list of strings.
        ValueError: If ``query`` is empty or whitespace-only.
        RuntimeError: If the Ollama request fails or returns an invalid response.
    """
    if not isinstance(query, str):
        raise TypeError("`query` must be a string")
    if not isinstance(context_chunks, list):
        raise TypeError("`context_chunks` must be a list of strings")
    if any(not isinstance(chunk, str) for chunk in context_chunks):
        raise TypeError("All items in `context_chunks` must be strings")
    if not query.strip():
        raise ValueError("`query` must not be empty")

    context_text = "\n\n".join(chunk.strip() for chunk in context_chunks if chunk.strip())
    history_text = ""
    if history:
        history_lines = [f"{item['role']}: {item['content']}" for item in history]
        history_text = "Conversation history:\n" + "\n".join(history_lines) + "\n\n"

    prompt = (
        "You are a helpful research assistant.\n\n"
        "Answer ONLY using the provided context.\n\n"
        "If the answer is not contained in the context, say you don't know.\n\n"
        f"{history_text}"
        f"Context:\n{context_text}\n\n"
        f"Question:\n{query}\n\n"
        "Answer:"
    )

    payload: dict[str, Any] = {"model": "llama3.1:8b", "prompt": prompt, "stream": False}

    try:
        response = requests.post(_OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Failed to reach Ollama: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise RuntimeError("Ollama returned an invalid JSON response") from exc

    if not isinstance(data, dict) or "response" not in data or not isinstance(data["response"], str):
        raise RuntimeError("Ollama returned an invalid response payload")

    return data["response"].strip()
