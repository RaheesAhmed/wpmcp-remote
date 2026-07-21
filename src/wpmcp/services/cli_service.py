"""WP-CLI domain: run a strict allowlist of WP-CLI commands remotely.

The companion plugin exposes ``wpmcp/v1/cli/run`` which executes ``wp <command>``
in the site's WordPress root. This service enforces the allowlist and shell-
metacharacter rejection *before* forwarding the command, and writes every
attempt to an append-only audit log.
"""

from __future__ import annotations

import re
import shlex
from typing import Any

from wpmcp.core.audit import append_audit
from wpmcp.core.exceptions import SecurityError
from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient

# Two-token subcommands the AI is permitted to run. Anything else is rejected.
ALLOWED_COMMANDS: tuple[str, ...] = (
    "plugin install",
    "plugin update",
    "plugin delete",
    "plugin activate",
    "plugin deactivate",
    "theme install",
    "theme update",
    "theme delete",
    "theme activate",
    "core update",
    "core update-db",
    "core version",
    "cache flush",
    "cron event run",
    "cron event list",
    "db export",
    "db size",
    "user list",
    "option get",
    "option update",
)

# Shell metacharacters that would allow chaining/injection. WP-CLI args only.
_METACHAR_RE = re.compile(r"[;|&$`><\n\r]")


def _validate(command: str) -> str:
    """Return the validated command or raise ``SecurityError``."""

    raw = command.strip()
    if not raw:
        raise SecurityError("Command is empty.")

    if _METACHAR_RE.search(raw):
        raise SecurityError(
            "Command contains forbidden shell metacharacters. "
            "Only WP-CLI arguments are allowed; no chaining or redirection."
        )

    tokens = shlex.split(raw)
    if not tokens:
        raise SecurityError("Command is empty.")

    if len(tokens) < 2:
        raise SecurityError(
            f"Command '{tokens[0]}' is not on the allowlist. "
            f"Use wp_discover or list_allowed_commands to see permitted commands."
        )

    # An allowlist entry may be 2 tokens (e.g. "plugin install") or 3 tokens
    # (e.g. "cron event run"). A command matches when an entry's tokens are an
    # exact prefix of the command's tokens — so "cron event list" matches the
    # "cron event list" entry, but "cron event" alone does not.
    prefix_preview = " ".join(tokens[:3])
    matched = any(
        len(allowed.split()) >= 2 and tokens[: len(allowed.split())] == allowed.split()
        for allowed in ALLOWED_COMMANDS
    )
    if not matched:
        raise SecurityError(
            f"Command '{prefix_preview}' is not on the allowlist. "
            f"Permitted: {', '.join(ALLOWED_COMMANDS)}."
        )
    return raw


class CliService(BaseDomainService):
    domain = "cli"

    def _register(self) -> None:
        reg = self.add

        async def run(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            command = _validate(str(p.get("command", "")))
            await append_audit(
                {
                    "event": "wp_cli.run",
                    "site": site,
                    "command": command,
                    "status": "dispatched",
                }
            )
            try:
                data = await c.plugin("/cli/run", body={"command": command})
            except Exception as error:
                await append_audit(
                    {
                        "event": "wp_cli.run",
                        "site": site,
                        "command": command,
                        "status": "error",
                        "error": str(error),
                    }
                )
                raise
            await append_audit(
                {
                    "event": "wp_cli.run",
                    "site": site,
                    "command": command,
                    "status": "complete",
                    "exit_code": data.get("exit_code") if isinstance(data, dict) else None,
                }
            )
            return WpResult.success(
                action="run",
                domain="cli",
                site=site,
                view=View.OPERATION,
                data=data,
                message=f"Ran: wp {command}",
            )

        async def list_allowed_commands(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            return WpResult.success(
                action="list_allowed_commands",
                domain="cli",
                site=site,
                view=View.OPERATION,
                data={"allowed": list(ALLOWED_COMMANDS)},
                meta={"count": len(ALLOWED_COMMANDS)},
            )

        reg(
            "run",
            "Run a whitelisted WP-CLI command (install/update core, plugins, themes).",
            run,
            params={"command": "str"},
            destructive=True,
            read_only=False,
        )
        reg(
            "list_allowed_commands",
            "Return the WP-CLI allowlist so the model can check before running.",
            list_allowed_commands,
            params={},
            destructive=False,
            read_only=True,
        )
