"""Catalog resources: capabilities, action catalog, and registered sites."""

from __future__ import annotations

from typing import Any

from fastmcp import FastMCP

from wpmcp.wordpress.multisite import SiteRegistry

RESOURCE_ANNOTATIONS = {"readOnlyHint": True, "idempotentHint": True}


def register_catalog_resources(mcp: FastMCP, registry: SiteRegistry, services: dict[str, Any]) -> None:
    """Expose stable, read-only context for MCP clients."""

    @mcp.resource(
        "wp://capabilities",
        name="WPMCP capabilities",
        description="What WPMCP can do, how it dispatches, and its safety model.",
        annotations=RESOURCE_ANNOTATIONS,
    )
    def get_capabilities() -> dict[str, object]:
        return {
            "version": "1.0.0",
            "transport": "streamable-http",
            "model": "namespaced dispatch — 17 gateway tools, 190 actions",
            "multisite": True,
            "generative_ui": "ui://wpmcp/console-v1.html",
            "safety": [
                "WordPress Application Passwords per site",
                "filesystem paths restricted to themes/plugins/uploads/mu-plugins",
                "SQL restricted to SELECT/SHOW/DESCRIBE/EXPLAIN",
                "destructive actions flagged in the catalog",
            ],
        }

    @mcp.resource(
        "wp://action-catalog",
        name="WPMCP action catalog",
        description="Every gateway tool and the actions it accepts.",
        annotations=RESOURCE_ANNOTATIONS,
    )
    def get_action_catalog() -> list[dict[str, object]]:
        catalog: list[dict[str, object]] = []
        for domain, service in services.items():
            catalog.append(
                {
                    "domain": domain,
                    "actions": [a.model_dump(mode="json") for a in service.catalog()],
                }
            )
        return catalog

    @mcp.resource(
        "wp://sites",
        name="Registered WordPress sites",
        description="Multisite connections known to this WPMCP server.",
        annotations=RESOURCE_ANNOTATIONS,
    )
    def get_sites() -> dict[str, object]:
        return {
            "default": registry.default_alias,
            "sites": registry.describe(),
        }
