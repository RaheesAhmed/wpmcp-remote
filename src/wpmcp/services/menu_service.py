"""Menus domain: menus, items, and locations."""

from __future__ import annotations

from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


class MenuService(BaseDomainService):
    domain = "menus"

    def _register(self) -> None:
        reg = self.add

        async def get_menus(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core("/menus")
            return WpResult.success(action="get_menus", domain="menus", site=site, view=View.MENUS, data=data, meta={"count": len(data)})

        async def create_menu(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core("/menus", body={"name": p.get("name", "")})
            return WpResult.success(action="create_menu", domain="menus", site=site, view=View.OPERATION, data=data, message="Menu created.")

        async def delete_menu(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core_delete(f"/menus/{p.get('id')}", params={"force": "true"})
            return WpResult.success(action="delete_menu", domain="menus", site=site, view=View.OPERATION, data=data, message="Menu deleted.")

        async def get_menu_items(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core("/menu-items", params={"menus": p.get("menu")} if p.get("menu") else None)
            return WpResult.success(action="get_menu_items", domain="menus", site=site, view=View.MENU_ITEMS, data=data, meta={"count": len(data)})

        async def create_menu_item(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {"title": p.get("title", ""), "url": p.get("url", ""), "menus": p.get("menu")}
            if p.get("object_id") is not None:
                body["object_id"] = p["object_id"]
                body["object"] = p.get("object", "post")
            data = await c.core("/menu-items", body=body)
            return WpResult.success(action="create_menu_item", domain="menus", site=site, view=View.OPERATION, data=data, message="Menu item added.")

        async def update_menu_item(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {k: p[k] for k in ("title", "url", "status") if k in p}
            data = await c.core(f"/menu-items/{p.get('id')}", body=body)
            return WpResult.success(action="update_menu_item", domain="menus", site=site, view=View.OPERATION, data=data, message="Menu item updated.")

        async def delete_menu_item(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core_delete(f"/menu-items/{p.get('id')}", params={"force": "true"})
            return WpResult.success(action="delete_menu_item", domain="menus", site=site, view=View.OPERATION, data=data, message="Menu item deleted.")

        async def get_menu_locations(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core("/menu-locations")
            return WpResult.success(action="get_menu_locations", domain="menus", site=site, view=View.MENU_LOCATIONS, data=data)

        async def assign_menu_to_location(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/menus/assign-location", body={"location": p.get("location", ""), "menu_id": p.get("menu_id")})
            return WpResult.success(action="assign_menu_to_location", domain="menus", site=site, view=View.OPERATION, data=data, message="Menu assigned to location.")

        reg("get_menus", "List all navigation menus.", get_menus)
        reg("create_menu", "Create a menu.", create_menu, params={"name": "str"}, read_only=False)
        reg("delete_menu", "Delete a menu by id.", delete_menu, params={"id": "int"}, destructive=True, read_only=False)
        reg("get_menu_items", "List items in a menu.", get_menu_items, params={"menu": "int?"})
        reg("create_menu_item", "Add an item to a menu.", create_menu_item, params={"title": "str", "url": "str", "menu": "int", "object_id": "int?", "object": "str?"}, read_only=False)
        reg("update_menu_item", "Update a menu item.", update_menu_item, params={"id": "int", "title": "str?", "url": "str?"}, read_only=False)
        reg("delete_menu_item", "Delete a menu item.", delete_menu_item, params={"id": "int"}, destructive=True, read_only=False)
        reg("get_menu_locations", "List registered menu locations.", get_menu_locations)
        reg("assign_menu_to_location", "Assign a menu to a location.", assign_menu_to_location, params={"location": "str", "menu_id": "int"}, read_only=False)
