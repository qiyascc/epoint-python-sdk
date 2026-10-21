from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import json
from typing import Any

from .errors import SignatureError
from .messages import text


def encode(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, separators=(",", ":"), ensure_ascii=True)
    return base64.b64encode(body.encode("utf-8")).decode("ascii")


def sign(private_key: str, data: str) -> str:
    digest = hashlib.sha1(f"{private_key}{data}{private_key}".encode()).digest()
    return base64.b64encode(digest).decode("ascii")


def matches(private_key: str, data: str, signature: str) -> bool:
    if not private_key or not data or not signature or len(data) > MAX_DATA or len(signature) > 128:
        return False
    return hmac.compare_digest(sign(private_key, data).encode(), str(signature).strip().encode())


MAX_DATA = 65536


def decode(data: str) -> dict[str, Any]:
    if len(data) > MAX_DATA:
        raise SignatureError(text("error.too_large", limit=MAX_DATA))
    try:
        raw = base64.b64decode(data, validate=True)
        parsed = json.loads(raw.decode("utf-8"))
    except (binascii.Error, ValueError, UnicodeDecodeError):
        raise SignatureError(text("error.data")) from None
    if not isinstance(parsed, dict):
        raise SignatureError(text("error.data_object"))
    return parsed


def verify(private_key: str, data: str, signature: str) -> dict[str, Any]:
    if not matches(private_key, data, signature):
        raise SignatureError(text("error.signature"))
    return decode(data)
