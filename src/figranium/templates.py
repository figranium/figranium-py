"""Figranium v0.20 template catalog clients."""
from typing import Any, Optional
from ._http import HttpClient, AsyncHttpClient, path_id
from .types import RequestOptions

class TemplatesResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def list(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/templates", options=options)

    def search(self, *, limit: int = 12, offset: int = 0, sort: str = "popular",
               category: str = "all", search: str = "", options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/templates", query={
            "limit": limit, "offset": offset, "sort": sort, "category": category, "search": search
        }, options=options)

    def get(self, template_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", f"/api/templates/{path_id(template_id)}", options=options)

    def record_import(self, template_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        """Call after saving the imported task; each instance counts once per template."""
        return self._http.request("POST", f"/api/templates/{path_id(template_id)}/import", options=options)

class AsyncTemplatesResource:
    def __init__(self, http: AsyncHttpClient) -> None:
        self._http = http

    async def list(self, *, options: Optional[RequestOptions] = None) -> Any:
        return await self._http.request("GET", "/api/templates", options=options)

    async def search(self, *, limit: int = 12, offset: int = 0, sort: str = "popular",
                     category: str = "all", search: str = "", options: Optional[RequestOptions] = None) -> Any:
        return await self._http.request("GET", "/api/templates", query={
            "limit": limit, "offset": offset, "sort": sort, "category": category, "search": search
        }, options=options)

    async def get(self, template_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return await self._http.request("GET", f"/api/templates/{path_id(template_id)}", options=options)

    async def record_import(self, template_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return await self._http.request("POST", f"/api/templates/{path_id(template_id)}/import", options=options)
