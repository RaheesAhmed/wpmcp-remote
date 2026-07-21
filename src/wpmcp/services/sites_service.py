"""Sites domain: multisite management and per-site introspection."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


class SitesService(BaseDomainService):
    domain = "sites"

    def __init__(self, registry) -> None:
        super().__init__(registry)

    def _register(self) -> None:
        reg = self.add

        async def list_sites(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = self.registry.describe()
            return WpResult.success(action="list_sites", domain="sites", site=site, view=View.SITES, data=data, meta={"count": len(data), "default": self.registry.default_alias})

        async def test_connection(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            info = await c.test_connection()
            return WpResult.success(action="test_connection", domain="sites", site=site, view=View.SITE_INFO, data=info)

        async def get_site_info(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core("")
            return WpResult.success(action="get_site_info", domain="sites", site=site, view=View.SITE_INFO, data=data)

        async def list_network_sites(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/sites/list")
            return WpResult.success(action="list_network_sites", domain="sites", site=site, view=View.SITES, data=data.get("sites", data), meta={"count": data.get("total") if isinstance(data, dict) else None})

        async def create_network_site(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {"domain": p.get("domain", ""), "title": p.get("title", ""), "email": p.get("email", "")}
            data = await c.plugin("/sites/create", body=body)
            return WpResult.success(action="create_network_site", domain="sites", site=site, view=View.OPERATION, data=data, message="Network site created.")

        async def delete_network_site(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/sites/delete", body={"id": p.get("id")})
            return WpResult.success(action="delete_network_site", domain="sites", site=site, view=View.OPERATION, data=data, message="Network site deleted.")

        reg("list_sites", "List registered WPMCP site connections.", list_sites)
        reg("test_connection", "Test the connection to the current site.", test_connection)
        reg("get_site_info", "Get core site info for the current site.", get_site_info)
        reg("list_network_sites", "List sites in a WordPress multisite network.", list_network_sites)
        reg("create_network_site", "Create a site in a multisite network.", create_network_site, params={"domain": "str", "title": "str", "email": "str"}, read_only=False)
        reg("delete_network_site", "Delete a site from a multisite network.", delete_network_site, params={"id": "int"}, destructive=True, read_only=False)
