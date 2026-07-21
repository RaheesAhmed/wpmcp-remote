"""Maintenance domain: shortcodes, cron, widgets, settings, advanced media."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


class MaintenanceService(BaseDomainService):
    domain = "maintenance"

    def _register(self) -> None:
        reg = self.add

        async def list_shortcodes(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/shortcodes/list")
            return WpResult.success(action="list_shortcodes", domain="maintenance", site=site, view=View.SHORTCODES, data=data.get("shortcodes", data), meta={"count": data.get("total") if isinstance(data, dict) else None})

        async def execute_shortcode(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/shortcodes/execute", body={"content": p.get("content", "")})
            return WpResult.success(action="execute_shortcode", domain="maintenance", site=site, view=View.OPERATION, data=data)

        async def list_cron_jobs(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/cron/list")
            return WpResult.success(action="list_cron_jobs", domain="maintenance", site=site, view=View.CRON, data=data.get("jobs", data), meta={"count": data.get("total") if isinstance(data, dict) else None})

        async def schedule_event(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {"hook": p.get("hook", ""), "recurrence": p.get("recurrence", "once"), "args": p.get("args", [])}
            if p.get("timestamp"):
                body["timestamp"] = p["timestamp"]
            data = await c.plugin("/cron/schedule", body=body)
            return WpResult.success(action="schedule_event", domain="maintenance", site=site, view=View.OPERATION, data=data, message="Cron event scheduled.")

        async def unschedule_event(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/cron/unschedule", body={"hook": p.get("hook", ""), "args": p.get("args", [])})
            return WpResult.success(action="unschedule_event", domain="maintenance", site=site, view=View.OPERATION, data=data, message="Cron event unscheduled.")

        async def run_cron(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/cron/run")
            return WpResult.success(action="run_cron", domain="maintenance", site=site, view=View.OPERATION, data=data, message="Cron triggered.")

        async def get_sidebars(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/widgets/sidebars")
            return WpResult.success(action="get_sidebars", domain="maintenance", site=site, view=View.WIDGETS, data=data.get("sidebars", data))

        async def get_widgets(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/widgets", params={"sidebar": p.get("sidebar")} if p.get("sidebar") else None)
            return WpResult.success(action="get_widgets", domain="maintenance", site=site, view=View.WIDGETS, data=data.get("widgets", data))

        async def get_settings(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/settings")
            return WpResult.success(action="get_settings", domain="maintenance", site=site, view=View.SETTINGS, data=data)

        async def update_settings(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/settings", body={"settings": p.get("settings", {})})
            return WpResult.success(action="update_settings", domain="maintenance", site=site, view=View.OPERATION, data=data, message="Settings updated.")

        async def get_unused_media(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/media/unused")
            return WpResult.success(action="get_unused_media", domain="maintenance", site=site, view=View.MEDIA, data=data.get("media", data), meta={"count": data.get("total") if isinstance(data, dict) else None})

        async def get_media_analytics(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/media/analytics")
            return WpResult.success(action="get_media_analytics", domain="maintenance", site=site, view=View.MEDIA, data=data)

        reg("list_shortcodes", "List registered shortcodes.", list_shortcodes)
        reg("execute_shortcode", "Execute a shortcode string.", execute_shortcode, params={"content": "str"}, read_only=False)
        reg("list_cron_jobs", "List scheduled cron jobs.", list_cron_jobs)
        reg("schedule_event", "Schedule a cron event.", schedule_event, params={"hook": "str", "recurrence": "str?", "timestamp": "str?"}, read_only=False)
        reg("unschedule_event", "Unschedule a cron event.", unschedule_event, params={"hook": "str", "args": "list?"}, read_only=False)
        reg("run_cron", "Manually trigger WordPress cron.", run_cron, read_only=False)
        reg("get_sidebars", "List widget areas.", get_sidebars)
        reg("get_widgets", "List widgets, optionally in a sidebar.", get_widgets, params={"sidebar": "str?"})
        reg("get_settings", "Get site settings.", get_settings)
        reg("update_settings", "Update site settings.", update_settings, params={"settings": "object"}, read_only=False)
        reg("get_unused_media", "Find unused media items.", get_unused_media)
        reg("get_media_analytics", "Get media storage analytics.", get_media_analytics)
