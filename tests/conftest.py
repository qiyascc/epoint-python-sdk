from __future__ import annotations

import json
from typing import Any, Callable, Union
from urllib.parse import parse_qs

import httpx
import pytest

from epoint_sdk import AsyncEpoint, Epoint, signing

PUBLIC = "i000000001"
PRIVATE = "sandbox_private_key_0000000001"

Reply = Union[httpx.Response, Exception, Callable[[httpx.Request], httpx.Response]]


class Gateway:
    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []
        self.replies: list[Reply] = []

    def reply(self, body: Any = None, status: int = 200) -> Gateway:
        content = b"" if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
        self.replies.append(httpx.Response(status, content=content))
        return self

    def fail(self, exc: Exception) -> Gateway:
        self.replies.append(exc)
        return self

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        reply = self.replies.pop(0) if self.replies else httpx.Response(200, json={"status": "success"})
        if isinstance(reply, Exception):
            raise reply
        if callable(reply):
            return reply(request)
        return reply

    def form(self, index: int = -1) -> dict[str, str]:
        return {k: v[0] for k, v in parse_qs(self.requests[index].content.decode()).items()}

    def payload(self, index: int = -1) -> dict[str, Any]:
        form = self.form(index)
        assert signing.matches(PRIVATE, form["data"], form["signature"])
        return signing.decode(form["data"])

    @property
    def paths(self) -> list[str]:
        return [r.url.path for r in self.requests]


@pytest.fixture
def gw() -> Gateway:
    return Gateway()


@pytest.fixture
def ep(gw: Gateway) -> Epoint:
    client = Epoint(PUBLIC, PRIVATE, http_client=httpx.Client(transport=httpx.MockTransport(gw)), max_retries=2)
    client._wait = lambda attempt: 0.0
    return client


@pytest.fixture
def aep(gw: Gateway) -> AsyncEpoint:
    client = AsyncEpoint(PUBLIC, PRIVATE, http_client=httpx.AsyncClient(transport=httpx.MockTransport(gw)),
                         max_retries=2)
    client._wait = lambda attempt: 0.0
    return client
