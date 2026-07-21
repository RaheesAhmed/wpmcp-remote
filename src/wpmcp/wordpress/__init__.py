"""WordPress connectivity: async REST client, endpoint map, and multisite registry."""

from wpmcp.wordpress.client import WordPressClient
from wpmcp.wordpress.multisite import Site, SiteRegistry, get_site_registry

__all__ = ["WordPressClient", "Site", "SiteRegistry", "get_site_registry"]
