"""Async WordPress REST client with connection pooling and basic auth."""

from __future__ import annotations

from typing import Any

import httpx

from wpmcp.core.exceptions import WordPressApiError
from wpmcp.core.logging import logger
from wpmcp.wordpress.endpoints import wpmcp_v1, wp_v2

_JSON = "application/json"
_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=60.0, pool=15.0)
_LIMITS = httpx.Limits(max_connections=32, max_keepalive_connections=16)


class WordPressClient:
    """Thin async wrapper over a single WordPress site's REST API.

    Uses one persistent ``httpx.AsyncClient`` per site for keep-alive and
    HTTP/2 multiplexing. Authentication is HTTP Basic with a WordPress
    Application Password.
    """

<<<<<<< HEAD
    def __init__(self, base_url: str, username: str = "", app_password: str | None = None, api_token: str | None = None) -> None:
        if not api_token and not (username and app_password):
            raise ValueError("WordPressClient requires either an api_token or username + app_password.")
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._auth = None if api_token else httpx.BasicAuth(username, app_password)
=======
    def __init__(self, base_url: str, username: str, app_password: str, api_token: str | None = None) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_token = api_token
        self._auth = httpx.BasicAuth(username, app_password) if not api_token else None
>>>>>>> d3b7de4aa03328e99e3e4286158839f805e0de37
        headers = {
            "Accept": _JSON,
            "User-Agent": "WPMCP/1.0 (+remote-mcp)",
        }
        if api_token:
            headers["Authorization"] = f"Bearer {api_token}"
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            auth=self._auth,
            timeout=_TIMEOUT,
            limits=_LIMITS,
            headers=headers,
            follow_redirects=True,
        )

    @property
    def base_url(self) -> str:
        return self._base_url

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        expect_json: bool = True,
    ) -> Any:
        url = path if path.startswith("/wp-json") else f"/wp-json/{path}"
        try:
            response = await self._client.request(
                method,
                url,
                params=params,
                json=json_body,
                files=files,
            )
        except httpx.HTTPError as error:
            raise WordPressApiError(
                f"Transport error contacting WordPress: {error}",
                endpoint=url,
            ) from error

        if response.status_code >= 400:
            self._raise_for_status(response, url)

        if not expect_json:
            return response
        try:
            return response.json()
        except ValueError as error:
            snippet = response.text[:200].replace("\n", " ")
            raise WordPressApiError(
                f"WordPress returned a non-JSON response (HTTP {response.status_code}) for {url}: {snippet!r}",
                status_code=response.status_code,
                endpoint=url,
            ) from error

    @staticmethod
    def _raise_for_status(response: httpx.Response, endpoint: str) -> None:
        message = f"WordPress API error {response.status_code} for {endpoint}"
        try:
            body = response.json()
            if isinstance(body, dict):
                message = body.get("message") or body.get("code") or message
        except ValueError:
            if response.text:
                message = f"{message}: {response.text[:200]}"
        raise WordPressApiError(message, status_code=response.status_code, endpoint=endpoint)

    # --- generic verbs -------------------------------------------------
    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self._request("GET", path, params=params)

    async def post(self, path: str, body: dict[str, Any] | None = None) -> Any:
        return await self._request("POST", path, json_body=body or {})

    async def delete(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self._request("DELETE", path, params=params)

    async def upload(self, path: str, filename: str, content: bytes, mime: str) -> Any:
        return await self._request(
            "POST",
            path,
            files={"file": (filename, content, mime)},
        )

    # --- convenience helpers -------------------------------------------
    async def test_connection(self) -> dict[str, Any]:
        data = await self.get(wp_v2(""))
        return {"url": self._base_url, "name": data.get("name"), "description": data.get("description")}

    async def plugin(self, path: str, *, body: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> Any:
        """Call a companion-plugin endpoint (``wpmcp/v1``)."""

        full = wpmcp_v1(path)
        if body is not None:
            return await self.post(full, body)
        if params is not None:
            return await self.get(full, params)
        return await self.get(full)

    async def core(self, path: str, *, body: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> Any:
        """Call a core WordPress REST endpoint (``wp/v2``)."""

        full = wp_v2(path)
        if body is not None:
            return await self.post(full, body)
        if params is not None:
            return await self.get(full, params)
        return await self.get(full)

    async def core_delete(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self.delete(wp_v2(path), params=params)

    def log(self, action: str, detail: str) -> None:
        logger.info("[%s] %s — %s", self._base_url, action, detail)
