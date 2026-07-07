"""Embedding utilities backed by sentence-transformers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

__all__ = [
    "generate_embedding",
    "generate_embeddings",
]

_MODEL_NAME: Final[str] = "all-MiniLM-L6-v2"
_model: "SentenceTransformer | None" = None


def _get_model() -> "SentenceTransformer":
    """Load and cache the sentence-transformer model once."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise ImportError("sentence-transformers is required to generate embeddings") from exc

        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def generate_embedding(text: str) -> list[float]:
    """Generate a single embedding for the supplied text.

    Args:
        text: The input text to embed.

    Returns:
        A list of floating-point values representing the embedding.

    Raises:
        TypeError: If ``text`` is not a string.
        ValueError: If ``text`` is empty or whitespace-only.
    """
    if not isinstance(text, str):
        raise TypeError("`text` must be a string")
    if not text.strip():
        raise ValueError("`text` must not be empty")

    return _get_model().encode(text, convert_to_numpy=False).tolist()


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings for a list of input texts.

    Args:
        texts: The input texts to embed.

    Returns:
        A list of embeddings, one per input text.

    Raises:
        TypeError: If ``texts`` is not a list of strings.
        ValueError: If ``texts`` is empty or contains empty entries.
    """
    if not isinstance(texts, list):
        raise TypeError("`texts` must be a list of strings")
    if not texts:
        raise ValueError("`texts` must not be empty")
    if any(not isinstance(text, str) for text in texts):
        raise TypeError("All items in `texts` must be strings")
    if any(not text.strip() for text in texts):
        raise ValueError("All items in `texts` must be non-empty")

    return _get_model().encode(texts, convert_to_numpy=False).tolist()
