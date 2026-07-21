"""Append-only audit log for sensitive operations (e.g. WP-CLI runs)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from anyio import Path as AsyncPath

from wpmcp.core.config import get_server_settings


async def append_audit(entry: dict[str, Any]) -> None:
    """Append one JSON-line audit record to the configured audit log file."""

    settings = get_server_settings()
    path = AsyncPath(settings.audit_log_path)
    record = {"timestamp": datetime.now(timezone.utc).isoformat(), **entry}
    line = json.dumps(record, default=str, separators=(",", ":")) + "\n"
    await path.parent.mkdir(parents=True, exist_ok=True)
    async with await path.open("a", encoding="utf-8") as handle:
        await handle.write(line)


def audit_log_path() -> Path:
    """Return the resolved audit log path (sync, for surfacing to clients)."""

    return Path(get_server_settings().audit_log_path).resolve()
