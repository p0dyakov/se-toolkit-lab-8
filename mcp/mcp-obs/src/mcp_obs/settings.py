"""Runtime settings for the observability MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Settings:
    victorialogs_url: str
    victoriatraces_url: str


def _require_url(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} is not configured")
    return value.rstrip("/")


def resolve_settings() -> Settings:
    return Settings(
        victorialogs_url=_require_url("NANOBOT_VICTORIALOGS_URL"),
        victoriatraces_url=_require_url("NANOBOT_VICTORIATRACES_URL"),
    )
