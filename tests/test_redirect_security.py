"""Authenticated redirects must not forward custom API keys through injected HTTPX clients."""

import asyncio

import httpx
import pytest

from figranium import AsyncFigranium, Figranium, FigraniumError


def redirect_transport(seen: list[httpx.Request], status: int = 302) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.host == "api.example":
            return httpx.Response(status, headers={"location": "https://attacker.example/stolen"}, request=request)
        return httpx.Response(200, json={"status": "ok"}, request=request)
    return httpx.MockTransport(handler)


@pytest.mark.parametrize("stream", [False, True])
def test_sync_custom_follow_redirects_client_is_overridden(stream: bool) -> None:
    seen: list[httpx.Request] = []
    with httpx.Client(transport=redirect_transport(seen), follow_redirects=True) as transport:
        client = Figranium(base_url="https://api.example", api_key="test-secret",
                           api_key_header="x-api-key", http_client=transport)
        with pytest.raises(FigraniumError) as captured:
            if stream:
                list(client.executions.stream("run-1"))
            else:
                client.health.check()
    assert captured.value.code == "REDIRECT_NOT_ALLOWED"
    assert captured.value.status == 302
    assert len(seen) == 1
    assert seen[0].headers["x-api-key"] == "test-secret"


@pytest.mark.parametrize("stream", [False, True])
def test_async_custom_follow_redirects_client_is_overridden(stream: bool) -> None:
    async def exercise() -> None:
        seen: list[httpx.Request] = []
        async with httpx.AsyncClient(transport=redirect_transport(seen, 307), follow_redirects=True) as transport:
            client = AsyncFigranium(base_url="https://api.example", api_key="test-secret",
                                    api_key_header="x-api-key", http_client=transport)
            with pytest.raises(FigraniumError) as captured:
                if stream:
                    _ = [event async for event in client.executions.stream("run-1")]
                else:
                    await client.health.check()
        assert captured.value.code == "REDIRECT_NOT_ALLOWED"
        assert captured.value.status == 307
        assert len(seen) == 1
        assert seen[0].headers["x-api-key"] == "test-secret"
    asyncio.run(exercise())
