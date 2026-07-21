"""Users domain: users, roles, capabilities, application passwords."""

from __future__ import annotations

import secrets
import string
from typing import Any

from wpmcp.domain.enums import View
from wpmcp.domain.models import WpResult
from wpmcp.services.base import BaseDomainService
from wpmcp.wordpress.client import WordPressClient


def _generate_password(length: int = 24) -> str:
    """Generate a strong random password (letters, digits, symbols)."""

    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]"
    return "".join(secrets.choice(alphabet) for _ in range(length))


class UsersService(BaseDomainService):
    domain = "users"

    def _register(self) -> None:
        reg = self.add

        async def get_users(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            params = {k: p[k] for k in ("search", "roles", "per_page") if k in p}
            data = await c.core("/users", params=params or None)
            return WpResult.success(action="get_users", domain="users", site=site, view=View.USERS, data=data, meta={"count": len(data)})

        async def create_user(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {"username": p.get("username", ""), "email": p.get("email", ""), "password": p.get("password", ""), "roles": p.get("roles", "subscriber")}
            data = await c.core("/users", body=body)
            return WpResult.success(action="create_user", domain="users", site=site, view=View.OPERATION, data=data, message="User created.")

        async def update_user(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            body = {k: p[k] for k in ("email", "name", "roles", "password") if k in p}
            data = await c.core(f"/users/{p.get('id')}", body=body)
            return WpResult.success(action="update_user", domain="users", site=site, view=View.OPERATION, data=data, message="User updated.")

        async def delete_user(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            params = {"reassign": p.get("reassign", 1)} if p.get("reassign") else {"force": "true"}
            data = await c.core_delete(f"/users/{p.get('id')}", params=params)
            return WpResult.success(action="delete_user", domain="users", site=site, view=View.OPERATION, data=data, message="User deleted.")

        async def get_roles(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/users/roles")
            return WpResult.success(action="get_roles", domain="users", site=site, view=View.ROLES, data=data.get("roles", data))

        async def create_role(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/users/roles/create", body={"name": p.get("name", ""), "capabilities": p.get("capabilities", {})})
            return WpResult.success(action="create_role", domain="users", site=site, view=View.OPERATION, data=data, message="Role created.")

        async def delete_role(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/users/roles/delete", body={"name": p.get("name", "")})
            return WpResult.success(action="delete_role", domain="users", site=site, view=View.OPERATION, data=data, message="Role deleted.")

        async def get_capabilities(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.plugin("/users/capabilities", params={"role": p.get("role", "")})
            return WpResult.success(action="get_capabilities", domain="users", site=site, view=View.ROLES, data=data)

        async def assign_role(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core(f"/users/{p.get('user_id')}", body={"roles": p.get("role", "")})
            return WpResult.success(action="assign_role", domain="users", site=site, view=View.OPERATION, data=data, message="Role assigned.")

        async def create_application_password(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            user_id = p.get("user_id")
            app_name = p.get("app_name", "")
            data = await c.core(f"/users/{user_id}/application-passwords", body={"name": app_name})
            secret = data.get("password") if isinstance(data, dict) else None
            safe = {k: v for k, v in data.items() if k != "password"} if isinstance(data, dict) else data
            return WpResult.success(
                action="create_application_password",
                domain="users",
                site=site,
                view=View.OPERATION,
                data={"application_password": safe, "password": secret},
                message="Application password created. Store it now — it will not be shown again.",
            )

        async def list_application_passwords(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            data = await c.core(f"/users/{p.get('user_id')}/application-passwords")
            items = data if isinstance(data, list) else data.get("application_passwords", []) if isinstance(data, dict) else []
            safe = [
                {
                    "uuid": item.get("uuid"),
                    "name": item.get("name"),
                    "created": item.get("created"),
                    "last_used": item.get("last_used"),
                    "last_ip": item.get("last_ip"),
                }
                for item in items
            ]
            return WpResult.success(
                action="list_application_passwords",
                domain="users",
                site=site,
                view=View.USERS,
                data=safe,
                meta={"count": len(safe)},
                message="Application passwords (secrets never included).",
            )

        async def revoke_application_password(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            user_id = p.get("user_id")
            uuid = p.get("uuid", "")
            data = await c.core_delete(f"/users/{user_id}/application-passwords/{uuid}")
            return WpResult.success(
                action="revoke_application_password",
                domain="users",
                site=site,
                view=View.OPERATION,
                data=data,
                message="Application password revoked.",
            )

        async def reset_user_password(c: WordPressClient, site: str, p: dict[str, Any]) -> WpResult:
            user_id = p.get("user_id")
            new_password = p.get("new_password") or _generate_password()
            provided = bool(p.get("new_password"))
            data = await c.core(f"/users/{user_id}", body={"password": new_password})
            return WpResult.success(
                action="reset_user_password",
                domain="users",
                site=site,
                view=View.OPERATION,
                data={"user_id": user_id, "updated": True, "password": new_password},
                message=(
                    "Password reset. Store the new password now — it will not be shown again."
                    if not provided
                    else "Password reset with the provided value."
                ),
            )

        reg("get_users", "List users with optional filters.", get_users, params={"search": "str?", "roles": "str?", "per_page": "int?"})
        reg("create_user", "Create a user.", create_user, params={"username": "str", "email": "str", "password": "str", "roles": "str?"}, read_only=False)
        reg("update_user", "Update a user.", update_user, params={"id": "int", "email": "str?", "name": "str?", "roles": "str?"}, read_only=False)
        reg("delete_user", "Delete a user.", delete_user, params={"id": "int", "reassign": "int?"}, destructive=True, read_only=False)
        reg("get_roles", "List all roles.", get_roles)
        reg("create_role", "Create a custom role.", create_role, params={"name": "str", "capabilities": "object"}, read_only=False)
        reg("delete_role", "Delete a role.", delete_role, params={"name": "str"}, destructive=True, read_only=False)
        reg("get_capabilities", "Get capabilities for a role.", get_capabilities, params={"role": "str"})
        reg("assign_role", "Assign a role to a user.", assign_role, params={"user_id": "int", "role": "str"}, read_only=False)
        reg("create_application_password", "Create an application password for a user; secret returned once.", create_application_password, params={"user_id": "int", "app_name": "str"}, read_only=False)
        reg("list_application_passwords", "List a user's application passwords (no secrets).", list_application_passwords, params={"user_id": "int"})
        reg("revoke_application_password", "Revoke a user's application password by uuid.", revoke_application_password, params={"user_id": "int", "uuid": "str"}, destructive=True, read_only=False)
        reg("reset_user_password", "Reset a user's password (generates a strong one if omitted; returned once).", reset_user_password, params={"user_id": "int", "new_password": "str?"}, destructive=True, read_only=False)
