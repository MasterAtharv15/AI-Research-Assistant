"""Text chunking utilities.

Provides a single public function `chunk_text` which splits a long piece of
text into overlapping chunks while preserving word boundaries where possible.
"""

from __future__ import annotations

from typing import List

__all__ = ["chunk_text"]


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
	"""Split `text` into overlapping chunks.

	The function attempts to preserve word boundaries by preferring to cut
	chunks at whitespace. When a single word is longer than `chunk_size`, the
	word will be split.

	Args:
		text: The input text to chunk.
		chunk_size: Maximum number of characters per chunk (must be > 0).
		overlap: Number of characters that consecutive chunks should overlap
			by (must be >= 0 and < `chunk_size`).

	Returns:
		A list of text chunks (strings). If `text` is empty or contains only
		whitespace an empty list is returned.

	Raises:
		TypeError: If arguments are of the wrong type.
		ValueError: If `chunk_size` <= 0, or `overlap` is negative or
			greater-or-equal to `chunk_size`.
	"""
	# Validate types
	if not isinstance(text, str):
		raise TypeError("`text` must be a str")
	if not isinstance(chunk_size, int):
		raise TypeError("`chunk_size` must be an int")
	if not isinstance(overlap, int):
		raise TypeError("`overlap` must be an int")

	# Validate values
	if chunk_size <= 0:
		raise ValueError("`chunk_size` must be greater than 0")
	if overlap < 0:
		raise ValueError("`overlap` must be non-negative")
	if overlap >= chunk_size:
		raise ValueError("`overlap` must be smaller than `chunk_size`")

	# Normalize whitespace and quick exit
	import re

	normalized = re.sub(r"\s+", " ", text).strip()
	if not normalized:
		return []

	chunks: List[str] = []
	length = len(normalized)
	pos = 0

	while pos < length:
		# Tentative end position
		end = min(length, pos + chunk_size)

		# If we're not at the end and the cut would split a word, try to
		# move end backwards to the last whitespace within the window.
		if end < length and normalized[end] != " ":
			last_space = normalized.rfind(" ", pos, end)
			if last_space != -1 and last_space > pos:
				end = last_space

		chunk = normalized[pos:end].strip()
		if chunk:
			chunks.append(chunk)

		# If we've reached the end of the text, break
		if end >= length:
			break

		# Compute next start position applying the requested overlap.
		next_pos = max(pos + 1, end - overlap)

		# Ensure we don't get stuck: if next_pos <= pos then advance by at
		# least one character (this can happen for tiny chunk sizes).
		if next_pos <= pos:
			next_pos = pos + 1

		# Skip leading spaces on next_pos
		while next_pos < length and normalized[next_pos] == " ":
			next_pos += 1

		pos = next_pos

	return chunks

