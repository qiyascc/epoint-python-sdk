from __future__ import annotations

from decimal import Decimal

import pytest

from epoint_sdk import InvalidRequestError
from epoint_sdk.money import amount, parse


@pytest.mark.parametrize("value,expected", [(10, "10.00"), ("9.9", "9.90"), (Decimal("0.01"), "0.01"), (19.99, "19.99"),
                                            (" 5 ", "5.00")])
def test_valid(value, expected):
    assert str(amount(value)) == expected


@pytest.mark.parametrize("value", [0, -1, "1.005", 0.001, "abc", None, True, "NaN", "Infinity", [], 1e-9])
def test_invalid(value):
    with pytest.raises(InvalidRequestError):
        amount(value)


def test_parse_is_lenient():
    assert parse("10") == Decimal("10.00")
    assert parse(None) is None and parse("x") is None and parse("nan") is None
