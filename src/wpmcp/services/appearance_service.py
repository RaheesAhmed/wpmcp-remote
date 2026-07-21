"""Appearance domain: themes, theme.json, templates, child themes, global styles."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


class AppearanceService(BaseDomainService):
    domain = "appearance"

    def _register(self) -> None:
        reg = self.add

        async def get_themes(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes")
            return WpResult.success(action="get_themes", domain="appearance", site=site, view=View.THEMES, data=data.get("themes", data), meta={"count": len(data.get("themes", data) if isinstance(data, dict) else data)})

        async def activate_theme(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes/activate", body={"stylesheet": p.get("stylesheet", "")})
            return WpResult.success(action="activate_theme", domain="appearance", site=site, view=View.OPERATION, data=data, message=f"Theme '{p.get('stylesheet')}' activated.")

        async def get_active_theme(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes/active")
            return WpResult.success(action="get_active_theme", domain="appearance", site=site, view=View.THEMES, data=data)

        async def create_child_theme(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes/child", body={"parent": p.get("parent", ""), "name": p.get("name", "")})
            return WpResult.success(action="create_child_theme", domain="appearance", site=site, view=View.OPERATION, data=data, message="Child theme created.")

        async def get_theme_json(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes/theme-json", params={"theme": p.get("theme")} if p.get("theme") else None)
            return WpResult.success(action="get_theme_json", domain="appearance", site=site, view=View.THEME_JSON, data=data)

        async def update_theme_json(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes/theme-json", body={"theme": p.get("theme", ""), "json": p.get("json", {})})
            return WpResult.success(action="update_theme_json", domain="appearance", site=site, view=View.OPERATION, data=data, message="theme.json updated.")

        async def read_theme_file(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes/file/read", body={"theme": p.get("theme", ""), "file": p.get("file", "")})
            return WpResult.success(action="read_theme_file", domain="appearance", site=site, view=View.FILE, data=data)

        async def write_theme_file(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes/file/write", body={"theme": p.get("theme", ""), "file": p.get("file", ""), "content": p.get("content", ""), "create_backup": bool(p.get("create_backup", True))})
            return WpResult.success(action="write_theme_file", domain="appearance", site=site, view=View.OPERATION, data=data, message="Theme file written.")

        async def list_theme_files(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes/files", body={"theme": p.get("theme", "")})
            return WpResult.success(action="list_theme_files", domain="appearance", site=site, view=View.FILES, data=data.get("files", data), meta={"count": len(data.get("files", [])) if isinstance(data, dict) else 0})

        async def get_templates(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes/templates", body={"theme": p.get("theme", "")})
            return WpResult.success(action="get_templates", domain="appearance", site=site, view=View.TEMPLATES, data=data.get("templates", data))

        async def get_global_styles(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes/global-styles")
            return WpResult.success(action="get_global_styles", domain="appearance", site=site, view=View.THEME_JSON, data=data)

        async def delete_theme(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/themes/delete", body={"stylesheet": p.get("stylesheet", "")})
            return WpResult.success(action="delete_theme", domain="appearance", site=site, view=View.OPERATION, data=data, message="Theme deleted.", )

        reg("get_themes", "List all installed themes.", get_themes)
        reg("activate_theme", "Activate a theme by stylesheet.", activate_theme, params={"stylesheet": "str"}, read_only=False)
        reg("get_active_theme", "Get the currently active theme.", get_active_theme)
        reg("create_child_theme", "Create a child theme.", create_child_theme, params={"parent": "str", "name": "str"}, read_only=False)
        reg("get_theme_json", "Read a block theme's theme.json.", get_theme_json, params={"theme": "str?"})
        reg("update_theme_json", "Update a theme's theme.json.", update_theme_json, params={"theme": "str", "json": "object"}, read_only=False)
        reg("read_theme_file", "Read a file from a theme.", read_theme_file, params={"theme": "str", "file": "str"})
        reg("write_theme_file", "Write a file in a theme (with backup).", write_theme_file, params={"theme": "str", "file": "str", "content": "str", "create_backup": "bool?"}, read_only=False)
        reg("list_theme_files", "List files in a theme.", list_theme_files, params={"theme": "str"})
        reg("get_templates", "Get theme templates.", get_templates, params={"theme": "str?"})
        reg("get_global_styles", "Get global styles.", get_global_styles)
        reg("delete_theme", "Delete a theme.", delete_theme, params={"stylesheet": "str"}, destructive=True, read_only=False)
