"""Asynchronous resource variants sharing the sync resources' endpoint definitions."""

from typing import AsyncIterator, Optional, cast

from ._http import AsyncHttpClient, path_id
from ._resources import (
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



class AsyncCookieStatesResource(CookieStatesResource):
    pass


class AsyncTasksResource(TasksResource):
    pass


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
