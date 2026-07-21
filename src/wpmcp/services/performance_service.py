"""Performance domain: cache, optimization, cleanup, maintenance, rewrites."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


class PerformanceService(BaseDomainService):
    domain = "performance"

    def _register(self) -> None:
        reg = self.add

        async def clear_cache(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/performance/clear-cache")
            return WpResult.success(action="clear_cache", domain="performance", site=site, view=View.OPERATION, data=data, message="Cache cleared.")

        async def optimize_database(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/performance/optimize-db")
            return WpResult.success(action="optimize_database", domain="performance", site=site, view=View.OPERATION, data=data, message="Database optimized.")

        async def cleanup_database(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {k: bool(p.get(k, False)) for k in ("revisions", "autodrafts", "spam", "trash")}
            data = await c.plugin("/performance/cleanup", body=body)
            return WpResult.success(action="cleanup_database", domain="performance", site=site, view=View.OPERATION, data=data, message="Database cleaned up.")

        async def flush_rewrite_rules(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/performance/flush-rewrites")
            return WpResult.success(action="flush_rewrite_rules", domain="performance", site=site, view=View.OPERATION, data=data, message="Rewrite rules flushed.")

        async def regenerate_thumbnails(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/performance/regenerate-thumbnails", body={"media_id": p.get("media_id")})
            return WpResult.success(action="regenerate_thumbnails", domain="performance", site=site, view=View.OPERATION, data=data, message="Thumbnails regenerated.")

        async def get_performance_metrics(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/performance/metrics")
            return WpResult.success(action="get_performance_metrics", domain="performance", site=site, view=View.PERFORMANCE, data=data)

        async def enable_maintenance_mode(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/performance/maintenance", body={"enabled": bool(p.get("enabled", True))})
            return WpResult.success(action="enable_maintenance_mode", domain="performance", site=site, view=View.OPERATION, data=data, message="Maintenance mode toggled.")

        async def get_system_info(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/security/system-info")
            return WpResult.success(action="get_system_info", domain="performance", site=site, view=View.PERFORMANCE, data=data)

        reg("clear_cache", "Clear object cache and transients.", clear_cache, read_only=False)
        reg("optimize_database", "Optimize all database tables.", optimize_database, read_only=False)
        reg("cleanup_database", "Remove revisions, spam, trash, auto-drafts.", cleanup_database, params={"revisions": "bool?", "autodrafts": "bool?", "spam": "bool?", "trash": "bool?"}, destructive=True, read_only=False)
        reg("flush_rewrite_rules", "Flush WordPress rewrite rules.", flush_rewrite_rules, read_only=False)
        reg("regenerate_thumbnails", "Regenerate image thumbnails.", regenerate_thumbnails, params={"media_id": "int?"}, read_only=False)
        reg("get_performance_metrics", "Get performance metrics.", get_performance_metrics)
        reg("enable_maintenance_mode", "Toggle maintenance mode.", enable_maintenance_mode, params={"enabled": "bool"}, read_only=False)
        reg("get_system_info", "Get system information.", get_system_info)
