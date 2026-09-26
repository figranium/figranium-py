"""Internal sync and async HTTP transports."""

import json
from typing import Any, AsyncIterator, Iterator, Mapping, Optional, Union
from urllib.parse import quote, urlencode, urlsplit

import httpx

from .errors import FigraniumError
from .types import RequestOptions, StreamEvent

QueryValue = Union[str, int, float, bool, None]


def normalize_base_url(value: str) -> str:
    trimmed = value.strip().rstrip("/")
    if not trimmed:
        raise ValueError("base_url must not be empty")
    parsed = urlsplit(trimmed)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("base_url must use http or https")
    return trimmed


def path_id(value: Union[str, int]) -> str:
    return quote(str(value), safe="")


def _url(base_url: str, path: str, query: Optional[Mapping[str, QueryValue]] = None) -> str:
    result = f"{base_url}/{path.lstrip('/')}"
    values = {
        key: str(value).lower() if isinstance(value, bool) else str(value)
        for key, value in (query or {}).items()
        if value is not None
    }
    return f"{result}?{urlencode(values)}" if values else result


def _parse_event(lines: list[str]) -> Optional[StreamEvent]:
    event: StreamEvent = {}
    data: list[str] = []
    for line in lines:
        if not line or line.startswith(":"):
            continue
        field, separator, value = line.partition(":")
        if separator and value.startswith(" "):
            value = value[1:]
        if field == "data":
            data.append(value)
        elif field == "event":
            event["event"] = value
        elif field == "id":
            event["id"] = value
        elif field == "retry" and value.isdigit():
            event["retry"] = int(value)
    if not data:
        return None
    raw = "\n".join(data)
    event["raw"] = raw
    try:
        event["data"] = json.loads(raw)
    except ValueError:
        event["data"] = raw
    return event


def _request_parts(options: Optional[RequestOptions]) -> tuple[Optional[Mapping[str, str]], Any]:
    value = options or {}
    return value.get("headers"), value.get("timeout")


class HttpClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout: float,
        headers: Optional[Mapping[str, str]],
        api_key: Optional[str],
        api_key_header: str,
        client: Optional[httpx.Client],
    ) -> None:
        self.base_url = normalize_base_url(base_url)
        base_headers = {"accept": "application/json", **(headers or {})}
        if api_key:
            if api_key_header == "x-api-key":
                base_headers["x-api-key"] = api_key
            else:
                base_headers["authorization"] = f"Bearer {api_key}"
        self.timeout = timeout
        self._owns_client = client is None
        self.client = client or httpx.Client(headers=base_headers)
        if client is not None:
            self.client.headers.update(base_headers)

    def request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        query: Optional[Mapping[str, QueryValue]] = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        headers, timeout = _request_parts(options)
        try:
            response = self.client.request(
                method,
                _url(self.base_url, path, query),
                headers=headers,
                timeout=self.timeout if timeout is None else timeout,
                **({"json": body} if body is not None else {}),
            )
        except httpx.TimeoutException as error:
            raise FigraniumError("Figranium request was aborted", code="REQUEST_ABORTED", cause=error) from error
        except httpx.HTTPError as error:
            raise FigraniumError("Unable to reach the Figranium server", code="NETWORK_ERROR", cause=error) from error
        if not response.is_success:
            raise FigraniumError.from_response(response)
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            return response.text

    def stream(self, path: str, *, options: Optional[RequestOptions] = None) -> Iterator[StreamEvent]:
        headers, timeout = _request_parts(options)
        stream_headers = {"accept": "text/event-stream", **(headers or {})}
        try:
            with self.client.stream(
                "GET",
                _url(self.base_url, path),
                headers=stream_headers,
                timeout=None if timeout is None else timeout,
            ) as response:
                if not response.is_success:
                    response.read()
                    raise FigraniumError.from_response(response)
                lines: list[str] = []
                for line in response.iter_lines():
                    if line == "":
                        event = _parse_event(lines)
                        lines = []
                        if event is not None:
                            yield event
                    else:
                        lines.append(line)
                event = _parse_event(lines)
                if event is not None:
                    yield event
        except FigraniumError:
            raise
        except httpx.TimeoutException as error:
            raise FigraniumError("Figranium stream was aborted", code="REQUEST_ABORTED", cause=error) from error
        except httpx.HTTPError as error:
            raise FigraniumError(
                "Unable to stream from the Figranium server", code="NETWORK_ERROR", cause=error
            ) from error

    def close(self) -> None:
        if self._owns_client:
            self.client.close()


class AsyncHttpClient:
    def __init__(
        self,
        *,
        base_url: str,
        timeout: float,
        headers: Optional[Mapping[str, str]],
        api_key: Optional[str],
        api_key_header: str,
        client: Optional[httpx.AsyncClient],
    ) -> None:
        self.base_url = normalize_base_url(base_url)
        base_headers = {"accept": "application/json", **(headers or {})}
        if api_key:
            if api_key_header == "x-api-key":
                base_headers["x-api-key"] = api_key
            else:
                base_headers["authorization"] = f"Bearer {api_key}"
        self.timeout = timeout
        self._owns_client = client is None
        self.client = client or httpx.AsyncClient(headers=base_headers)
        if client is not None:
            self.client.headers.update(base_headers)

    async def request(
        self,
        method: str,
        path: str,
        *,
        body: Any = None,
        query: Optional[Mapping[str, QueryValue]] = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        headers, timeout = _request_parts(options)
        try:
            response = await self.client.request(
                method,
                _url(self.base_url, path, query),
                headers=headers,
                timeout=self.timeout if timeout is None else timeout,
                **({"json": body} if body is not None else {}),
            )
        except httpx.TimeoutException as error:
            raise FigraniumError("Figranium request was aborted", code="REQUEST_ABORTED", cause=error) from error
        except httpx.HTTPError as error:
            raise FigraniumError("Unable to reach the Figranium server", code="NETWORK_ERROR", cause=error) from error
        if not response.is_success:
            raise FigraniumError.from_response(response)
        if response.status_code == 204 or not response.content:
            return None
        try:
            return response.json()
        except ValueError:
            return response.text

    async def stream(self, path: str, *, options: Optional[RequestOptions] = None) -> AsyncIterator[StreamEvent]:
        headers, timeout = _request_parts(options)
        stream_headers = {"accept": "text/event-stream", **(headers or {})}
        try:
            async with self.client.stream(
                "GET",
                _url(self.base_url, path),
                headers=stream_headers,
                timeout=None if timeout is None else timeout,
            ) as response:
                if not response.is_success:
                    await response.aread()
                    raise FigraniumError.from_response(response)
                lines: list[str] = []
                async for line in response.aiter_lines():
                    if line == "":
                        event = _parse_event(lines)
                        lines = []
                        if event is not None:
                            yield event
                    else:
                        lines.append(line)
                event = _parse_event(lines)
                if event is not None:
                    yield event
        except FigraniumError:
            raise
        except httpx.TimeoutException as error:
            raise FigraniumError("Figranium stream was aborted", code="REQUEST_ABORTED", cause=error) from error
        except httpx.HTTPError as error:
            raise FigraniumError(
                "Unable to stream from the Figranium server", code="NETWORK_ERROR", cause=error
            ) from error

    async def close(self) -> None:
        if self._owns_client:
            await self.client.aclose()
