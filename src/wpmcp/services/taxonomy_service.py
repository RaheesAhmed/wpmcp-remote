"""Taxonomy domain: post types, taxonomies, terms."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


class TaxonomyService(BaseDomainService):
    domain = "taxonomy"

    def _register(self) -> None:
        reg = self.add

        async def get_post_types(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core("/types")
            return WpResult.success(action="get_post_types", domain="taxonomy", site=site, view=View.TAXONOMY, data=data)

        async def get_post_type(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core(f"/types/{p.get('type', 'post')}")
            return WpResult.success(action="get_post_type", domain="taxonomy", site=site, view=View.TAXONOMY, data=data)

        async def get_taxonomies(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core("/taxonomies")
            return WpResult.success(action="get_taxonomies", domain="taxonomy", site=site, view=View.TAXONOMY, data=data)

        async def get_terms(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            taxonomy = p.get("taxonomy", "category")
            data = await c.core(f"/{taxonomy}")
            return WpResult.success(action="get_terms", domain="taxonomy", site=site, view=View.TERMS, data=data, meta={"count": len(data), "taxonomy": taxonomy})

        async def create_term(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            taxonomy = p.get("taxonomy", "category")
            body = {"name": p.get("name", "")}
            if p.get("parent") is not None:
                body["parent"] = p["parent"]
            data = await c.core(f"/{taxonomy}", body=body)
            return WpResult.success(action="create_term", domain="taxonomy", site=site, view=View.OPERATION, data=data, message="Term created.")

        async def update_term(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            taxonomy = p.get("taxonomy", "category")
            body = {k: p[k] for k in ("name", "description", "parent") if k in p}
            data = await c.core(f"/{taxonomy}/{p.get('id')}", body=body)
            return WpResult.success(action="update_term", domain="taxonomy", site=site, view=View.OPERATION, data=data, message="Term updated.")

        async def delete_term(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            taxonomy = p.get("taxonomy", "category")
            data = await c.core_delete(f"/{taxonomy}/{p.get('id')}", params={"force": "true"})
            return WpResult.success(action="delete_term", domain="taxonomy", site=site, view=View.OPERATION, data=data, message="Term deleted.")

        reg("get_post_types", "List all registered post types.", get_post_types)
        reg("get_post_type", "Get details for a post type.", get_post_type, params={"type": "str"})
        reg("get_taxonomies", "List all taxonomies.", get_taxonomies)
        reg("get_terms", "List terms in a taxonomy.", get_terms, params={"taxonomy": "str"})
        reg("create_term", "Create a term.", create_term, params={"taxonomy": "str", "name": "str", "parent": "int?"}, read_only=False)
        reg("update_term", "Update a term.", update_term, params={"taxonomy": "str", "id": "int", "name": "str?", "description": "str?"}, read_only=False)
        reg("delete_term", "Delete a term.", delete_term, params={"taxonomy": "str", "id": "int"}, destructive=True, read_only=False)
