"""Pydantic models exchanged between services, tools, and the generative UI."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from wpmcp.domain.enums import View


class DomainModel(BaseModel):
    """Base model with predictable, strict serialization."""

    model_config = ConfigDict(extra="forbid", use_enum_values=True)


class WpResult(DomainModel):
    """Unified envelope returned by every WPMCP dispatch tool.

    The generative UI inspects ``view`` to choose a renderer and reads
    ``data`` for the payload. ``meta`` carries counts, pagination, and
    auxiliary context.
    """

    ok: bool = True
    action: str
    domain: str
    site: str
    view: View
    data: Any = None
    message: str | None = None
    meta: dict[str, Any] | None = None

    @classmethod
    def success(
        cls,
        *,
        action: str,
        domain: str,
        site: str,
        view: View,
        data: Any = None,
        message: str | None = None,
        meta: dict[str, Any] | None = None,
    ) -> "WpResult":
        return cls(
            ok=True,
            action=action,
            domain=domain,
            site=site,
            view=view,
            data=data,
            message=message,
            meta=meta,
        )

    @classmethod
    def failure(
        cls,
        *,
        action: str,
        domain: str,
        site: str,
        message: str,
        view: View = View.ERROR,
        data: Any = None,
        meta: dict[str, Any] | None = None,
    ) -> "WpResult":
        return cls(
            ok=False,
            action=action,
            domain=domain,
            site=site,
            view=view,
            data=data,
            message=message,
            meta=meta,
        )


class ActionCatalog(DomainModel):
    """Description of a single dispatch action, surfaced via wp_discover."""

    name: str
    summary: str
    params: dict[str, str] = Field(default_factory=dict)
    destructive: bool = False
    read_only: bool = True


class DomainCatalog(DomainModel):
    """Description of one gateway tool and its actions."""

    tool: str
    domain: str
    title: str
    description: str
    actions: list[ActionCatalog]
