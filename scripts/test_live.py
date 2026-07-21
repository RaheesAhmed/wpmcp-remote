"""Live end-to-end test against the configured WordPress site.

Drives the real FastMCP server in-process (reads .env), calls wp_discover and
a read-only wp_content action against the default site. Prints status only —
never the token or password.
"""

from __future__ import annotations

import asyncio

from fastmcp import Client

import wpmcp.server as server
from wpmcp.wordpress.multisite import get_site_registry


async def main() -> None:
    sites = get_site_registry()
    print(f"Registered sites: {sites.aliases}")
    if not sites.aliases:
        print("FAIL: no sites registered. Check .env (WPMCP_SITE_*_URL / _TOKEN).")
        return
    default = sites.default_alias
    site = sites.site(default)
    print(f"Default site: {default} -> {site.base_url} (auth: {'token' if site.api_token else 'app-password'})")

    async with Client(server.mcp) as client:
        discovery = await client.call_tool("wp_discover", {})
        sc = discovery.structured_content
        domains = sc["result"] if isinstance(sc, dict) and "result" in sc else sc
        total = sum(len(d.get("actions", [])) for d in domains)
        print(f"wp_discover OK: {len(domains)} domains, {total} actions")

        result = await client.call_tool(
            "wp_content",
            {"action": "get_posts", "site": default, "params": {"per_page": 3}},
        )
        rsc = result.structured_content
        if isinstance(rsc, dict) and rsc.get("ok"):
            data = rsc.get("data", {})
            posts = data.get("posts") or data.get("items") or []
            print(f"get_posts OK: {len(posts)} post(s) returned from WordPress.")
            for p in posts[:3]:
                title = p.get("title", {})
                if isinstance(title, dict):
                    title = title.get("rendered", "")
                print(f"  - [{p.get('id')}] {title}")
        else:
            print(f"get_posts FAIL: {rsc}")


if __name__ == "__main__":
    asyncio.run(main())
