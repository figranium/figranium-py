# API method index

Methods on `Figranium` return immediately. Methods on `AsyncFigranium` are awaited. Stream methods return a synchronous or asynchronous iterator respectively. Every request accepts `options={"headers": ..., "timeout": ...}`.

## Top level

- `run_task(task_id, input=None)`
- `scrape(input)`
- `agent(input)`
- `headful(input)`
- `close()`

Classified execution outcomes (`success`, `error`, `stopped`, `crashed`, and `anti_bot`) are completed responses. Inspect `result["outcome"]` rather than relying only on HTTP status.

## Tasks

- `tasks.list()`
- `tasks.list_summaries()`
- `tasks.save(task, create_version=False)`
- `tasks.touch(task_id)`
- `tasks.update(task_id, patch)`
- `tasks.delete(task_id)`
- `tasks.versions(task_id)`
- `tasks.version(task_id, version_id)`
- `tasks.clear_versions(task_id)`
- `tasks.rollback(task_id, version_id)`
- `tasks.generate_selector(task, action_index, prompt)`
- `tasks.generate_script(description)`
- `tasks.run(task_id, input=None)`

## Executions

- `executions.list(api_key_route=None)` — automatically selects the workspace-session route or the API-key route; pass `True` or `False` to override
- `executions.get(execution_id)`
- `executions.get_full_result(execution_id)` — returns `{ "result": ... }` when a complete result was retained; API keys require `results:read` and access to the execution's Task
- `executions.delete(execution_id)`
- `executions.clear()`
- `executions.stop(run_id)`
- `executions.stream(run_id)` — stream events for a run via `/api/executions/stream?runId=...`; requires workspace-session authentication (not an API key). Available on both sync and async clients.

## Schedules

- `schedules.list()`
- `schedules.set(task_id, schedule)`
- `schedules.delete(task_id)`
- `schedules.status(task_id)`
- `schedules.describe(task_id, schedule)`
- `schedules.overall_status()`

## Captures

- `captures.list(run_id=None)`
- `captures.screenshots()`
- `captures.delete(name)`
- `captures.clear()`

## Cabinets

- `cabinets.list()`
- `cabinets.create(name)`
- `cabinets.rename(cabinet_id, name)`
- `cabinets.delete(cabinet_id, target_cabinet_id=None, migrate=False)`
- `cabinets.list_items(cabinet_id)`
- `cabinets.clear(cabinet_id)`
- `cabinets.set_item_status(cabinet_id, item_ids, status)`
- `cabinets.remove_items(cabinet_id, item_ids)`
- `cabinets.zip_items(cabinet_id, item_ids, name=None)`
- `cabinets.unzip_item(cabinet_id, item_id)`
- `cabinets.get_item_download_url(cabinet_id, item_id)`

## Named cookie states (workspace session only)

- `cookie_states.list()`
- `cookie_states.get(state_id)`
- `cookie_states.create(name, state)`
- `cookie_states.rename(state_id, name)`
- `cookie_states.update(state_id, state)`
- `cookie_states.delete(state_id)`

Use `Figranium(session=True, http_client=...)` with an authenticated `httpx.Client` containing the workspace session cookie, or `AsyncFigranium` with an authenticated `httpx.AsyncClient`. The SDK does not log in or obtain a session cookie. It adds the server's CSRF hint to session-authenticated mutations without an explicit Origin/Referer.

Scoped API keys are intended for permitted automation operations; they cannot administer named cookie states, 1Password credentials, connections, Baserow credentials, import/export, or Cloud authentication. Manage those in the workspace UI.

## Health

- `health.check()`

## Helpers

- `variable(name)` creates a `{$name}` template token.
- `action(input)` adds an action ID to a valid action mapping.
- `actions` provides navigation, interaction, extraction, control-flow, HTTP, upload, and CAPTCHA helpers.
- `FigraniumError` normalizes HTTP, timeout, and transport failures.

