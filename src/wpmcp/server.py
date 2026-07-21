"""FastMCP server composition and executable entry point."""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier

from wpmcp.core.config import get_server_settings
from wpmcp.tools.registry import register_all_tools
from wpmcp.wordpress.multisite import get_site_registry


def create_mcp_server() -> FastMCP:
    """Build the remote WPMCP server with optional bearer authentication."""

    settings = get_server_settings()
    auth = None
    if settings.bearer_token:
        auth = StaticTokenVerifier(
            tokens={
                settings.bearer_token: {
                    "client_id": "wpmcp-client",
                    "scopes": ["wordpress:read", "wordpress:write"],
                }
            },
            required_scopes=["wordpress:read"],
        )

    server = FastMCP(
        name=settings.server_name,
        instructions=(
            "WPMCP gives the model complete, multisite control of WordPress through 17 "
            "namespaced gateway tools (wp_content, wp_appearance, wp_plugins, wp_files, "
            "wp_database, wp_woocommerce, wp_blocks, wp_seo, wp_security, wp_performance, "
            "wp_backup, wp_maintenance, wp_menus, wp_taxonomy, wp_users, wp_sites, wp_discover). "
            "Every gateway tool takes `action`, optional `site`, and `params`. Call wp_discover "
            "first to learn every available action and its parameters. Destructive actions are "
            "flagged in the catalog — confirm with the user before running them. Every result "
            "renders in the interactive WPMCP console."
        ),
        auth=auth,
    )

    register_all_tools(server, get_site_registry())
    return server


mcp = create_mcp_server()


def main() -> None:
    """Run the remote Streamable HTTP MCP server."""

    settings = get_server_settings()
    mcp.run(transport=settings.transport, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
