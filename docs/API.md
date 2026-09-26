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

- `executions.list(api_key_route=True)`
- `executions.get(execution_id)`
- `executions.delete(execution_id)`
- `executions.clear()`
- `executions.stop(run_id)`
- `executions.stream()`

## Schedules

- `schedules.list()`
- `schedules.set(task_id, schedule)`
- `schedules.delete(task_id)`
- `schedules.status(task_id)`
- `schedules.describe(task_id, schedule)`
- `schedules.overall_status()`

## Captures and cookies

- `captures.list(run_id=None)`
- `captures.screenshots()`
- `captures.delete(name)`
- `captures.cookies()`
- `captures.delete_cookie(name, domain=None, path=None)`
- `captures.clear()`
- `captures.clear_cookies()`

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

## Credentials

- `credentials.list()`
- `credentials.create(input)`
- `credentials.update(credential_id, input)`
- `credentials.delete(credential_id)`
- `credentials.baserow_databases(credential_id)`
- `credentials.baserow_tables(credential_id, database_id)`

## Browser and headful sessions

- `browser.open(input=None)`
- `browser.highlight(input)`
- `browser.stop_headful()`
- `browser.headful_status()`
- `browser.inspect()`
- `browser.vnc_password()`
- `browser.selector_stream()`

## Settings (session required)

- `settings.get_api_key()` / `settings.set_api_key(api_key=None)`
- `settings.get_user_agent()` / `settings.set_user_agent(selection)`
- `settings.get_ai_models()` / `settings.set_ai_models(models)`
- `settings.get_provider_keys(provider)` / `settings.set_provider_keys(provider, keys)`
- `settings.get_theme()` / `settings.set_theme(theme)`
- `settings.list_proxies()`
- `settings.add_proxy(proxy)` / `settings.import_proxies(proxies)`
- `settings.update_proxy(proxy_id, proxy)`
- `settings.delete_proxy(proxy_id)` / `settings.delete_proxies(ids)`
- `settings.set_default_proxy(proxy_id)`
- `settings.set_proxy_rotation(input)`

## Authentication and health

- `auth.check_setup()`
- `auth.setup(name, email, password)`
- `auth.login(email, password)`
- `auth.logout()`
- `auth.me()`
- `health.check()`

## Helpers

- `variable(name)` creates a `{$name}` template token.
- `action(input)` adds an action ID to a valid action mapping.
- `actions` provides navigation, interaction, extraction, control-flow, HTTP, upload, and CAPTCHA helpers.
- `FigraniumError` normalizes HTTP, timeout, and transport failures.

