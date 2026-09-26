"""Synchronous API resources."""

from typing import Any, Dict, Iterator, Mapping, Optional, Sequence, Union

from ._http import HttpClient, path_id
from .types import AiModels, AiProvider, CabinetItemStatus, RequestOptions, Schedule, StreamEvent, Theme


def _defined(**values: Any) -> Dict[str, Any]:
    return {key: value for key, value in values.items() if value is not None}


class Resource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http


class AuthResource(Resource):
    def check_setup(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/auth/check-setup", options=options)

    def setup(self, name: str, email: str, password: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request(
            "POST", "/api/auth/setup", body={"name": name, "email": email, "password": password}, options=options
        )

    def login(self, email: str, password: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request(
            "POST", "/api/auth/login", body={"email": email, "password": password}, options=options
        )

    def logout(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/auth/logout", options=options)

    def me(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/auth/me", options=options)


class TasksResource(Resource):
    def list(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/tasks", options=options)

    def list_summaries(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/tasks/list", options=options)

    def save(
        self, task: Mapping[str, Any], *, create_version: bool = False, options: Optional[RequestOptions] = None
    ) -> Any:
        return self._http.request(
            "POST",
            "/api/tasks",
            query={"version": "true" if create_version else None},
            body=dict(task),
            options=options,
        )

    def touch(self, task_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", f"/api/tasks/{path_id(task_id)}/touch", options=options)

    def update(self, task_id: str, patch: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("PATCH", f"/api/tasks/{path_id(task_id)}", body=dict(patch), options=options)

    def delete(self, task_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("DELETE", f"/api/tasks/{path_id(task_id)}", options=options)

    def versions(self, task_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", f"/api/tasks/{path_id(task_id)}/versions", options=options)

    def version(self, task_id: str, version_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request(
            "GET", f"/api/tasks/{path_id(task_id)}/versions/{path_id(version_id)}", options=options
        )

    def clear_versions(self, task_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", f"/api/tasks/{path_id(task_id)}/versions/clear", options=options)

    def rollback(self, task_id: str, version_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request(
            "POST", f"/api/tasks/{path_id(task_id)}/rollback", body={"versionId": version_id}, options=options
        )

    def generate_selector(
        self, task: Mapping[str, Any], action_index: int, prompt: str, *, options: Optional[RequestOptions] = None
    ) -> Any:
        body = {"task": dict(task), "actionIndex": action_index, "prompt": prompt}
        return self._http.request("POST", "/api/tasks/generate-selector", body=body, options=options)

    def generate_script(self, description: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request(
            "POST", "/api/tasks/generate-script", body={"description": description}, options=options
        )

    def run(
        self, task_id: str, input: Optional[Mapping[str, Any]] = None, *, options: Optional[RequestOptions] = None
    ) -> Any:
        return self._http.request("POST", f"/tasks/{path_id(task_id)}/api", body=dict(input or {}), options=options)


class ExecutionsResource(Resource):
    def list(self, *, api_key_route: bool = True, options: Optional[RequestOptions] = None) -> Any:
        path = "/api/executions/list" if api_key_route else "/api/executions"
        return self._http.request("GET", path, options=options)

    def get(self, execution_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", f"/api/executions/{path_id(execution_id)}", options=options)

    def delete(self, execution_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("DELETE", f"/api/executions/{path_id(execution_id)}", options=options)

    def clear(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/executions/clear", options=options)

    def stop(self, run_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/executions/stop", body={"runId": run_id}, options=options)

    def stream(self, *, options: Optional[RequestOptions] = None) -> Iterator[StreamEvent]:
        return self._http.stream("/api/executions/stream", options=options)


class SchedulesResource(Resource):
    def list(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/schedules", options=options)

    def set(self, task_id: str, schedule: Schedule, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", f"/api/schedules/{path_id(task_id)}", body=schedule, options=options)

    def delete(self, task_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("DELETE", f"/api/schedules/{path_id(task_id)}", options=options)

    def status(self, task_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", f"/api/schedules/{path_id(task_id)}/status", options=options)

    def describe(self, task_id: str, schedule: Schedule, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", f"/api/schedules/{path_id(task_id)}/describe", body=schedule, options=options)

    def overall_status(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/schedules/status/all", options=options)


class CapturesResource(Resource):
    def list(self, *, run_id: Optional[str] = None, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/data/captures", query={"runId": run_id}, options=options)

    def screenshots(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/data/screenshots", options=options)

    def delete(self, name: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("DELETE", f"/api/data/captures/{path_id(name)}", options=options)

    def cookies(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/data/cookies", options=options)

    def delete_cookie(
        self,
        name: str,
        *,
        domain: Optional[str] = None,
        path: Optional[str] = None,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        return self._http.request(
            "POST", "/api/data/cookies/delete", body=_defined(name=name, domain=domain, path=path), options=options
        )

    def clear(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/data/clear-screenshots", options=options)

    def clear_cookies(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/data/clear-cookies", options=options)


class CabinetsResource(Resource):
    def list(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/cabinets", options=options)

    def create(self, name: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/cabinets", body={"name": name}, options=options)

    def rename(self, cabinet_id: str, name: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("PATCH", f"/api/cabinets/{path_id(cabinet_id)}", body={"name": name}, options=options)

    def delete(
        self,
        cabinet_id: str,
        *,
        target_cabinet_id: Optional[str] = None,
        migrate: bool = False,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        body = _defined(targetCabinetId=target_cabinet_id, mode="migrate" if migrate else None)
        return self._http.request("DELETE", f"/api/cabinets/{path_id(cabinet_id)}", body=body, options=options)

    def list_items(self, cabinet_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", f"/api/cabinets/{path_id(cabinet_id)}/items", options=options)

    def clear(self, cabinet_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", f"/api/cabinets/{path_id(cabinet_id)}/clear", options=options)

    def set_item_status(
        self,
        cabinet_id: str,
        item_ids: Sequence[str],
        status: CabinetItemStatus,
        *,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        return self._http.request(
            "PATCH",
            f"/api/cabinets/{path_id(cabinet_id)}/items/status",
            body={"itemIds": list(item_ids), "status": status},
            options=options,
        )

    def remove_items(
        self, cabinet_id: str, item_ids: Sequence[str], *, options: Optional[RequestOptions] = None
    ) -> Any:
        return self._http.request(
            "DELETE", f"/api/cabinets/{path_id(cabinet_id)}/items", body={"itemIds": list(item_ids)}, options=options
        )

    def zip_items(
        self,
        cabinet_id: str,
        item_ids: Sequence[str],
        name: Optional[str] = None,
        *,
        options: Optional[RequestOptions] = None,
    ) -> Any:
        body = {"itemIds": list(item_ids), **_defined(name=name)}
        return self._http.request("POST", f"/api/cabinets/{path_id(cabinet_id)}/zip", body=body, options=options)

    def unzip_item(self, cabinet_id: str, item_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request(
            "POST", f"/api/cabinets/{path_id(cabinet_id)}/items/{path_id(item_id)}/unzip", options=options
        )

    def get_item_download_url(self, cabinet_id: str, item_id: str) -> str:
        return f"{self._http.base_url}/api/cabinets/{path_id(cabinet_id)}/items/{path_id(item_id)}/download"


class CredentialsResource(Resource):
    def list(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/credentials", options=options)

    def create(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/credentials", body=dict(input), options=options)

    def update(self, credential_id: str, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request(
            "PUT", f"/api/credentials/{path_id(credential_id)}", body=dict(input), options=options
        )

    def delete(self, credential_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("DELETE", f"/api/credentials/{path_id(credential_id)}", options=options)

    def baserow_databases(self, credential_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request(
            "GET", f"/api/credentials/{path_id(credential_id)}/proxy/baserow/databases", options=options
        )

    def baserow_tables(
        self, credential_id: str, database_id: Union[str, int], *, options: Optional[RequestOptions] = None
    ) -> Any:
        path = f"/api/credentials/{path_id(credential_id)}/proxy/baserow/databases/{path_id(database_id)}/tables"
        return self._http.request("GET", path, options=options)


class BrowserResource(Resource):
    def open(self, input: Optional[Mapping[str, Any]] = None, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/browser/open", body=dict(input or {}), options=options)

    def highlight(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/inspector/highlight", body=dict(input), options=options)

    def stop_headful(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/headful/stop", options=options)

    def headful_status(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/headful/status", options=options)

    def inspect(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/headful/inspect", options=options)

    def vnc_password(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/headful/vnc-password", options=options)

    def selector_stream(self, *, options: Optional[RequestOptions] = None) -> Iterator[StreamEvent]:
        return self._http.stream("/api/headful/selector_stream", options=options)


class SettingsResource(Resource):
    def get_api_key(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/settings/api-key", options=options)

    def set_api_key(self, api_key: Optional[str] = None, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/settings/api-key", body=_defined(apiKey=api_key), options=options)

    def get_user_agent(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/settings/user-agent", options=options)

    def set_user_agent(self, selection: Optional[str], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/settings/user-agent", body={"selection": selection}, options=options)

    def get_ai_models(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/settings/ai-models", options=options)

    def set_ai_models(self, models: AiModels, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/settings/ai-models", body=models, options=options)

    def get_theme(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/settings/theme", options=options)

    def set_theme(self, theme: Theme, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/settings/theme", body={"theme": theme}, options=options)

    def list_proxies(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/settings/proxies", options=options)

    def add_proxy(self, proxy: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/settings/proxies", body=dict(proxy), options=options)

    def import_proxies(self, proxies: Sequence[Mapping[str, Any]], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request(
            "POST", "/api/settings/proxies/import", body={"proxies": list(proxies)}, options=options
        )

    def update_proxy(self, proxy_id: str, proxy: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request(
            "PUT", f"/api/settings/proxies/{path_id(proxy_id)}", body=dict(proxy), options=options
        )

    def delete_proxy(self, proxy_id: str, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("DELETE", f"/api/settings/proxies/{path_id(proxy_id)}", options=options)

    def delete_proxies(self, ids: Sequence[str], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("DELETE", "/api/settings/proxies", body={"ids": list(ids)}, options=options)

    def set_default_proxy(self, proxy_id: Optional[str], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/settings/proxies/default", body={"id": proxy_id}, options=options)

    def set_proxy_rotation(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/api/settings/proxies/rotation", body=dict(input), options=options)

    def get_provider_keys(self, provider: AiProvider, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", f"/api/settings/{_provider_path(provider)}", options=options)

    def set_provider_keys(
        self, provider: AiProvider, keys: Sequence[str], *, options: Optional[RequestOptions] = None
    ) -> Any:
        response_key = "openAiApiKeys" if provider == "openai" else f"{provider}ApiKeys"
        return self._http.request(
            "POST", f"/api/settings/{_provider_path(provider)}", body={response_key: list(keys)}, options=options
        )


def _provider_path(provider: AiProvider) -> str:
    return "openai-api-key" if provider == "openai" else f"{provider}-api-key"


class ExecutionResource(Resource):
    def scrape(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/scrape", body=dict(input), options=options)

    def agent(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/agent", body=dict(input), options=options)

    def headful(self, input: Mapping[str, Any], *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("POST", "/headful", body=dict(input), options=options)


class HealthResource(Resource):
    def check(self, *, options: Optional[RequestOptions] = None) -> Any:
        return self._http.request("GET", "/api/health", options=options)
