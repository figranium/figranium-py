<div align="center">
  <img src="https://raw.githubusercontent.com/figranium/figranium-py/main/banner.png" alt="Figranium Banner">
</div>

# Figranium Python SDK

[![PyPI version](https://img.shields.io/pypi/v/figranium-sdk.svg)](https://pypi.org/project/figranium-sdk/)

Official Python SDK for [Figranium](https://github.com/figranium/figranium), the self-hosted browser automation and web scraping platform.

- Synchronous and asynchronous clients
- Type hints and a `py.typed` marker
- API-key and persistent browser-session authentication
- Configurable timeouts, custom `httpx` clients, structured errors, and SSE streams
- Python 3.9+

## Install

```bash
pip install figranium-sdk
```

## Quick start

```python
import os

from figranium import Figranium

with Figranium(
    base_url="http://localhost:11345",
    api_key=os.environ["FIGRANIUM_API_KEY"],
) as figranium:
    tasks = figranium.tasks.list_summaries()["tasks"]
    result = figranium.run_task(
        tasks[0]["id"],
        {
            "variables": {"query": "Python SDK"},
        },
    )

print(result.get("data"))
print(result.get("outcome"))  # success | error | stopped | crashed | anti_bot
```

`base_url` defaults to `http://localhost:11345`. API keys use `Authorization: Bearer` by default. Set `api_key_header="x-api-key"` if your deployment expects that header.

## Create a typed task

```python
from figranium import Figranium, Task, actions, variable

task: Task = {
    "name": "Search and extract",
    "description": "Runs a search and captures visible results",
    "url": "https://example.com",
    "mode": "agent",
    "variables": {"query": {"type": "string", "value": "figranium"}},
    "actions": [
        actions.wait_for("#search"),
        actions.type("#search", variable("query")),
        actions.press("Enter", "#search"),
        actions.wait_for(".results"),
        actions.get_content(".results", "resultText"),
    ],
}

with Figranium(api_key="...") as client:
    saved = client.tasks.save(task)
    result = client.run_task(
        saved["id"],
        {
            "variables": {"query": "browser automation"},
        },
    )
```

`variable("query")` produces Figranium's required `{$query}` syntax. Action helpers generate unique IDs and accept `base={...}` for common fields or a caller-supplied ID. Plain action dictionaries remain supported when every specification field is needed.

CAPTCHA-aware tasks can wait for a challenge and solve it separately:

```python
actions.wait_for_captcha(
    captcha_type="turnstile",
    selector="#challenge",
    timeout=120_000,
    var_name="captchaReady",
)
actions.solve_captcha(captcha_type="turnstile", timeout=120_000)
```

## Async client

Every resource is available through `AsyncFigranium` with the same method names:

```python
from figranium import AsyncFigranium

async with AsyncFigranium(api_key="...") as client:
    result = await client.run_task("task-id", {"variables": {"query": "async Python"}})
```

## Stream executions

Synchronous streams are ordinary iterators:

```python
with Figranium(api_key="...") as client:
    for event in client.executions.stream():
        print(event.get("event"), event["data"])
```

Asynchronous streams are async iterators:

```python
async with AsyncFigranium(api_key="...") as client:
    async for event in client.executions.stream():
        print(event.get("event"), event["data"])
```

Streams remain open unless the server closes them, iteration stops, or an optional stream timeout is supplied with `options={"timeout": 60}`.

## Error handling

```python
from figranium import FigraniumError

try:
    result = client.run_task("missing-task")
except FigraniumError as error:
    print(error.status)  # HTTP status, or 0 for transport failures
    print(error.code)  # e.g. TASK_NOT_FOUND
    print(error.details)  # server-provided diagnostics
    print(error.request_id)  # supplied by the server or proxy, when available
```

Every request accepts an `options` keyword containing `headers` and `timeout`. The client-wide timeout defaults to 30 seconds.

## Session-only administration

Figranium's `/api/settings/*` endpoints require an authenticated session rather than an API key. Set `session=True`, log in through `client.auth.login(...)`, and reuse the same client; `httpx` maintains its cookie jar automatically.

```python
with Figranium(base_url="https://figranium.example", session=True) as admin:
    admin.auth.login("admin@example.com", "password")
    models = admin.settings.get_ai_models()
```

## Custom HTTP clients

Supply an `httpx.Client` or `httpx.AsyncClient` to integrate custom transports, proxies, tracing, or test doubles. The SDK does not close a client supplied by the caller.

```python
import httpx

http_client = httpx.Client(proxy="http://proxy.example:8080")
client = Figranium(api_key="...", http_client=http_client)
```

See [docs/API.md](docs/API.md) for the full method index and [examples](examples/) for complete sync and async examples.

## License

Apache-2.0
