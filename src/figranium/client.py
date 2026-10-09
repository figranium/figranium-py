"""Figranium sync and async API clients."""

from typing import Any, Mapping, Optional

import httpx

from ._async_resources import (
    AsyncCabinetsResource,
    AsyncCapturesResource,
    AsyncExecutionResource,
    AsyncExecutionsResource,
    AsyncHealthResource,
    AsyncSchedulesResource,
    AsyncTasksResource,
)
from ._http import AsyncHttpClient, HttpClient
from ._resources import (
    CabinetsResource,
    CapturesResource,
    ExecutionResource,
    ExecutionsResource,
    HealthResource,
    SchedulesResource,
    TasksResource,
)
from .types import RequestOptions
from .templates import TemplatesResource, AsyncTemplatesResource


def _validate_api_key_header(value: str) -> None:
    if value not in {"authorization", "x-api-key"}:
        raise ValueError("api_key_header must be 'authorization' or 'x-api-key'")


class Figranium:
    """Synchronous Figranium API client."""

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:11345",
        api_key: Optional[str] = None,
        api_key_header: str = "authorization",
        session: bool = False,
        timeout: float = 30.0,
        headers: Optional[Mapping[str, str]] = None,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        _validate_api_key_header(api_key_header)
        if session and api_key is not None:
            raise ValueError("api_key and session authentication are mutually exclusive")
        self._http = HttpClient(
            base_url=base_url,
            timeout=timeout,
            headers=headers,
            api_key=api_key,
            api_key_header=api_key_header,
            client=http_client,
        )
        self.tasks = TasksResource(self._http)
        self.templates = TemplatesResource(self._http)
        self.executions = ExecutionsResource(self._http)
        self.schedules = SchedulesResource(self._http)
        self.captures = CapturesResource(self._http)
        self.cabinets = CabinetsResource(self._http)
        self.execution = ExecutionResource(self._http)
        self.health = HealthResource(self._http)

    def run_task(
        self, task_id: str, input: Optional[Mapping[str, Any]] = None, *, options: Optional[RequestOptions] = None
    ) -> Any:
        return self.tasks.run(task_id, input, options=options)

    def scrape(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self.execution.scrape(input, options=options)

    def agent(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self.execution.agent(input, options=options)

    def headful(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self.execution.headful(input, options=options)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "Figranium":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()


class AsyncFigranium:
    """Asynchronous Figranium API client."""

    def __init__(
        self,
        *,
        base_url: str = "http://localhost:11345",
        api_key: Optional[str] = None,
        api_key_header: str = "authorization",
        session: bool = False,
        timeout: float = 30.0,
        headers: Optional[Mapping[str, str]] = None,
        http_client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        _validate_api_key_header(api_key_header)
        if session and api_key is not None:
            raise ValueError("api_key and session authentication are mutually exclusive")
        self._http = AsyncHttpClient(
            base_url=base_url,
            timeout=timeout,
            headers=headers,
            api_key=api_key,
            api_key_header=api_key_header,
            client=http_client,
        )
        # Endpoint implementations are shared; AsyncHttpClient makes each request awaitable.
        self.tasks = AsyncTasksResource(self._http)  # type: ignore[arg-type]
        self.templates = AsyncTemplatesResource(self._http)
        self.executions = AsyncExecutionsResource(self._http)  # type: ignore[arg-type]
        self.schedules = AsyncSchedulesResource(self._http)  # type: ignore[arg-type]
        self.captures = AsyncCapturesResource(self._http)  # type: ignore[arg-type]
        self.cabinets = AsyncCabinetsResource(self._http)  # type: ignore[arg-type]
        self.execution = AsyncExecutionResource(self._http)  # type: ignore[arg-type]
        self.health = AsyncHealthResource(self._http)  # type: ignore[arg-type]

    async def run_task(
        self, task_id: str, input: Optional[Mapping[str, Any]] = None, *, options: Optional[RequestOptions] = None
    ) -> Any:
        return await self.tasks.run(task_id, input, options=options)

    async def scrape(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return await self.execution.scrape(input, options=options)

    async def agent(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return await self.execution.agent(input, options=options)

    async def headful(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return await self.execution.headful(input, options=options)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> "AsyncFigranium":
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        await self.close()
