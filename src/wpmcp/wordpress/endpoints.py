"""Canonical WordPress REST endpoint paths.

Two namespaces are used:
- ``wp/v2`` — the core WordPress REST API (posts, pages, media, users, etc.).
- ``wpmcp/v1`` — the companion plugin's extended endpoints (files, database,
  cron, shortcodes, security, performance, themes, plugins, menus, blocks,
  woocommerce, seo, backup, roles).
"""

from __future__ import annotations

# Core WordPress REST API (always available).
WP_V2 = "/wp-json/wp/v2"

# Companion plugin REST namespace.
WPMCP_V1 = "/wp-json/wpmcp/v1"


def wp_v2(path: str = "") -> str:
    """Build a core WP REST path."""

    return f"{WP_V2}{path}"


def wpmcp_v1(path: str = "") -> str:
    """Build a companion-plugin REST path."""

    return f"{WPMCP_V1}{path}"
