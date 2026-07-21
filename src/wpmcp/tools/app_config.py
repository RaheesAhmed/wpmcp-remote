"""Shared MCP Apps metadata for every WPMCP gateway tool."""

from fastmcp.apps import AppConfig

WP_APP_URI = "ui://wpmcp/console-v1.html"
WP_APP_CONFIG = AppConfig(
    resource_uri=WP_APP_URI,
    prefers_border=False,
    visibility=["model", "app"],
)
