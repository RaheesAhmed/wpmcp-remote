"""Base service with the dispatch + catalog contract."""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Protocol

from wpmcp.domain.models import ActionCatalog, WpResult
from wpmcp.wordpress.client import WordPressClient
from wpmcp.wordpress.multisite import SiteRegistry

ActionHandler = Callable[[WordPressClient, str, dict[str, Any]], Awaitable[WpResult]]


class _CatalogProvider(Protocol):
    def catalog(self) -> list[ActionCatalog]: ...


class BaseDomainService:
    """Shared dispatch logic for every domain service.

    Subclasses populate ``self.actions`` (name -> handler) and ``self._catalog``
    (list of ``ActionCatalog``). Handlers receive a resolved ``WordPressClient``
    and the validated ``params`` dict, and return a ``WpResult``.
    """

    domain: str = "base"

    def __init__(self, registry: SiteRegistry) -> None:
        self.registry = registry
        self.actions: dict[str, ActionHandler] = {}
        self._catalog: list[ActionCatalog] = []
        self._register()

    def _register(self) -> None:
        """Override to populate ``self.actions`` and ``self._catalog``."""

    def catalog(self) -> list[ActionCatalog]:
        return list(self._catalog)

    def add(self, name: str, summary: str, handler: ActionHandler, *, params: dict[str, str] | None = None, destructive: bool = False, read_only: bool = True) -> None:
        self.actions[name] = handler
        self._catalog.append(
            ActionCatalog(
                name=name,
                summary=summary,
                params=params or {},
                destructive=destructive,
                read_only=read_only,
            )
        )

    async def dispatch(self, action: str, site: str | None, params: dict[str, Any]) -> WpResult:
        from wpmcp.core.exceptions import UnknownActionError

        handler = self.actions.get(action)
        if handler is None:
            raise UnknownActionError(action, self.domain, list(self.actions))
        client = self.registry.client_for(site)
        resolved_site = self.registry.resolve(site)
        return await handler(client, resolved_site, params)
