"""Environment-backed server and multisite configuration."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="WPMCP_", extra="ignore")

    host: str = "127.0.0.1"
    port: int = Field(default=8787, ge=1, le=65535)
    transport: Literal["stdio", "http", "sse", "streamable-http"] = "http"
    server_name: str = "WPMCP — Remote WordPress MCP"
    bearer_token: str | None = None
    default_site: str = "primary"
    allow_destructive: bool = False
    audit_log_path: str = "wpmcp-audit.log"

    @field_validator("default_site")
    @classmethod
    def _normalize_default_site(cls, value: str) -> str:
        return value.strip().lower()


@lru_cache
def get_server_settings() -> ServerSettings:
    """Return the cached, validated server settings."""

    return ServerSettings()
