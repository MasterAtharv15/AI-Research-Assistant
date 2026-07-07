"""In-memory chat memory service for storing conversation history."""

from __future__ import annotations

from threading import Lock
from typing import Any, Final

__all__ = [
    "create_session",
    "add_message",
    "get_history",
    "clear_session",
]

_Message = dict[str, str]

_sessions: dict[str, list[_Message]] = {}
_lock: Final[Lock] = Lock()


def _validate_session_id(session_id: str) -> None:
    """Validate a session identifier."""
    if not isinstance(session_id, str):
        raise TypeError("`session_id` must be a string")
    if not session_id.strip():
        raise ValueError("`session_id` must not be empty")


def _validate_role(role: str) -> None:
    """Validate a chat role."""
    if not isinstance(role, str):
        raise TypeError("`role` must be a string")
    if role not in {"user", "assistant"}:
        raise ValueError("`role` must be either 'user' or 'assistant'")


def _validate_content(content: str) -> None:
    """Validate message content."""
    if not isinstance(content, str):
        raise TypeError("`content` must be a string")
    if not content.strip():
        raise ValueError("`content` must not be empty")


def create_session(session_id: str) -> None:
    """Create a new conversation session if one does not already exist.

    Args:
        session_id: The unique identifier for the session.

    Raises:
        TypeError: If ``session_id`` is not a string.
        ValueError: If ``session_id`` is empty.
    """
    _validate_session_id(session_id)
    with _lock:
        _sessions.setdefault(session_id, [])


def add_message(session_id: str, role: str, content: str) -> None:
    """Append a message to an existing conversation session.

    Args:
        session_id: The session identifier.
        role: The message role, either ``user`` or ``assistant``.
        content: The message content.

    Raises:
        TypeError: If the inputs are not strings.
        ValueError: If the session identifier is empty, the role is invalid, or the content is empty.
        KeyError: If the session does not exist.
    """
    _validate_session_id(session_id)
    _validate_role(role)
    _validate_content(content)

    with _lock:
        if session_id not in _sessions:
            raise KeyError(f"Session '{session_id}' does not exist")
        _sessions[session_id].append({"role": role, "content": content})


def get_history(session_id: str) -> list[dict[str, str]]:
    """Return the message history for a session.

    Args:
        session_id: The session identifier.

    Returns:
        A shallow copy of the session's message history.

    Raises:
        TypeError: If ``session_id`` is not a string.
        ValueError: If ``session_id`` is empty.
        KeyError: If the session does not exist.
    """
    _validate_session_id(session_id)
    with _lock:
        if session_id not in _sessions:
            raise KeyError(f"Session '{session_id}' does not exist")
        return [{"role": message["role"], "content": message["content"]} for message in _sessions[session_id]]


def clear_session(session_id: str) -> None:
    """Remove all messages from a session.

    Args:
        session_id: The session identifier.

    Raises:
        TypeError: If ``session_id`` is not a string.
        ValueError: If ``session_id`` is empty.
        KeyError: If the session does not exist.
    """
    _validate_session_id(session_id)
    with _lock:
        if session_id not in _sessions:
            raise KeyError(f"Session '{session_id}' does not exist")
        _sessions[session_id].clear()
