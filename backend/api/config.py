"""Settings read from the environment, and paths inside backend/."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import httpx

VERSION = "1.4.0"
# backend/ — the Python project root (contains pyproject.toml, knowledge/, data/).
BACKEND_DIR = Path(__file__).resolve().parents[1]


def database_url() -> str:
    return os.getenv("DATABASE_URL", "")


def backup_directory() -> Path:
    value = os.getenv("HAEDAP_BACKUP_DIR")
    return Path(value).resolve() if value else BACKEND_DIR / "data/backups"


def allowed_hosts() -> set[str]:
    hosts = {"127.0.0.1", "localhost"}
    hosts.update(item.strip().lower() for item in os.getenv("HAEDAP_ALLOWED_HOSTS", "").split(",") if item.strip())
    return hosts


@dataclass(frozen=True)
class LLMSettings:
    base_url: str
    model: str
    api_key: str = field(repr=False)
    response_format: str = "text"


def llm_settings() -> LLMSettings | None:
    """Resolve the same settings for health and generation; never contact a model here."""
    base = (os.getenv("OPENAI_BASE_URL") or "").strip() or "https://api.openai.com/v1"
    model = (os.getenv("OPENAI_MODEL") or "").strip()
    key = (os.getenv("OPENAI_API_KEY") or "").strip()
    output_format = (os.getenv("OPENAI_RESPONSE_FORMAT") or "").strip() or "text"
    if not model or output_format not in {"text", "json_object", "json_schema"}:
        return None
    if any(character.isspace() for character in base) or "?" in base or "#" in base:
        return None
    try:
        url = httpx.URL(base)
        if url.scheme not in {"http", "https"} or not url.host or url.userinfo:
            return None
        if url.host == "api.openai.com" and not key:
            return None
    except (httpx.InvalidURL, ValueError):
        return None
    return LLMSettings(str(url).rstrip("/"), model, key, output_format)


def llm_configured() -> bool:
    return llm_settings() is not None
