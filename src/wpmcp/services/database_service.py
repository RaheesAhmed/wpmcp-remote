"""Database domain: tables, SELECT-only queries, options, structure, preview."""

from __future__ import annotations

import re
from typing import Any

from wpmcp.core.exceptions import SecurityError
from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient

_SAFE_QUERY_RE = re.compile(r"^\s*(SELECT|SHOW|DESCRIBE|EXPLAIN)\b", re.IGNORECASE)


class DatabaseService(BaseDomainService):
    domain = "database"

    def _register(self) -> None:
        reg = self.add

        async def list_tables(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/database/tables")
            return WpResult.success(action="list_tables", domain="database", site=site, view=View.TABLES, data=data.get("tables", data), meta={"total": data.get("total"), "prefix": data.get("prefix")})

        async def execute_sql(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            query = p.get("query", "").strip()
            if not query:
                raise SecurityError("Query is required.")
            if not _SAFE_QUERY_RE.match(query):
                raise SecurityError("Only SELECT, SHOW, DESCRIBE, EXPLAIN statements are permitted.")
            data = await c.plugin("/database/query", body={"query": query})
            return WpResult.success(action="execute_sql", domain="database", site=site, view=View.QUERY, data=data.get("results", data), meta={"rows": data.get("rows"), "query": query})

        async def get_option(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/database/option", params={"name": p.get("name", "")})
            return WpResult.success(action="get_option", domain="database", site=site, view=View.OPTIONS, data=data)

        async def update_option(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/database/option", body={"name": p.get("name", ""), "value": p.get("value")})
            return WpResult.success(action="update_option", domain="database", site=site, view=View.OPERATION, data=data, message="Option updated.")

        async def get_table_structure(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            table = p.get("table", "")
            data = await c.plugin("/database/query", body={"query": f"DESCRIBE `{table}`"})
            return WpResult.success(action="get_table_structure", domain="database", site=site, view=View.TABLE_STRUCTURE, data=data.get("results", data), meta={"table": table})

        async def get_table_preview(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            table = p.get("table", "")
            limit = int(p.get("limit", 10))
            data = await c.plugin("/database/query", body={"query": f"SELECT * FROM `{table}` LIMIT {limit}"})
            return WpResult.success(action="get_table_preview", domain="database", site=site, view=View.TABLE_PREVIEW, data=data.get("results", data), meta={"table": table, "limit": limit})

        reg("list_tables", "List all database tables.", list_tables)
        reg("execute_sql", "Run a SELECT/SHOW/DESCRIBE/EXPLAIN query.", execute_sql, params={"query": "str"})
        reg("get_option", "Read a WordPress option.", get_option, params={"name": "str"})
        reg("update_option", "Update a WordPress option.", update_option, params={"name": "str", "value": "any"}, read_only=False)
        reg("get_table_structure", "Describe a table's structure.", get_table_structure, params={"table": "str"})
        reg("get_table_preview", "Preview rows from a table.", get_table_preview, params={"table": "str", "limit": "int?"})
