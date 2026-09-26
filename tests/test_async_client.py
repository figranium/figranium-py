import asyncio
import json

import httpx

from figranium import AsyncFigranium


def test_async_client_request_and_stream() -> None:
    asyncio.run(_exercise_async_client())


async def _exercise_async_client() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/stream"):
            return httpx.Response(200, text='event: update\ndata: {"status":"done"}\n\n', request=request)
        return httpx.Response(200, json={"success": True, "data": [1]}, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        client = AsyncFigranium(api_key="secret", http_client=http_client)
        result = await client.run_task("task/a", {"variables": {"query": "books"}})
        events = [event async for event in client.executions.stream()]

    assert result == {"success": True, "data": [1]}
    assert requests[0].url.raw_path == b"/tasks/task%2Fa/api"
    assert json.loads(requests[0].content) == {"variables": {"query": "books"}}
    assert events == [{"event": "update", "data": {"status": "done"}, "raw": '{"status":"done"}'}]
