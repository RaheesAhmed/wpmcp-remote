"""Plugins domain: activate, deactivate, delete, read/write plugin files."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


class PluginService(BaseDomainService):
    domain = "plugins"

    def _register(self) -> None:
        reg = self.add

        async def get_plugins(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/plugins")
            plugins = data.get("plugins", data) if isinstance(data, dict) else data
            return WpResult.success(action="get_plugins", domain="plugins", site=site, view=View.PLUGINS, data=plugins, meta={"count": len(plugins) if isinstance(plugins, list) else 0})

        async def activate_plugin(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/plugins/activate", body={"plugin": p.get("plugin", "")})
            return WpResult.success(action="activate_plugin", domain="plugins", site=site, view=View.OPERATION, data=data, message=f"Plugin '{p.get('plugin')}' activated.")

        async def deactivate_plugin(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/plugins/deactivate", body={"plugin": p.get("plugin", "")})
            return WpResult.success(action="deactivate_plugin", domain="plugins", site=site, view=View.OPERATION, data=data, message=f"Plugin '{p.get('plugin')}' deactivated.")

        async def delete_plugin(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/plugins/delete", body={"plugin": p.get("plugin", "")})
            return WpResult.success(action="delete_plugin", domain="plugins", site=site, view=View.OPERATION, data=data, message="Plugin deleted.")

        async def read_plugin_file(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/plugins/file/read", body={"plugin": p.get("plugin", ""), "file": p.get("file", "")})
            return WpResult.success(action="read_plugin_file", domain="plugins", site=site, view=View.FILE, data=data)

        async def write_plugin_file(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/plugins/file/write", body={"plugin": p.get("plugin", ""), "file": p.get("file", ""), "content": p.get("content", ""), "create_backup": bool(p.get("create_backup", True))})
            return WpResult.success(action="write_plugin_file", domain="plugins", site=site, view=View.OPERATION, data=data, message="Plugin file written.")

        async def list_plugin_files(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/plugins/files", body={"plugin": p.get("plugin", "")})
            files = data.get("files", data) if isinstance(data, dict) else data
            return WpResult.success(action="list_plugin_files", domain="plugins", site=site, view=View.PLUGIN_FILES, data=files, meta={"count": len(files) if isinstance(files, list) else 0})

        async def get_active_plugins(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/plugins/active")
            return WpResult.success(action="get_active_plugins", domain="plugins", site=site, view=View.PLUGINS, data=data.get("plugins", data))

        async def plugin_exists(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/plugins/exists", body={"plugin": p.get("plugin", "")})
            return WpResult.success(action="plugin_exists", domain="plugins", site=site, view=View.OPERATION, data=data)

        reg("get_plugins", "List all installed plugins.", get_plugins)
        reg("activate_plugin", "Activate a plugin.", activate_plugin, params={"plugin": "str"}, read_only=False)
        reg("deactivate_plugin", "Deactivate a plugin.", deactivate_plugin, params={"plugin": "str"}, read_only=False)
        reg("delete_plugin", "Delete a plugin.", delete_plugin, params={"plugin": "str"}, destructive=True, read_only=False)
        reg("read_plugin_file", "Read a file from a plugin.", read_plugin_file, params={"plugin": "str", "file": "str"})
        reg("write_plugin_file", "Write a file in a plugin (with backup).", write_plugin_file, params={"plugin": "str", "file": "str", "content": "str", "create_backup": "bool?"}, read_only=False)
        reg("list_plugin_files", "List files in a plugin.", list_plugin_files, params={"plugin": "str"})
        reg("get_active_plugins", "List active plugins.", get_active_plugins)
        reg("plugin_exists", "Check if a plugin is installed.", plugin_exists, params={"plugin": "str"})
