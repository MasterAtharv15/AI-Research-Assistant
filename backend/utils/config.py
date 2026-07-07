"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pathlib import Path

from dotenv import dotenv_values
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

__all__ = ["Settings", "settings"]


class Settings(BaseSettings):
    """Application settings loaded from environment variables and a .env file."""

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    OLLAMA_BASE_URL: str = Field(..., description="Base URL for the Ollama API")
    MODEL_NAME: str = Field(..., description="Model name to use for generation")
    STORAGE_DIR: str = Field(..., description="Directory for persisted chunk data")
    UPLOAD_DIR: str = Field(..., description="Directory for uploaded files")


_env_values = dotenv_values(_ENV_FILE) if _ENV_FILE.exists() else {}

for key, value in _env_values.items():
    if value is not None:
        import os

        os.environ.setdefault(key, value)

settings = Settings(
    OLLAMA_BASE_URL=_env_values.get("OLLAMA_BASE_URL", ""),
    MODEL_NAME=_env_values.get("MODEL_NAME", ""),
    STORAGE_DIR=_env_values.get("STORAGE_DIR", ""),
    UPLOAD_DIR=_env_values.get("UPLOAD_DIR", ""),
)
