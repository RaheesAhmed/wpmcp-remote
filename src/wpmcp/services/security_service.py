"""Security domain: site health, updates, debug log, core integrity, permissions."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


class SecurityService(BaseDomainService):
    domain = "security"

    def _register(self) -> None:
        reg = self.add

        async def get_site_health(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/security/site-health")
            return WpResult.success(action="get_site_health", domain="security", site=site, view=View.SECURITY, data=data)

        async def check_updates(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/security/check-updates")
            return WpResult.success(action="check_updates", domain="security", site=site, view=View.UPDATES, data=data, meta={"total_updates": data.get("totalUpdates") if isinstance(data, dict) else None})

        async def get_debug_log(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/security/debug-log")
            return WpResult.success(action="get_debug_log", domain="security", site=site, view=View.DEBUG_LOG, data=data)

        async def verify_core_files(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/security/verify-core")
            return WpResult.success(action="verify_core_files", domain="security", site=site, view=View.SECURITY, data=data)

        async def get_system_info(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/security/system-info")
            return WpResult.success(action="get_system_info", domain="security", site=site, view=View.SECURITY, data=data)

        async def scan_permissions(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/security/scan-permissions")
            return WpResult.success(action="scan_permissions", domain="security", site=site, view=View.SECURITY, data=data)

        async def get_failed_logins(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/security/failed-logins")
            return WpResult.success(action="get_failed_logins", domain="security", site=site, view=View.SECURITY, data=data)

        async def get_version_info(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/security/version-info")
            return WpResult.success(action="get_version_info", domain="security", site=site, view=View.SECURITY, data=data)

        reg("get_site_health", "Get site health status.", get_site_health)
        reg("check_updates", "Check for core/plugin/theme updates.", check_updates)
        reg("get_debug_log", "Read the WordPress debug.log.", get_debug_log)
        reg("verify_core_files", "Verify WordPress core file checksums.", verify_core_files)
        reg("get_system_info", "Get system information.", get_system_info)
        reg("scan_permissions", "Scan file permissions.", scan_permissions)
        reg("get_failed_logins", "Get recent failed login attempts.", get_failed_logins)
        reg("get_version_info", "Get version information.", get_version_info)
