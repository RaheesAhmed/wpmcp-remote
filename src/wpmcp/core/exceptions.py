"""Domain-specific exception hierarchy."""

from __future__ import annotations


class WpMcpError(Exception):
    """Base error for all WPMCP failures."""


class SiteNotRegisteredError(WpMcpError):
    """Raised when a requested multisite alias is not configured."""

    def __init__(self, alias: str) -> None:
        super().__init__(f"WordPress site '{alias}' is not registered.")
        self.alias = alias


class WordPressApiError(WpMcpError):
    """Raised when the WordPress REST API returns an error response."""

    def __init__(self, message: str, status_code: int = 0, endpoint: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint


class UnknownActionError(WpMcpError):
    """Raised when a dispatch tool receives an action it does not support."""

    def __init__(self, action: str, domain: str, available: list[str]) -> None:
        super().__init__(
            f"Unknown action '{action}' for domain '{domain}'. "
            f"Call wp_discover for the catalog. Available: {', '.join(available)}."
        )
        self.action = action
        self.domain = domain


class ValidationError(WpMcpError):
    """Raised when action parameters fail validation."""


class SecurityError(WpMcpError):
    """Raised when an operation is blocked by safety policy."""
