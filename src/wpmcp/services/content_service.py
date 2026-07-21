"""Content domain: posts, pages, media, comments, categories, tags."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


def _post_summary(post: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": post.get("id"),
        "title": (post.get("title") or {}).get("rendered", ""),
        "status": post.get("status"),
        "type": post.get("type"),
        "date": post.get("date"),
        "link": post.get("link"),
        "author": post.get("author"),
        "excerpt": (post.get("excerpt") or {}).get("rendered", ""),
    }


class ContentService(BaseDomainService):
    domain = "content"

    def _register(self) -> None:
        reg = self.add

        async def create_post(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {"title": p.get("title", ""), "content": p.get("content", ""), "status": p.get("status", "draft")}
            if p.get("excerpt") is not None:
                body["excerpt"] = p["excerpt"]
            post = await c.core("/posts", body=body)
            return WpResult.success(action="create_post", domain="content", site=site, view=View.POST, data=post, message="Post created.")

        async def update_post(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            post_id = p.get("id")
            body = {k: p[k] for k in ("title", "content", "status", "excerpt") if k in p}
            post = await c.core(f"/posts/{post_id}", body=body)
            return WpResult.success(action="update_post", domain="content", site=site, view=View.POST, data=post, message="Post updated.")

        async def delete_post(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            post_id = p.get("id")
            force = bool(p.get("force", False))
            result = await c.core_delete(f"/posts/{post_id}", params={"force": "true"} if force else None)
            return WpResult.success(action="delete_post", domain="content", site=site, view=View.OPERATION, data=result, message="Post deleted.")

        async def get_posts(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            params = {k: p[k] for k in ("search", "status", "per_page", "page", "orderby", "order", "author", "categories") if k in p}
            posts = await c.core("/posts", params=params)
            return WpResult.success(action="get_posts", domain="content", site=site, view=View.POSTS, data=[_post_summary(x) for x in posts], meta={"count": len(posts)})

        async def get_post(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            post = await c.core(f"/posts/{p.get('id')}")
            return WpResult.success(action="get_post", domain="content", site=site, view=View.POST, data=post)

        async def search_posts(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            posts = await c.core("/posts", params={"search": p.get("query", "")})
            return WpResult.success(action="search_posts", domain="content", site=site, view=View.POSTS, data=[_post_summary(x) for x in posts], meta={"count": len(posts)})

        async def create_page(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {"title": p.get("title", ""), "content": p.get("content", ""), "status": p.get("status", "draft")}
            if p.get("parent") is not None:
                body["parent"] = p["parent"]
            page = await c.core("/pages", body=body)
            return WpResult.success(action="create_page", domain="content", site=site, view=View.POST, data=page, message="Page created.")

        async def get_pages(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            pages = await c.core("/pages", params={"search": p.get("search")} if p.get("search") else None)
            return WpResult.success(action="get_pages", domain="content", site=site, view=View.PAGES, data=pages, meta={"count": len(pages)})

        async def delete_page(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            result = await c.core_delete(f"/pages/{p.get('id')}", params={"force": "true"} if p.get("force") else None)
            return WpResult.success(action="delete_page", domain="content", site=site, view=View.OPERATION, data=result, message="Page deleted.")

        async def upload_media(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            import base64
            raw = p.get("content_b64") or p.get("content")
            if raw and isinstance(raw, str) and p.get("content_b64"):
                content = base64.b64decode(raw)
            else:
                content = (raw or "").encode()
            media = await c.upload("/media", p.get("filename", "upload.bin"), content, p.get("mime", "application/octet-stream"))
            return WpResult.success(action="upload_media", domain="content", site=site, view=View.POST, data=media, message="Media uploaded.")

        async def get_media(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            media = await c.core("/media", params={"per_page": p.get("per_page", 50)})
            return WpResult.success(action="get_media", domain="content", site=site, view=View.MEDIA_GALLERY, data=media, meta={"count": len(media)})

        async def delete_media(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            result = await c.core_delete(f"/media/{p.get('id')}", params={"force": "true"})
            return WpResult.success(action="delete_media", domain="content", site=site, view=View.OPERATION, data=result, message="Media deleted.")

        async def get_comments(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            comments = await c.core("/comments", params={"post": p.get("post")} if p.get("post") else None)
            return WpResult.success(action="get_comments", domain="content", site=site, view=View.COMMENTS, data=comments, meta={"count": len(comments)})

        async def update_comment(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {k: p[k] for k in ("status", "content", "author_name", "author_email") if k in p}
            comment = await c.core(f"/comments/{p.get('id')}", body=body)
            return WpResult.success(action="update_comment", domain="content", site=site, view=View.OPERATION, data=comment, message="Comment updated.")

        async def get_categories(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            cats = await c.core("/categories")
            return WpResult.success(action="get_categories", domain="content", site=site, view=View.TERMS, data=cats, meta={"count": len(cats)})

        async def create_category(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {"name": p.get("name", "")}
            if p.get("parent") is not None:
                body["parent"] = p["parent"]
            cat = await c.core("/categories", body=body)
            return WpResult.success(action="create_category", domain="content", site=site, view=View.OPERATION, data=cat, message="Category created.")

        async def get_tags(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            tags = await c.core("/tags")
            return WpResult.success(action="get_tags", domain="content", site=site, view=View.TERMS, data=tags, meta={"count": len(tags)})

        reg("create_post", "Create a blog post.", create_post, params={"title": "str", "content": "str", "status": "draft|publish|pending|future", "excerpt": "str?"}, destructive=False, read_only=False)
        reg("update_post", "Update an existing post by id.", update_post, params={"id": "int", "title": "str?", "content": "str?", "status": "str?", "excerpt": "str?"}, destructive=False, read_only=False)
        reg("delete_post", "Delete a post by id.", delete_post, params={"id": "int", "force": "bool?"}, destructive=True, read_only=False)
        reg("get_posts", "List posts with optional filters.", get_posts, params={"search": "str?", "status": "str?", "per_page": "int?", "page": "int?"})
        reg("get_post", "Get a single post by id.", get_post, params={"id": "int"})
        reg("search_posts", "Search posts by keyword.", search_posts, params={"query": "str"})
        reg("create_page", "Create a new page.", create_page, params={"title": "str", "content": "str", "status": "str?", "parent": "int?"}, read_only=False)
        reg("get_pages", "List pages.", get_pages, params={"search": "str?"})
        reg("delete_page", "Delete a page by id.", delete_page, params={"id": "int", "force": "bool?"}, destructive=True, read_only=False)
        reg("upload_media", "Upload a media file (base64 content).", upload_media, params={"filename": "str", "content_b64": "str", "mime": "str?"}, read_only=False)
        reg("get_media", "List media library items.", get_media, params={"per_page": "int?"})
        reg("delete_media", "Delete a media item by id.", delete_media, params={"id": "int"}, destructive=True, read_only=False)
        reg("get_comments", "List comments, optionally for a post.", get_comments, params={"post": "int?"})
        reg("update_comment", "Update a comment (status/content).", update_comment, params={"id": "int", "status": "str?", "content": "str?"}, read_only=False)
        reg("get_categories", "List all categories.", get_categories)
        reg("create_category", "Create a category.", create_category, params={"name": "str", "parent": "int?"}, read_only=False)
        reg("get_tags", "List all tags.", get_tags)
