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
    body = 'id: one\nevent: execution\ndata: {"status":"running"}\n\ndata: hello\ndata: world\nretry: 2500\n\n'

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=body, headers={"content-type": "text/event-stream"}, request=request)

    with httpx.Client(transport=httpx.MockTransport(handler)) as http_client:
        events = list(Figranium(api_key="secret", http_client=http_client).executions.stream())

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
        client.credentials.baserow_tables("cred/1", 42)
        client.browser.inspect()

    assert [(request.method, str(request.url)) for request in requests] == [
        ("PATCH", "http://localhost:11345/api/tasks/task%201"),
        ("POST", "http://localhost:11345/api/executions/stop"),
        ("DELETE", "http://localhost:11345/api/schedules/task%201"),
        ("DELETE", "http://localhost:11345/api/data/captures/recording.webm"),
        ("GET", "http://localhost:11345/api/credentials/cred%2F1/proxy/baserow/databases/42/tables"),
        ("POST", "http://localhost:11345/api/headful/inspect"),
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
