"""Centralized logging configuration for the FastAPI application.

This module creates a single logger instance named ``ai_research_assistant``
that writes informational messages to both the console and a rotating file log
located under the project's ``logs`` directory.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Final


PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
LOGS_DIR: Final[Path] = PROJECT_ROOT / "logs"
LOG_FILE: Final[Path] = LOGS_DIR / "app.log"


def _configure_logger() -> logging.Logger:
    """Create and configure the shared application logger."""
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    logger_instance: logging.Logger = logging.getLogger("ai_research_assistant")
    logger_instance.setLevel(logging.INFO)
    logger_instance.propagate = False

    if logger_instance.handlers:
        return logger_instance

    formatter: logging.Formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    logger_instance.addHandler(console_handler)
    logger_instance.addHandler(file_handler)

    return logger_instance


logger: logging.Logger = _configure_logger()

__all__ = ["logger"]
