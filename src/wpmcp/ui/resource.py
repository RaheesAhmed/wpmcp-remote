"""Register the WPMCP generative UI as an MCP Apps resource."""

from __future__ import annotations

import asyncio
from importlib.resources import files

from fastmcp import FastMCP
from fastmcp.apps import AppConfig, ResourceCSP

from wpmcp.tools.app_config import WP_APP_URI

_MCP_APPS_CDN_ORIGIN = "https://unpkg.com"


async def _read_asset(asset_name: str) -> str:
    """Read a packaged UI asset without blocking the event loop."""

    asset = files("wpmcp.ui.assets").joinpath(asset_name)
    return await asyncio.to_thread(asset.read_text, encoding="utf-8")


def register_wp_ui_resource(mcp: FastMCP) -> None:
    """Register the self-contained WPMCP console application."""

    @mcp.resource(
        WP_APP_URI,
        name="WPMCP console",
        description="Premium interactive UI for every WPMCP tool result.",
        app=AppConfig(
            prefers_border=False,
            csp=ResourceCSP(resource_domains=[_MCP_APPS_CDN_ORIGIN]),
        ),
    )
    async def get_wp_console() -> str:
        """Return the self-contained WPMCP console application."""

        template, base_styles, panel_styles, state_styles, core_script, render_script, action_script = await asyncio.gather(
            _read_asset("console.html"),
            _read_asset("console.css"),
            _read_asset("panels.css"),
            _read_asset("states.css"),
            _read_asset("console.js"),
            _read_asset("renderers.js"),
            _read_asset("actions.js"),
        )
        styles = "\n".join((base_styles, panel_styles, state_styles))
        script = "\n".join((core_script, render_script, action_script))
        return template.replace("__WPMCP_STYLES__", styles).replace("__WPMCP_SCRIPT__", script)
