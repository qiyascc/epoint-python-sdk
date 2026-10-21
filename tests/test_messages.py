from __future__ import annotations

import pytest

from epoint_sdk import InvalidRequestError, messages
from epoint_sdk.money import amount


def test_override_and_reset():
    messages.use({"value": {"amount_positive": "{field} sıfırdan böyük olmalıdır"}})
    try:
        with pytest.raises(InvalidRequestError, match="sıfırdan"):
            amount(0)
    finally:
        messages.reset()
    with pytest.raises(KeyError):
        messages.use({"value.nope": "x"})
