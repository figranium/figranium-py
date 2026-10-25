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
        events = [event async for event in client.executions.stream("async/run? 1")]

    assert result == {"success": True, "data": [1]}
    assert requests[0].url.raw_path == b"/tasks/task%2Fa/api"
    assert json.loads(requests[0].content) == {"variables": {"query": "books"}}
    assert requests[1].url.path == "/api/executions/stream"
    assert requests[1].url.params["runId"] == "async/run? 1"
    assert events == [{"event": "update", "data": {"status": "done"}, "raw": '{"status":"done"}'}]


def test_async_execution_list_auth_mode_and_full_result() -> None:
    asyncio.run(_exercise_async_execution_routes())


async def _exercise_async_execution_routes() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/result"):
            return httpx.Response(200, json={"result": {"value": 42}}, request=request)
        return httpx.Response(200, json={"executions": []}, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        session = AsyncFigranium(session=True, http_client=http_client)
        await session.executions.list()

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        api_key = AsyncFigranium(api_key="secret", http_client=http_client)
        await api_key.executions.list()
        full = await api_key.executions.get_full_result("run/1")

    assert [r.url.raw_path for r in requests] == [
        b"/api/executions",
        b"/api/executions/list",
        b"/api/executions/run%2F1/result",
    ]
    assert full == {"result": {"value": 42}}



def test_async_task_summaries_choose_auth_route() -> None:
    asyncio.run(_exercise_async_task_summaries())


async def _exercise_async_task_summaries() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/api/tasks":
            return httpx.Response(200, json=[{"id": 7, "name": "Session task"}], request=request)
        return httpx.Response(200, json={"tasks": [{"id": "api", "name": "API task"}]}, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http_client:
        session = AsyncFigranium(session=True, http_client=http_client)
        assert await session.tasks.list_summaries() == {"tasks": [{"id": "7", "name": "Session task"}]}
        api_key = AsyncFigranium(api_key="secret", http_client=http_client)
        assert await api_key.tasks.list_summaries() == {"tasks": [{"id": "api", "name": "API task"}]}

    assert [request.url.path for request in requests] == ["/api/tasks", "/api/tasks/list"]


def test_async_cookie_states_session_csrf() -> None:
    asyncio.run(_exercise_async_cookie_states())


async def _exercise_async_cookie_states() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, json={"ok": True}, request=request)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), cookies={"session": "async"}) as http_client:
        client = AsyncFigranium(session=True, http_client=http_client)
        await client.cookie_states.create("login", {"cookies": [], "origins": []})
        await client.cookie_states.delete("state/1")

    assert [r.method for r in requests] == ["POST", "DELETE"]
    assert requests[1].url.raw_path == b"/api/cookie-states/state%2F1"
    assert all(r.headers.get("x-requested-with") == "XMLHttpRequest" for r in requests)
    assert all("session=async" in r.headers.get("cookie", "") for r in requests)
