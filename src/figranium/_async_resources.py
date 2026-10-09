"""Asynchronous resource variants sharing the sync resources' endpoint definitions."""

from typing import AsyncIterator, Optional, cast

from ._http import AsyncHttpClient
from ._resources import (
    CabinetsResource,
    CapturesResource,
    ExecutionResource,
    ExecutionsResource,
    HealthResource,
    SchedulesResource,
    TasksResource,
)
from .types import RequestOptions, StreamEvent



class AsyncTasksResource(TasksResource):
    pass


class AsyncExecutionsResource(ExecutionsResource):
    def stream(self, *, options: Optional[RequestOptions] = None) -> AsyncIterator[StreamEvent]:  # type: ignore[override]
        http = cast(AsyncHttpClient, self._http)
        return http.stream("/api/executions/stream", options=options)


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
