"""Domain services — one per WordPress capability area.

Every service exposes a ``dispatch(action, site, params)`` coroutine and a
``catalog()`` description used by ``wp_discover``.
"""

from wpmcp.services.base import ActionHandler, BaseDomainService

__all__ = ["ActionHandler", "BaseDomainService"]
