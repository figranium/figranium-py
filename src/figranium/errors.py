"""Exceptions raised by the Figranium SDK."""

from typing import Any, Optional

import httpx


class FigraniumError(Exception):
    """A normalized HTTP, timeout, or transport failure."""

    def __init__(
        self,
        message: str,
        *,
        status: int = 0,
        code: Optional[str] = None,
        details: Any = None,
        request_id: Optional[str] = None,
        response: Optional[httpx.Response] = None,
        cause: Optional[BaseException] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.details = details
        self.request_id = request_id
        self.response = response
        if cause is not None:
            self.__cause__ = cause

    @classmethod
    def from_response(cls, response: httpx.Response) -> "FigraniumError":
        request_id = response.headers.get("x-request-id")
        raw = response.text
        body: Any = None
        try:
            parsed = response.json()
            if isinstance(parsed, dict):
                body = parsed
        except ValueError:
            pass
        code = body.get("error") if isinstance(body, dict) and isinstance(body.get("error"), str) else None
        details = body.get("details", body.get("detail")) if isinstance(body, dict) else None
        server_message = body.get("message") if isinstance(body, dict) else None
        message = (
            server_message
            if isinstance(server_message, str)
            else code or raw or (f"Figranium request failed with status {response.status_code}")
        )
        return cls(
            message,
            status=response.status_code,
            code=code,
            details=details,
            request_id=request_id,
            response=response,
        )
