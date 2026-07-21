"""Register the 17 dispatch (gateway) tools plus ``wp_discover``.

Each gateway tool wraps one domain service's ``dispatch``. The tool surface
exposes only ``action``, optional ``site``, and ``params`` — collapsing the
legacy 190 tools into 17 namespaced gateways so the model's context window
stays small. ``wp_discover`` returns the full action catalog.
"""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError

from wpmcp.core.exceptions import WpMcpError
from wpmcp.domain.models import DomainCatalog, WpResult
from wpmcp.tools.annotations import GATEWAY_TOOL, READ_ONLY_TOOL
from wpmcp.tools.app_config import WP_APP_CONFIG
from wpmcp.wordpress.multisite import SiteRegistry

_SERVICES: dict[str, tuple[str, str, str]] = {
    # domain: (tool_name, title, description)
    "content": ("wp_content", "WordPress content", "Posts, pages, media, comments, categories, tags."),
    "users": ("wp_users", "WordPress users", "Users, roles, and capabilities."),
    "appearance": ("wp_appearance", "WordPress appearance", "Themes, theme.json, templates, child themes, global styles."),
    "plugins": ("wp_plugins", "WordPress plugins", "Activate, deactivate, delete, and edit plugin files."),
    "menus": ("wp_menus", "WordPress menus", "Menus, menu items, and menu locations."),
    "taxonomy": ("wp_taxonomy", "WordPress taxonomy", "Post types, taxonomies, and terms."),
    "files": ("wp_files", "WordPress files", "Read, write, copy, move, delete, list files (allowed dirs only)."),
    "database": ("wp_database", "WordPress database", "Tables, SELECT-only queries, options, structure, preview."),
    "woocommerce": ("wp_woocommerce", "WooCommerce", "Products, orders, customers, coupons, reports, shipping."),
    "blocks": ("wp_blocks", "Gutenberg blocks", "Block types, patterns, reusable blocks, templates, style variations."),
    "seo": ("wp_seo", "WordPress SEO", "Sitemaps, robots, redirects, OG/Twitter, schema, analysis."),
    "security": ("wp_security", "WordPress security", "Site health, updates, debug log, core integrity, permissions."),
    "performance": ("wp_performance", "WordPress performance", "Cache, optimization, cleanup, maintenance, rewrites."),
    "backup": ("wp_backup", "Backup & migration", "Full/db/files backup, restore, export/import, clone, schedule."),
    "maintenance": ("wp_maintenance", "WordPress maintenance", "Shortcodes, cron, widgets, settings, advanced media."),
    "sites": ("wp_sites", "WordPress sites", "Multisite connections and network site management."),
    "cli": ("wp_cli", "WP-CLI", "Run whitelisted WP-CLI commands — install/update core, plugins, themes."),
}


def register_gateway_tools(mcp: FastMCP, services: dict[str, Any], registry: SiteRegistry) -> None:
    """Register one dispatch tool per domain, all sharing the generative UI."""

    for domain, (tool_name, title, description) in _SERVICES.items():
        service = services[domain]
        _register_one(mcp, tool_name, title, description, domain, service)

    @mcp.tool(
        title="WordPress discovery",
        description=(
            "Return the catalog of every WPMCP gateway tool and its actions. "
            "Call this first to learn available actions before dispatching."
        ),
        annotations=READ_ONLY_TOOL,
        app=WP_APP_CONFIG,
    )
    async def wp_discover(site: str | None = None) -> list[DomainCatalog]:
        """List every gateway tool and the actions it supports."""

        catalog: list[DomainCatalog] = []
        for domain, (tool_name, title, description) in _SERVICES.items():
            catalog.append(
                DomainCatalog(
                    tool=tool_name,
                    domain=domain,
                    title=title,
                    description=description,
                    actions=services[domain].catalog(),
                )
            )
        return catalog


def _register_one(
    mcp: FastMCP,
    tool_name: str,
    title: str,
    description: str,
    domain: str,
    service: Any,
) -> None:
    """Register a single dispatch tool bound to ``service``."""

    @mcp.tool(
        name=tool_name,
        title=title,
        description=description,
        annotations=GATEWAY_TOOL,
        app=WP_APP_CONFIG,
    )
    async def gateway(
        action: str,
        site: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> WpResult:
        """Dispatch ``action`` against the ``domain`` service.

        Args:
            action: One of the actions listed by ``wp_discover``.
            site: Optional multisite alias; defaults to the configured default.
            params: Action-specific parameters (see the catalog).
        """

        try:
            return await service.dispatch(action, site, params or {})
        except WpMcpError as error:
            return WpResult.failure(
                action=action,
                domain=domain,
                site=registry.resolve(site),
                message=str(error),
            )
        except Exception as error:  # noqa: BLE001 - surface any WP failure to the model
            raise ToolError(f"{domain}/{action} failed: {error}") from error
