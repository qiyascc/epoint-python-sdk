from __future__ import annotations

from typing import Any, Optional


class EpointError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConfigurationError(EpointError):
    pass


class InvalidRequestError(EpointError, ValueError):
    pass


class SignatureError(EpointError):
    pass


class TransportError(EpointError):
    def __init__(self, message: str, *, path: str = "", order_id: Optional[str] = None) -> None:
        super().__init__(message)
        self.path = path
        self.order_id = order_id


class NotSentError(TransportError):
    pass


class OutcomeUnknownError(TransportError):
    def __init__(self, message: str, *, status_code: Optional[int] = None, **kwargs: Any) -> None:
        super().__init__(message, **kwargs)
        self.status_code = status_code


class HTTPStatusError(EpointError):
    def __init__(self, message: str, *, status_code: int, body: Any = None, path: str = "") -> None:
        super().__init__(message)
        self.status_code = status_code
        self.body = body
        self.path = path


class GatewayError(EpointError):
    def __init__(
        self,
        message: str,
        *,
        code: Optional[str] = None,
        trace_id: Optional[str] = None,
        status_code: int = 200,
        payload: Optional[dict[str, Any]] = None,
        path: str = "",
    ) -> None:
        super().__init__(message)
        self.code = code
        self.trace_id = trace_id
        self.status_code = status_code
        self.payload = payload or {}
        self.path = path

    def __str__(self) -> str:
        parts = [self.message]
        if self.code:
            parts.insert(0, f"[{self.code}]")
        if self.trace_id:
            parts.append(f"(trace {self.trace_id})")
        return " ".join(parts)
