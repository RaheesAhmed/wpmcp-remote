"""Backup & migration domain: full/db/files backup, restore, export/import, clone."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


class BackupService(BaseDomainService):
    domain = "backup"

    def _register(self) -> None:
        reg = self.add

        async def full_backup(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/backup/full", body={"destination": p.get("destination", "")})
            return WpResult.success(action="full_backup", domain="backup", site=site, view=View.BACKUP, data=data, message="Full backup started.")

        async def backup_database(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/backup/database", body={"destination": p.get("destination", "")})
            return WpResult.success(action="backup_database", domain="backup", site=site, view=View.BACKUP, data=data, message="Database backup started.")

        async def backup_files(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/backup/files", body={"destination": p.get("destination", "")})
            return WpResult.success(action="backup_files", domain="backup", site=site, view=View.BACKUP, data=data, message="Files backup started.")

        async def list_backups(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/backup/list")
            return WpResult.success(action="list_backups", domain="backup", site=site, view=View.BACKUPS, data=data.get("backups", data), meta={"count": len(data.get("backups", [])) if isinstance(data, dict) else 0})

        async def restore_backup(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/backup/restore", body={"id": p.get("id")})
            return WpResult.success(action="restore_backup", domain="backup", site=site, view=View.OPERATION, data=data, message="Backup restored.")

        async def delete_backup(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/backup/delete", body={"id": p.get("id")})
            return WpResult.success(action="delete_backup", domain="backup", site=site, view=View.OPERATION, data=data, message="Backup deleted.")

        async def export_content(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/backup/export", body={"post_type": p.get("post_type", "post")})
            return WpResult.success(action="export_content", domain="backup", site=site, view=View.BACKUP, data=data, message="Content exported.")

        async def import_content(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/backup/import", body={"file": p.get("file", "")})
            return WpResult.success(action="import_content", domain="backup", site=site, view=View.OPERATION, data=data, message="Content imported.")

        async def clone_to_staging(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/backup/clone", body={"target": p.get("target", "")})
            return WpResult.success(action="clone_to_staging", domain="backup", site=site, view=View.OPERATION, data=data, message="Clone to staging started.")

        async def schedule_backups(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/backup/schedule", body={"recurrence": p.get("recurrence", "daily")})
            return WpResult.success(action="schedule_backups", domain="backup", site=site, view=View.OPERATION, data=data, message="Backups scheduled.")

        reg("full_backup", "Run a full site backup.", full_backup, params={"destination": "str?"}, read_only=False)
        reg("backup_database", "Back up the database.", backup_database, params={"destination": "str?"}, read_only=False)
        reg("backup_files", "Back up site files.", backup_files, params={"destination": "str?"}, read_only=False)
        reg("list_backups", "List available backups.", list_backups)
        reg("restore_backup", "Restore a backup by id.", restore_backup, params={"id": "str"}, destructive=True, read_only=False)
        reg("delete_backup", "Delete a backup by id.", delete_backup, params={"id": "str"}, destructive=True, read_only=False)
        reg("export_content", "Export content as XML.", export_content, params={"post_type": "str?"}, read_only=False)
        reg("import_content", "Import content from XML.", import_content, params={"file": "str"}, read_only=False)
        reg("clone_to_staging", "Clone the site to staging.", clone_to_staging, params={"target": "str"}, destructive=True, read_only=False)
        reg("schedule_backups", "Schedule recurring backups.", schedule_backups, params={"recurrence": "str"}, read_only=False)
