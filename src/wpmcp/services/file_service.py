"""Filesystem domain: read/write/copy/move/delete/list/info via the plugin."""

from __future__ import annotations

from typing import Any

from wpmcp.core.exceptions import SecurityError
from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient

_ALLOWED_DIRS = ("wp-content/themes", "wp-content/plugins", "wp-content/uploads", "wp-content/mu-plugins")


def _validate_path(path: str) -> str:
    normalized = path.replace("\\", "/").lstrip("./")
    if ".." in normalized.split("/"):
        raise SecurityError(f"Path traversal is not allowed: {path}")
    if not any(normalized.startswith(prefix) for prefix in _ALLOWED_DIRS):
        raise SecurityError(f"Path outside allowed directories: {path}")
    return normalized


class FileService(BaseDomainService):
    domain = "files"

    def _register(self) -> None:
        reg = self.add

        async def read_file(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            path = _validate_path(p.get("path", ""))
            data = await c.plugin("/file/read", body={"path": path})
            return WpResult.success(action="read_file", domain="files", site=site, view=View.FILE, data=data)

        async def write_file(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            path = _validate_path(p.get("path", ""))
            data = await c.plugin("/file/write", body={"path": path, "content": p.get("content", ""), "create_backup": bool(p.get("create_backup", True))})
            return WpResult.success(action="write_file", domain="files", site=site, view=View.OPERATION, data=data, message="File written.")

        async def delete_file(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            path = _validate_path(p.get("path", ""))
            data = await c.plugin("/file/delete", body={"path": path, "create_backup": bool(p.get("create_backup", True))})
            return WpResult.success(action="delete_file", domain="files", site=site, view=View.OPERATION, data=data, message="File deleted.")

        async def copy_file(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            source = _validate_path(p.get("source", ""))
            destination = _validate_path(p.get("destination", ""))
            data = await c.plugin("/file/copy", body={"source": source, "destination": destination})
            return WpResult.success(action="copy_file", domain="files", site=site, view=View.OPERATION, data=data, message="File copied.")

        async def move_file(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            source = _validate_path(p.get("source", ""))
            destination = _validate_path(p.get("destination", ""))
            data = await c.plugin("/file/move", body={"source": source, "destination": destination})
            return WpResult.success(action="move_file", domain="files", site=site, view=View.OPERATION, data=data, message="File moved.")

        async def list_files(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            path = _validate_path(p.get("path", "wp-content/themes"))
            data = await c.plugin("/file/list", body={"path": path, "recursive": bool(p.get("recursive", False))})
            files = data.get("files", data) if isinstance(data, dict) else data
            return WpResult.success(action="list_files", domain="files", site=site, view=View.FILES, data=files, meta={"count": len(files) if isinstance(files, list) else 0, "path": path})

        async def file_info(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            path = _validate_path(p.get("path", ""))
            data = await c.plugin("/file/info", body={"path": path})
            return WpResult.success(action="file_info", domain="files", site=site, view=View.FILE, data=data)

        reg("read_file", "Read a file from an allowed directory.", read_file, params={"path": "str"})
        reg("write_file", "Write a file (with backup).", write_file, params={"path": "str", "content": "str", "create_backup": "bool?"}, read_only=False)
        reg("delete_file", "Delete a file (with backup).", delete_file, params={"path": "str", "create_backup": "bool?"}, destructive=True, read_only=False)
        reg("copy_file", "Copy a file.", copy_file, params={"source": "str", "destination": "str"}, read_only=False)
        reg("move_file", "Move or rename a file.", move_file, params={"source": "str", "destination": "str"}, read_only=False)
        reg("list_files", "List files in a directory.", list_files, params={"path": "str", "recursive": "bool?"})
        reg("file_info", "Get file metadata.", file_info, params={"path": "str"})
