from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Optional, TypeVar

import httpx

from . import signing
from .config import Settings, load_settings
from .enums import Status
from .errors import GatewayError, HTTPStatusError, NotSentError, OutcomeUnknownError, TransportError
from .messages import text

T = TypeVar("T")

NOT_SENT = (httpx.ConnectError, httpx.ConnectTimeout, httpx.PoolTimeout, httpx.UnsupportedProtocol)
RETRY_STATUSES = frozenset({429, 500, 502, 503, 504})


@dataclass
class Op:
    endpoint: str
    payload: Optional[dict[str, Any]] = None
    parse: Callable[[Any], Any] = lambda body: body
    safe: bool = False
    method: str = "POST"
    signed: bool = True
    json_body: bool = False
    path_params: Mapping[str, Any] = field(default_factory=dict)
    payment_state: bool = False
    order_id: Optional[str] = None


def clean(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if value is not None and value != ""}


class Outcome:
    def __init__(self, value: Any = None, error: Optional[Exception] = None, retry: bool = False) -> None:
        self.value = value
        self.error = error
        self.retry = retry


class Engine:
    def __init__(
        self,
        public_key: Optional[str] = None,
        private_key: Optional[str] = None,
        *,
        settings: Optional[Settings] = None,
        config_file: Optional[str] = None,
        **overrides: Any,
    ) -> None:
        if settings is None:
            settings = load_settings(config_file, public_key=public_key, private_key=private_key, **overrides)
        elif public_key or private_key or overrides:
            changes = {k: v for k, v in dict(overrides, public_key=public_key, private_key=private_key).items()
                       if v is not None}
            current = settings.model_dump()
            current["private_key"] = settings.private_key.get_secret_value()
            settings = load_settings(None, **{**current, **changes})
        self.settings = settings
        settings.check_transport()
        self.public_key, self._private_key = settings.keys()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(public_key={self.public_key!r}, base_url={self.settings.base_url!r})"

    def _timeout(self) -> httpx.Timeout:
        return httpx.Timeout(self.settings.timeout, connect=self.settings.connect_timeout)

    def _headers(self) -> dict[str, str]:
        return {"Accept": "application/json", "User-Agent": self.settings.resolved_user_agent()}

    def sign(self, payload: Mapping[str, Any]) -> dict[str, str]:
        body = {"public_key": self.public_key, **clean(payload)}
        data = signing.encode(body)
        return {"data": data, "signature": signing.sign(self._private_key, data)}

    def _request_args(self, op: Op) -> dict[str, Any]:
        args: dict[str, Any] = {"headers": self._headers()}
        if op.method == "POST":
            body = self.sign(op.payload or {}) if op.signed else clean(op.payload or {})
            args["json" if op.json_body else "data"] = body
        return args

    def _wait(self, attempt: int) -> float:
        base = self.settings.backoff_base
        return min(self.settings.backoff_cap, base * (2 ** attempt)) + random.uniform(0, base / 2)

    def _on_exception(self, op: Op, exc: Exception, attempt: int) -> Outcome:
        path = self.settings.url(op.endpoint, **op.path_params)
        if isinstance(exc, NOT_SENT):
            if attempt < self.settings.max_retries:
                return Outcome(retry=True)
            return Outcome(error=NotSentError(text("error.connect", error=exc), path=path, order_id=op.order_id))
        if op.safe:
            if attempt < self.settings.max_retries:
                return Outcome(retry=True)
            return Outcome(error=TransportError(text("error.timeout", error=exc), path=path, order_id=op.order_id))
        return Outcome(error=OutcomeUnknownError(text("error.unknown_outcome", reason=type(exc).__name__), path=path,
                                                 order_id=op.order_id))

    def _on_response(self, op: Op, response: httpx.Response, attempt: int) -> Outcome:
        path = self.settings.url(op.endpoint, **op.path_params)
        status = response.status_code
        if status in RETRY_STATUSES and (op.safe or status == 429) and attempt < self.settings.max_retries:
            return Outcome(retry=True)
        if status >= 500 and not op.safe:
            return Outcome(error=OutcomeUnknownError(text("error.unknown_outcome", reason=f"HTTP {status}"),
                                                     status_code=status, path=path, order_id=op.order_id))
        try:
            body = response.json()
        except ValueError:
            snippet = response.text[:200]
            if status < 400 and not op.safe:
                return Outcome(error=OutcomeUnknownError(text("error.body", body=snippet), status_code=status,
                                                         path=path, order_id=op.order_id))
            return Outcome(error=HTTPStatusError(text("error.body", body=snippet), status_code=status, body=snippet,
                                                 path=path))
        if isinstance(body, dict):
            refused = Status.of(body.get("status")) is Status.ERROR
            if refused and not (op.payment_state and body.get("transaction")):
                message = str(body.get("message") or body.get("detail") or text("error.refused"))
                code = body.get("code")
                return Outcome(error=GatewayError(message, code=str(code) if code not in (None, "") else None,
                                                  trace_id=body.get("trace_id"), status_code=status, payload=body,
                                                  path=path))
        if status >= 400:
            detail = body.get("detail") or body.get("message") if isinstance(body, dict) else None
            return Outcome(error=HTTPStatusError(str(detail or text("error.status", status=status)), status_code=status,
                                                 body=body, path=path))
        return Outcome(value=op.parse(body))


class SyncEngine(Engine):
    def __init__(self, *args: Any, http_client: Optional[httpx.Client] = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._owns_http = http_client is None
        self._http = http_client or httpx.Client(timeout=self._timeout())

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def __enter__(self: T) -> T:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def _run(self, op: Op) -> Any:
        url = self.settings.url(op.endpoint, **op.path_params)
        args = self._request_args(op)
        attempt = 0
        while True:
            try:
                response = self._http.request(op.method, url, **args)
            except httpx.HTTPError as exc:
                outcome = self._on_exception(op, exc, attempt)
            else:
                outcome = self._on_response(op, response, attempt)
            if outcome.retry:
                time.sleep(self._wait(attempt))
                attempt += 1
                continue
            if outcome.error is not None:
                raise outcome.error
            return outcome.value


class AsyncEngine(Engine):
    def __init__(self, *args: Any, http_client: Optional[httpx.AsyncClient] = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._owns_http = http_client is None
        self._http = http_client or httpx.AsyncClient(timeout=self._timeout())

    async def close(self) -> None:
        if self._owns_http:
            await self._http.aclose()

    async def __aenter__(self: T) -> T:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    async def _run(self, op: Op) -> Any:
        url = self.settings.url(op.endpoint, **op.path_params)
        args = self._request_args(op)
        attempt = 0
        while True:
            try:
                response = await self._http.request(op.method, url, **args)
            except httpx.HTTPError as exc:
                outcome = self._on_exception(op, exc, attempt)
            else:
                outcome = self._on_response(op, response, attempt)
            if outcome.retry:
                await asyncio.sleep(self._wait(attempt))
                attempt += 1
                continue
            if outcome.error is not None:
                raise outcome.error
            return outcome.value
