from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Union

from .errors import InvalidRequestError
from .messages import text

Amount = Union[Decimal, int, float, str]
CENT = Decimal("0.01")


def amount(value: Amount, field: str = "amount") -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (Decimal, int, float, str)):
        raise InvalidRequestError(text("value.amount_type", field=field, value=value))
    try:
        number = Decimal(str(value).strip()) if not isinstance(value, Decimal) else value
    except InvalidOperation:
        raise InvalidRequestError(text("value.amount_type", field=field, value=value)) from None
    if not number.is_finite():
        raise InvalidRequestError(text("value.amount_finite", field=field, value=value))
    if number <= 0:
        raise InvalidRequestError(text("value.amount_positive", field=field, value=value))
    if number != number.quantize(CENT):
        raise InvalidRequestError(text("value.amount_scale", field=field, value=value))
    return number.quantize(CENT)


def wire(value: Decimal) -> float:
    return float(value)


def parse(value: object) -> Decimal | None:
    if value is None or value == "" or isinstance(value, bool):
        return None
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        return None
    return number.quantize(CENT) if number.is_finite() else None
