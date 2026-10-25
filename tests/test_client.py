import json
import re
from typing import Dict, Optional

import httpx
import pytest

from figranium import Figranium, FigraniumError, action, actions, variable


def response(
    request: httpx.Request,
    body: object,
    status: int = 200,
    headers: Optional[Dict[str, str]] = None,
) -> httpx.Response:
    return httpx.Response(status, json=body, headers=headers, request=request)


def test_normalizes_urls_and_sends_bearer_authentication() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return response(request, {"tasks": []})

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as http_client:
        client = Figranium(base_url="https://figranium.example///", api_key="secret", http_client=http_client)
        client.tasks.list_summaries()

    assert str(requests[0].url) == "https://figranium.example/api/tasks/list"
    assert requests[0].headers["authorization"] == "Bearer secret"


def test_supports_x_api_key_authentication() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return response(request, {"status": "ok"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        Figranium(api_key="secret", api_key_header="x-api-key", http_client=http_client).health.check()

    assert requests[0].headers["x-api-key"] == "secret"


def test_serializes_execution_input_and_encodes_path_parameters() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return response(request, {"success": True, "outcome": "anti_bot", "data": [1]})

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = Figranium(api_key="secret", http_client=http_client)
        result = client.run_task("task/a", {"variables": {"query": "books"}, "runId": "run-1"})

    assert requests[0].url.raw_path == b"/tasks/task%2Fa/api"
    assert json.loads(requests[0].content) == {"variables": {"query": "books"}, "runId": "run-1"}
    assert result["data"] == [1]
    assert result["outcome"] == "anti_bot"


def test_preserves_server_diagnostics() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return response(
            request,
            {"error": "TASK_NOT_FOUND", "message": "No such task", "details": {"id": "x"}},
            status=404,
            headers={"x-request-id": "req-1"},
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = Figranium(api_key="secret", http_client=http_client)
        with pytest.raises(FigraniumError) as captured:
            client.run_task("x")

    error = captured.value
    assert error.status == 404
    assert error.code == "TASK_NOT_FOUND"
    assert error.request_id == "req-1"
    assert error.details == {"id": "x"}


def test_normalizes_timeout_errors() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = Figranium(api_key="secret", http_client=http_client)
        with pytest.raises(FigraniumError, match="aborted") as captured:
            client.health.check()

    assert captured.value.code == "REQUEST_ABORTED"


def test_parses_json_sse_multiline_text_and_metadata() -> None:
    body = 'id: one\\nevent: execution\\ndata: {"status":"running"}\\n\\ndata: hello\\ndata: world\\nretry: 2500\\n\\n'
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(200, text=body, headers={"content-type": "text/event-stream"}, request=request)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        events = list(Figranium(session=True, http_client=http_client).executions.stream("run/1? x"))

    assert requests[0].url.path == "/api/executions/stream"
    assert requests[0].url.params["runId"] == "run/1? x"

    assert events == [
        {"data": {"status": "running"}, "raw": '{"status":"running"}', "event": "execution", "id": "one"},
        {"data": "hello\nworld", "raw": "hello\nworld", "retry": 2500},
    ]


def test_routes_representative_resource_calls() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return response(request, {"success": True})

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = Figranium(api_key="secret", http_client=http_client)
        client.tasks.update("task 1", {"name": "Updated"})
        client.executions.stop("run-1")
        client.schedules.delete("task 1")
        client.captures.delete("recording.webm")

    assert [(request.method, str(request.url)) for request in requests] == [
        ("PATCH", "http://localhost:11345/api/tasks/task%201"),
        ("POST", "http://localhost:11345/api/executions/stop"),
        ("DELETE", "http://localhost:11345/api/schedules/task%201"),
        ("DELETE", "http://localhost:11345/api/data/captures/recording.webm"),
    ]


def test_action_helpers() -> None:
    step = actions.type("#query", variable("search.query"))
    assert step["type"] == "type"
    assert step["selector"] == "#query"
    assert step["value"] == "{$search.query}"
    assert step["typeMode"] == "replace"
    assert re.match(r"^act_type_", step["id"])
    assert actions.click("#submit", base={"id": "submit"})["id"] == "submit"
    assert actions.wait_for_captcha(
        captcha_type="turnstile",
        selector="#challenge",
        timeout=120_000,
        var_name="captchaReady",
        base={"id": "wait-captcha"},
    ) == {
        "id": "wait-captcha",
        "type": "wait_captcha",
        "captchaType": "turnstile",
        "selector": "#challenge",
        "timeout": 120_000,
        "varName": "captchaReady",
    }
    assert action({"type": "click", "selector": "body"})["id"].startswith("act_click_")


def test_validates_configuration_and_variables() -> None:
    with pytest.raises(ValueError, match="http or https"):
        Figranium(base_url="file:///tmp/server")
    with pytest.raises(ValueError, match="mutually exclusive"):
        Figranium(api_key="secret", session=True)
    with pytest.raises(ValueError, match="must not be empty"):
        variable("   ")


def test_v021_task_cookie_state_and_baserow_output() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return response(request, {"id": "task_1"})

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        client = Figranium(api_key="secret", http_client=http_client)
        client.tasks.save({"name": "Task", "url": "https://example.com", "mode": "agent", "cookieStateId": "state_login", "output": {"provider": "baserow", "credentialId": "cred_1", "databaseId": "12", "tableId": "34", "dedicated": True, "onError": "fail"}})
        client.tasks.update("task_1", {"cookieStateId": None})

    assert json.loads(requests[0].content)["cookieStateId"] == "state_login"
    assert json.loads(requests[0].content)["output"]["dedicated"] is True
    assert json.loads(requests[1].content)["cookieStateId"] is None


def test_v021_cookie_states_and_session_csrf_headers() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return response(request, {"ok": True})

    state = {"cookies": [], "origins": []}
    with httpx.Client(transport=httpx.MockTransport(handler), cookies={"session": "example"}) as http_client:
        client = Figranium(session=True, http_client=http_client)
        client.cookie_states.list()
        client.cookie_states.get("state/1")
        client.cookie_states.create("login", state)
        client.cookie_states.rename("state/1", "renamed")
        client.cookie_states.update("state/1", state)
        client.cookie_states.delete("state/1")

    assert [(r.method, r.url.raw_path) for r in requests] == [
        ("GET", b"/api/cookie-states"),
        ("GET", b"/api/cookie-states/state%2F1"),
        ("POST", b"/api/cookie-states"),
        ("PATCH", b"/api/cookie-states/state%2F1"),
        ("PATCH", b"/api/cookie-states/state%2F1"),
        ("DELETE", b"/api/cookie-states/state%2F1"),
    ]
    assert "x-requested-with" not in requests[0].headers
    assert all(r.headers.get("x-requested-with") == "XMLHttpRequest" for r in requests[2:])
    assert all("session=example" in r.headers.get("cookie", "") for r in requests)
    assert json.loads(requests[2].content) == {"name": "login", "state": state}
    assert json.loads(requests[4].content) == {"state": state}


def test_session_csrf_respects_origin_and_api_key_mode() -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return response(request, {"ok": True})

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        Figranium(session=True, headers={"Origin": "https://example.test"}, http_client=http_client).tasks.update("1", {"name": "x"})
        Figranium(api_key="key", http_client=http_client).tasks.update("1", {"name": "x"})

    assert requests[0].headers["origin"] == "https://example.test"
    assert "x-requested-with" not in requests[0].headers
    assert "x-requested-with" not in requests[1].headers
