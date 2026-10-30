"""Asynchronous resource variants sharing the sync resources' endpoint definitions."""

from typing import Any, AsyncIterator, Optional, cast

from ._http import AsyncHttpClient, path_id
from ._resources import (
    ApiKeysResource,
    CabinetsResource,
    CookieStatesResource,
    CapturesResource,
    ExecutionResource,
    ExecutionsResource,
    HealthResource,
    SchedulesResource,
    TasksResource,
)
from .types import RequestOptions, StreamEvent



class AsyncApiKeysResource(ApiKeysResource):
    pass


class AsyncCookieStatesResource(CookieStatesResource):
    pass


class AsyncTasksResource(TasksResource):
    async def list_summaries(self, *, options: Optional[RequestOptions] = None) -> Any:  # type: ignore[override]
        """Use the session-compatible Task list or the API-key summaries route."""
        http = cast(AsyncHttpClient, self._http)
        if http.session:
            tasks = await http.request("GET", "/api/tasks", options=options)
            return {"tasks": [
                {"id": str(task["id"]), "name": task.get("name") or str(task["id"]),
                 **({"description": task["description"]} if task.get("description") else {})}
                for task in tasks
            ]}
        return await http.request("GET", "/api/tasks/list", options=options)


class AsyncExecutionsResource(ExecutionsResource):
    def stream(self, run_id: str, *, options: Optional[RequestOptions] = None) -> AsyncIterator[StreamEvent]:  # type: ignore[override]
        """Stream events for a run. Requires a workspace session, not an API key."""
        http = cast(AsyncHttpClient, self._http)
        return http.stream(f"/api/executions/stream?runId={path_id(run_id)}", options=options)


class AsyncSchedulesResource(SchedulesResource):
    pass


class AsyncCapturesResource(CapturesResource):
    pass


class AsyncCabinetsResource(CabinetsResource):
    pass




class AsyncExecutionResource(ExecutionResource):
    pass


class AsyncHealthResource(HealthResource):
    pass
