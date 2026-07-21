"""Multisite registry — manages connections to many WordPress installs."""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic import BaseModel, Field, HttpUrl, SecretStr

from wpmcp.core.config import get_server_settings
from wpmcp.core.exceptions import SiteNotRegisteredError
from wpmcp.wordpress.client import WordPressClient


class Site(BaseModel):
    """A single registered WordPress connection."""

    alias: str
    url: HttpUrl
    username: str
    app_password: SecretStr
    is_default: bool = False

    @property
    def base_url(self) -> str:
        return str(self.url).rstrip("/")


class SiteRegistry:
    """Holds live ``WordPressClient`` instances keyed by lowercase alias."""

    def __init__(self, sites: list[Site], default_alias: str) -> None:
        self._sites: dict[str, Site] = {s.alias: s for s in sites}
        self._clients: dict[str, WordPressClient] = {}
        self._default_alias = default_alias if default_alias in self._sites else (
            sites[0].alias if sites else ""
        )

    @property
    def default_alias(self) -> str:
        return self._default_alias

    @property
    def aliases(self) -> list[str]:
        return list(self._sites)

    def describe(self) -> list[dict[str, object]]:
        return [
            {
                "alias": site.alias,
                "url": site.base_url,
                "username": site.username,
                "is_default": site.alias == self._default_alias,
            }
            for site in self._sites.values()
        ]

    def resolve(self, alias: str | None) -> str:
        if alias and alias.lower() not in self._sites:
            raise SiteNotRegisteredError(alias.lower())
        return (alias or self._default_alias).lower()

    def site(self, alias: str | None) -> Site:
        resolved = self.resolve(alias)
        return self._sites[resolved]

    def client_for(self, alias: str | None) -> WordPressClient:
        resolved = self.resolve(alias)
        if resolved not in self._clients:
            site = self._sites[resolved]
            self._clients[resolved] = WordPressClient(
                base_url=site.base_url,
                username=site.username,
                app_password=site.app_password.get_secret_value(),
            )
        return self._clients[resolved]

    async def aclose(self) -> None:
        for client in self._clients.values():
            await client.aclose()
        self._clients.clear()


def _load_sites_from_env() -> list[Site]:
    """Read WPMCP_SITE_<ALIAS>_{URL,USERNAME,PASSWORD} tuples from the environment."""

    env = os.environ
    settings = get_server_settings()
    aliases: set[str] = set()
    for key in env:
        if key.startswith("WPMCP_SITE_") and key.endswith("_URL"):
            aliases.add(key[len("WPMCP_SITE_") : -len("_URL")].lower())

    sites: list[Site] = []
    for alias in sorted(aliases):
        url = env.get(f"WPMCP_SITE_{alias.upper()}_URL")
        username = env.get(f"WPMCP_SITE_{alias.upper()}_USERNAME")
        password = env.get(f"WPMCP_SITE_{alias.upper()}_PASSWORD")
        if not (url and username and password):
            continue
        sites.append(
            Site(
                alias=alias,
                url=url,
                username=username,
                app_password=password,
                is_default=(alias == settings.default_site),
            )
        )
    return sites


@lru_cache
def get_site_registry() -> SiteRegistry:
    """Return the cached multisite registry built from environment variables."""

    settings = get_server_settings()
    return SiteRegistry(_load_sites_from_env(), default_alias=settings.default_site)
