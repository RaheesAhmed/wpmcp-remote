"""Gutenberg blocks domain: block types, patterns, reusable blocks, templates."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


class BlocksService(BaseDomainService):
    domain = "blocks"

    def _register(self) -> None:
        reg = self.add

        async def get_block_types(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core("/block-types")
            return WpResult.success(action="get_block_types", domain="blocks", site=site, view=View.BLOCKS, data=data, meta={"count": len(data)})

        async def get_block_patterns(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/blocks/patterns")
            return WpResult.success(action="get_block_patterns", domain="blocks", site=site, view=View.BLOCK_PATTERNS, data=data.get("patterns", data))

        async def get_block_categories(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/blocks/pattern-categories")
            return WpResult.success(action="get_block_categories", domain="blocks", site=site, view=View.BLOCK_PATTERNS, data=data.get("categories", data))

        async def get_reusable_blocks(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core("/blocks", params={"per_page": p.get("per_page", 50)})
            return WpResult.success(action="get_reusable_blocks", domain="blocks", site=site, view=View.REUSABLE_BLOCKS, data=data, meta={"count": len(data)})

        async def create_reusable_block(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core("/blocks", body={"title": p.get("title", ""), "content": p.get("content", ""), "status": "publish"})
            return WpResult.success(action="create_reusable_block", domain="blocks", site=site, view=View.OPERATION, data=data, message="Reusable block created.")

        async def update_reusable_block(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {k: p[k] for k in ("title", "content") if k in p}
            data = await c.core(f"/blocks/{p.get('id')}", body=body)
            return WpResult.success(action="update_reusable_block", domain="blocks", site=site, view=View.OPERATION, data=data, message="Reusable block updated.")

        async def delete_reusable_block(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core_delete(f"/blocks/{p.get('id')}", params={"force": "true"})
            return WpResult.success(action="delete_reusable_block", domain="blocks", site=site, view=View.OPERATION, data=data, message="Reusable block deleted.")

        async def parse_blocks(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/blocks/parse", body={"content": p.get("content", "")})
            return WpResult.success(action="parse_blocks", domain="blocks", site=site, view=View.BLOCKS, data=data.get("blocks", data))

        async def get_block_editor_settings(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/blocks/editor-settings")
            return WpResult.success(action="get_block_editor_settings", domain="blocks", site=site, view=View.BLOCKS, data=data)

        async def get_style_variations(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/blocks/style-variations")
            return WpResult.success(action="get_style_variations", domain="blocks", site=site, view=View.THEME_JSON, data=data.get("variations", data))

        reg("get_block_types", "List all registered block types.", get_block_types)
        reg("get_block_patterns", "List block patterns.", get_block_patterns)
        reg("get_block_categories", "List pattern categories.", get_block_categories)
        reg("get_reusable_blocks", "List reusable blocks.", get_reusable_blocks, params={"per_page": "int?"})
        reg("create_reusable_block", "Create a reusable block.", create_reusable_block, params={"title": "str", "content": "str"}, read_only=False)
        reg("update_reusable_block", "Update a reusable block.", update_reusable_block, params={"id": "int", "title": "str?", "content": "str?"}, read_only=False)
        reg("delete_reusable_block", "Delete a reusable block.", delete_reusable_block, params={"id": "int"}, destructive=True, read_only=False)
        reg("parse_blocks", "Parse block content into blocks.", parse_blocks, params={"content": "str"})
        reg("get_block_editor_settings", "Get block editor settings.", get_block_editor_settings)
        reg("get_style_variations", "Get global style variations.", get_style_variations)
