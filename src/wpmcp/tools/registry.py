"""Compose every WPMCP tool, resource, prompt, and UI surface onto the server."""

from __future__ import annotations

from fastmcp import FastMCP

from wpmcp.prompts.workflow_prompts import register_workflow_prompts
from wpmcp.resources.catalog import register_catalog_resources
from wpmcp.tools.gateway_tools import register_gateway_tools
from wpmcp.wordpress.multisite import SiteRegistry


def _build_services(registry: SiteRegistry) -> dict[str, object]:
    from wpmcp.services.appearance_service import AppearanceService
    from wpmcp.services.backup_service import BackupService
    from wpmcp.services.blocks_service import BlocksService
    from wpmcp.services.cli_service import CliService
    from wpmcp.services.content_service import ContentService
    from wpmcp.services.database_service import DatabaseService
    from wpmcp.services.file_service import FileService
    from wpmcp.services.maintenance_service import MaintenanceService
    from wpmcp.services.menu_service import MenuService
    from wpmcp.services.performance_service import PerformanceService
    from wpmcp.services.plugin_service import PluginService
    from wpmcp.services.seo_service import SeoService
    from wpmcp.services.security_service import SecurityService
    from wpmcp.services.sites_service import SitesService
    from wpmcp.services.taxonomy_service import TaxonomyService
    from wpmcp.services.users_service import UsersService
    from wpmcp.services.woocommerce_service import WooCommerceService

    return {
        "content": ContentService(registry),
        "users": UsersService(registry),
        "appearance": AppearanceService(registry),
        "plugins": PluginService(registry),
        "menus": MenuService(registry),
        "taxonomy": TaxonomyService(registry),
        "files": FileService(registry),
        "database": DatabaseService(registry),
        "woocommerce": WooCommerceService(registry),
        "blocks": BlocksService(registry),
        "seo": SeoService(registry),
        "security": SecurityService(registry),
        "performance": PerformanceService(registry),
        "backup": BackupService(registry),
        "maintenance": MaintenanceService(registry),
        "sites": SitesService(registry),
        "cli": CliService(registry),
    }


def register_all_tools(mcp: FastMCP, registry: SiteRegistry) -> None:
    """Register services, gateway tools, resources, and prompts."""

    services = _build_services(registry)
    register_gateway_tools(mcp, services, registry)
    register_catalog_resources(mcp, registry, services)
    register_workflow_prompts(mcp)
