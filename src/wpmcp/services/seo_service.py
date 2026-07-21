"""SEO domain: sitemaps, robots.txt, redirects, OG/Twitter, schema, analysis."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


class SeoService(BaseDomainService):
    domain = "seo"

    def _register(self) -> None:
        reg = self.add

        async def set_seo_meta(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {"post_id": p.get("post_id"), "meta_description": p.get("meta_description", ""), "focus_keyword": p.get("focus_keyword", "")}
            data = await c.plugin("/seo/meta", body=body)
            return WpResult.success(action="set_seo_meta", domain="seo", site=site, view=View.OPERATION, data=data, message="SEO meta saved.")

        async def set_custom_meta(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/custom-meta", body={"post_id": p.get("post_id"), "key": p.get("key", ""), "value": p.get("value")})
            return WpResult.success(action="set_custom_meta", domain="seo", site=site, view=View.OPERATION, data=data, message="Custom meta saved.")

        async def generate_sitemap(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/sitemap")
            return WpResult.success(action="generate_sitemap", domain="seo", site=site, view=View.SEO, data=data)

        async def get_robots_txt(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/robots")
            return WpResult.success(action="get_robots_txt", domain="seo", site=site, view=View.SEO, data=data)

        async def update_robots_txt(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/robots", body={"content": p.get("content", "")})
            return WpResult.success(action="update_robots_txt", domain="seo", site=site, view=View.OPERATION, data=data, message="robots.txt updated.")

        async def create_redirect(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/redirects", body={"from": p.get("from", ""), "to": p.get("to", ""), "status": p.get("status", 301)})
            return WpResult.success(action="create_redirect", domain="seo", site=site, view=View.OPERATION, data=data, message="Redirect created.")

        async def get_redirects(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/redirects")
            return WpResult.success(action="get_redirects", domain="seo", site=site, view=View.SEO, data=data.get("redirects", data))

        async def delete_redirect(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/redirects/delete", body={"id": p.get("id")})
            return WpResult.success(action="delete_redirect", domain="seo", site=site, view=View.OPERATION, data=data, message="Redirect deleted.")

        async def set_og_tags(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/og", body={"post_id": p.get("post_id"), "tags": p.get("tags", {})})
            return WpResult.success(action="set_og_tags", domain="seo", site=site, view=View.OPERATION, data=data, message="Open Graph tags saved.")

        async def set_twitter_cards(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/twitter", body={"post_id": p.get("post_id"), "cards": p.get("cards", {})})
            return WpResult.success(action="set_twitter_cards", domain="seo", site=site, view=View.OPERATION, data=data, message="Twitter cards saved.")

        async def set_canonical_url(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/canonical", body={"post_id": p.get("post_id"), "url": p.get("url", "")})
            return WpResult.success(action="set_canonical_url", domain="seo", site=site, view=View.OPERATION, data=data, message="Canonical URL saved.")

        async def set_schema_markup(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/schema", body={"post_id": p.get("post_id"), "schema": p.get("schema", {})})
            return WpResult.success(action="set_schema_markup", domain="seo", site=site, view=View.OPERATION, data=data, message="Schema markup saved.")

        async def analyze_seo(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/seo/analyze", body={"post_id": p.get("post_id")})
            return WpResult.success(action="analyze_seo", domain="seo", site=site, view=View.SEO, data=data)

        reg("set_seo_meta", "Set SEO meta for a post.", set_seo_meta, params={"post_id": "int", "meta_description": "str", "focus_keyword": "str"}, read_only=False)
        reg("set_custom_meta", "Set custom post meta.", set_custom_meta, params={"post_id": "int", "key": "str", "value": "any"}, read_only=False)
        reg("generate_sitemap", "Generate an XML sitemap.", generate_sitemap)
        reg("get_robots_txt", "Read robots.txt.", get_robots_txt)
        reg("update_robots_txt", "Update robots.txt.", update_robots_txt, params={"content": "str"}, read_only=False)
        reg("create_redirect", "Create a redirect.", create_redirect, params={"from": "str", "to": "str", "status": "int?"}, read_only=False)
        reg("get_redirects", "List redirects.", get_redirects)
        reg("delete_redirect", "Delete a redirect.", delete_redirect, params={"id": "int"}, destructive=True, read_only=False)
        reg("set_og_tags", "Set Open Graph tags.", set_og_tags, params={"post_id": "int", "tags": "object"}, read_only=False)
        reg("set_twitter_cards", "Set Twitter card tags.", set_twitter_cards, params={"post_id": "int", "cards": "object"}, read_only=False)
        reg("set_canonical_url", "Set a canonical URL.", set_canonical_url, params={"post_id": "int", "url": "str"}, read_only=False)
        reg("set_schema_markup", "Set schema markup.", set_schema_markup, params={"post_id": "int", "schema": "object"}, read_only=False)
        reg("analyze_seo", "Analyze SEO for a post.", analyze_seo, params={"post_id": "int"})
