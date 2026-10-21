from __future__ import annotations

from typing import Any, Mapping, Union

from . import signing
from .errors import SignatureError
from .messages import text
from .models import Transaction

Form = Mapping[str, Any]


def _field(form: Form, key: str) -> str:
    value = form.get(key)
    if isinstance(value, (list, tuple)):
        value = value[0] if value else ""
    return str(value or "").strip()


def verify_callback(private_key: str, data: Union[str, Form], signature: str = "") -> Transaction:
    raw = data if isinstance(data, str) else _field(data, "data")
    if not isinstance(data, str):
        signature = _field(data, "signature")
    if not raw or not signature:
        raise SignatureError(text("error.callback_fields"))
    return Transaction.from_api(signing.verify(private_key, raw, signature))


def callback_form(private_key: str, payload: Mapping[str, Any]) -> dict[str, str]:
    data = signing.encode(dict(payload))
    return {"data": data, "signature": signing.sign(private_key, data)}
