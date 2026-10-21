from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Mapping, Optional

from .enums import CardStatus, Status
from .money import parse


def _str(body: Mapping[str, Any], key: str) -> Optional[str]:
    value = body.get(key)
    if value is None or value == "":
        return None
    return str(value)


@dataclass(frozen=True)
class Redirect:
    redirect_url: Optional[str]
    transaction: Optional[str]
    trace_id: Optional[str] = None
    message: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_api(cls, body: Mapping[str, Any]) -> Redirect:
        return cls(_str(body, "redirect_url"), _str(body, "transaction"), _str(body, "trace_id"), _str(body, "message"),
                   dict(body))


@dataclass(frozen=True)
class Transaction:
    status: Status
    transaction: Optional[str] = None
    order_id: Optional[str] = None
    amount: Optional[Decimal] = None
    code: Optional[str] = None
    message: Optional[str] = None
    bank_transaction: Optional[str] = None
    bank_response: Optional[str] = None
    operation_code: Optional[str] = None
    rrn: Optional[str] = None
    card_id: Optional[str] = None
    card_name: Optional[str] = None
    card_mask: Optional[str] = None
    split_amount: Optional[Decimal] = None
    other_attr: Any = None
    trace_id: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_api(cls, body: Mapping[str, Any]) -> Transaction:
        return cls(
            status=Status.of(body.get("status")),
            transaction=_str(body, "transaction"),
            order_id=_str(body, "order_id"),
            amount=parse(body.get("amount")),
            code=_str(body, "code"),
            message=_str(body, "message"),
            bank_transaction=_str(body, "bank_transaction"),
            bank_response=_str(body, "bank_response"),
            operation_code=_str(body, "operation_code"),
            rrn=_str(body, "rrn"),
            card_id=_str(body, "card_id"),
            card_name=_str(body, "card_name"),
            card_mask=_str(body, "card_mask"),
            split_amount=parse(body.get("split_amount")),
            other_attr=body.get("other_attr"),
            trace_id=_str(body, "trace_id"),
            raw=dict(body),
        )

    @property
    def paid(self) -> bool:
        return self.status is Status.SUCCESS

    @property
    def returned(self) -> bool:
        return self.status is Status.RETURNED

    @property
    def failed(self) -> bool:
        return self.status in (Status.FAILED, Status.ERROR)

    @property
    def pending(self) -> bool:
        return self.status in (Status.NEW, Status.SERVER_ERROR, Status.UNKNOWN)

    @property
    def final(self) -> bool:
        return not self.pending


Callback = Transaction


@dataclass(frozen=True)
class Result:
    status: Status
    transaction: Optional[str] = None
    message: Optional[str] = None
    trace_id: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_api(cls, body: Mapping[str, Any]) -> Result:
        return cls(Status.of(body.get("status")), _str(body, "transaction"), _str(body, "message"),
                   _str(body, "trace_id"), dict(body))

    @property
    def ok(self) -> bool:
        return self.status is Status.SUCCESS


@dataclass(frozen=True)
class CardRegistration:
    card_id: Optional[str]
    redirect_url: Optional[str]
    transaction: Optional[str] = None
    trace_id: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_api(cls, body: Mapping[str, Any]) -> CardRegistration:
        return cls(_str(body, "card_id"), _str(body, "redirect_url"), _str(body, "transaction"), _str(body, "trace_id"),
                   dict(body))


@dataclass(frozen=True)
class Card:
    id: Optional[str]
    status: CardStatus
    name: Optional[str] = None
    mask: Optional[str] = None
    expiry: Optional[str] = None
    description: Optional[str] = None
    trace_id: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_api(cls, body: Mapping[str, Any]) -> Card:
        return cls(_str(body, "id") or _str(body, "card_id"), CardStatus.of(body.get("status")), _str(body, "name"),
                   _str(body, "mask"), _str(body, "expired_date"), _str(body, "description"), _str(body, "trace_id"),
                   dict(body))

    @property
    def usable(self) -> bool:
        return self.status is CardStatus.ACTIVE


@dataclass(frozen=True)
class Widget:
    widget_url: Optional[str]
    transaction: Optional[str] = None
    trace_id: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_api(cls, body: Mapping[str, Any]) -> Widget:
        return cls(_str(body, "widget_url"), _str(body, "transaction"), _str(body, "trace_id"), dict(body))


@dataclass(frozen=True)
class InstallmentPlan:
    card_id: str
    name: str
    months: tuple[int, ...]

    @classmethod
    def from_api(cls, body: Mapping[str, Any]) -> InstallmentPlan:
        months = body.get("installment_months") or []
        return cls(str(body.get("installment_card_id") or ""), str(body.get("name") or ""),
                   tuple(int(m) for m in months if str(m).isdigit()))


@dataclass(frozen=True)
class Wallet:
    id: str
    name: str

    @classmethod
    def from_api(cls, body: Mapping[str, Any]) -> Wallet:
        return cls(str(body.get("id") or body.get("wallet_id") or ""), str(body.get("name") or ""))


@dataclass(frozen=True)
class Invoice:
    id: Optional[int]
    amount: Optional[Decimal]
    status: Optional[str]
    name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    period_from: Optional[str] = None
    period_to: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_api(cls, body: Mapping[str, Any]) -> Invoice:
        ident = str(body.get("id") or "")
        return cls(int(ident) if ident.isdigit() else None, parse(body.get("sum")), _str(body, "status"),
                   _str(body, "name"), _str(body, "description"), _str(body, "phone"), _str(body, "email"),
                   _str(body, "period_from"), _str(body, "period_to"), dict(body))


@dataclass(frozen=True)
class Transfer:
    order_id: Optional[str]
    status: Optional[str]
    bulk_id: Optional[str] = None
    amount: Optional[Decimal] = None
    payee_iban: Optional[str] = None
    payee_name: Optional[str] = None
    raw: Mapping[str, Any] = field(default_factory=dict, repr=False, compare=False)

    @classmethod
    def from_api(cls, body: Mapping[str, Any]) -> Transfer:
        return cls(_str(body, "order_id"), _str(body, "status"), _str(body, "bulkId") or _str(body, "bulk_id"),
                   parse(body.get("amount")), _str(body, "payee_iban"), _str(body, "payee_name"), dict(body))


@dataclass(frozen=True)
class CheckoutForm:
    action: str
    data: str
    signature: str

    @property
    def fields(self) -> dict[str, str]:
        return {"data": self.data, "signature": self.signature}
