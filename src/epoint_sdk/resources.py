from __future__ import annotations

from datetime import date
from typing import Any, Mapping, Optional, Union

from ._core import Op
from .enums import Currency, Language
from .errors import InvalidRequestError
from .messages import text
from .models import (
    Card,
    CardRegistration,
    InstallmentPlan,
    Invoice,
    Redirect,
    Result,
    Transaction,
    Transfer,
    Wallet,
    Widget,
)
from .money import Amount, amount, wire

LanguageLike = Union[Language, str]
CurrencyLike = Union[Currency, str]


def required(value: Any, name: str, limit: int = 255) -> str:
    result = str(value if value is not None else "").strip()
    if not result:
        raise InvalidRequestError(text("value.empty", field=name))
    if len(result) > limit:
        raise InvalidRequestError(text("value.too_long", field=name, limit=limit))
    return result


def optional(value: Any, name: str, limit: int = 1000) -> Optional[str]:
    if value is None or str(value).strip() == "":
        return None
    result = str(value).strip()
    if len(result) > limit:
        raise InvalidRequestError(text("value.too_long", field=name, limit=limit))
    return result


def flag(value: Optional[bool]) -> Optional[int]:
    return None if value is None else int(bool(value))


def day(value: Union[date, str]) -> str:
    return value.isoformat() if isinstance(value, date) else required(value, "date", 32)


class _Resource:
    def __init__(self, client: Any) -> None:
        self._client = client

    @property
    def _settings(self) -> Any:
        return self._client.settings

    def _language(self, value: Optional[LanguageLike]) -> str:
        return str(Language(str(value))) if value else str(self._settings.language)

    def _currency(self, value: Optional[CurrencyLike]) -> str:
        return str(Currency(str(value).upper())) if value else str(self._settings.currency)

    def _checkout(self, total: Amount, order_id: str, description: Optional[str], language: Optional[LanguageLike],
                  currency: Optional[CurrencyLike], success_url: Optional[str], error_url: Optional[str],
                  other_attr: Any = None) -> dict[str, Any]:
        return {
            "amount": wire(amount(total)),
            "order_id": required(order_id, "order_id"),
            "currency": self._currency(currency),
            "language": self._language(language),
            "description": optional(description, "description"),
            "success_redirect_url": success_url or self._settings.success_url,
            "error_redirect_url": error_url or self._settings.error_url,
            "other_attr": other_attr,
        }

    def _run(self, op: Op) -> Any:
        return self._client._run(op)


class Payments(_Resource):
    def create(self, amount: Amount, order_id: str, *, description: Optional[str] = None,
               language: Optional[LanguageLike] = None, currency: Optional[CurrencyLike] = None,
               success_url: Optional[str] = None, error_url: Optional[str] = None, installment: Optional[bool] = None,
               other_attr: Any = None) -> Any:
        payload = self._checkout(amount, order_id, description, language, currency, success_url, error_url, other_attr)
        payload["is_installment"] = flag(installment)
        return self._run(Op("payment", payload, Redirect.from_api, order_id=str(payload["order_id"])))

    def form(self, amount: Amount, order_id: str, *, description: Optional[str] = None,
             language: Optional[LanguageLike] = None, currency: Optional[CurrencyLike] = None,
             success_url: Optional[str] = None, error_url: Optional[str] = None, installment: Optional[bool] = None,
             other_attr: Any = None) -> Any:
        from .models import CheckoutForm

        payload = self._checkout(amount, order_id, description, language, currency, success_url, error_url, other_attr)
        payload["is_installment"] = flag(installment)
        signed = self._client.sign(payload)
        return CheckoutForm(self._settings.url("checkout"), signed["data"], signed["signature"])

    def status(self, transaction: str) -> Any:
        payload = {"transaction": required(transaction, "transaction")}
        return self._run(Op("status", payload, Transaction.from_api, safe=True, payment_state=True))

    def reverse(self, transaction: str, amount_: Optional[Amount] = None, *, currency: Optional[CurrencyLike] = None,
                language: Optional[LanguageLike] = None) -> Any:
        payload = {
            "transaction": required(transaction, "transaction"),
            "amount": wire(amount(amount_)) if amount_ is not None else None,
            "currency": self._currency(currency),
            "language": self._language(language),
        }
        return self._run(Op("reverse", payload, Result.from_api))

    def hold(self, amount: Amount, order_id: str, *, description: Optional[str] = None,
             language: Optional[LanguageLike] = None, currency: Optional[CurrencyLike] = None,
             success_url: Optional[str] = None, error_url: Optional[str] = None, other_attr: Any = None) -> Any:
        payload = self._checkout(amount, order_id, description, language, currency, success_url, error_url, other_attr)
        return self._run(Op("hold", payload, Redirect.from_api, order_id=str(payload["order_id"])))

    def capture(self, transaction: str, amount_: Amount) -> Any:
        payload = {"transaction": required(transaction, "transaction"), "amount": wire(amount(amount_))}
        return self._run(Op("capture", payload, Result.from_api))


class Cards(_Resource):
    def register(self, *, payouts: bool = False, description: Optional[str] = None,
                 language: Optional[LanguageLike] = None, success_url: Optional[str] = None,
                 error_url: Optional[str] = None) -> Any:
        payload = {
            "language": self._language(language),
            "refund": int(payouts),
            "description": optional(description, "description"),
            "success_redirect_url": success_url or self._settings.success_url,
            "error_redirect_url": error_url or self._settings.error_url,
        }
        return self._run(Op("card_register", payload, CardRegistration.from_api))

    def register_and_pay(self, amount: Amount, order_id: str, *, description: Optional[str] = None,
                         language: Optional[LanguageLike] = None, currency: Optional[CurrencyLike] = None,
                         success_url: Optional[str] = None, error_url: Optional[str] = None) -> Any:
        payload = self._checkout(amount, order_id, description, language, currency, success_url, error_url)
        payload["refund"] = 0
        return self._run(Op("card_register_pay", payload, CardRegistration.from_api, order_id=str(payload["order_id"])))

    def charge(self, card_id: str, amount_: Amount, order_id: str, *, description: Optional[str] = None,
               language: Optional[LanguageLike] = None, currency: Optional[CurrencyLike] = None) -> Any:
        payload = {
            "card_id": required(card_id, "card_id"),
            "amount": wire(amount(amount_)),
            "order_id": required(order_id, "order_id"),
            "currency": self._currency(currency),
            "language": self._language(language),
            "description": optional(description, "description"),
        }
        return self._run(Op("card_charge", payload, Transaction.from_api, payment_state=True,
                            order_id=str(payload["order_id"])))

    def payout(self, card_id: str, amount_: Amount, order_id: str, *, description: Optional[str] = None,
               language: Optional[LanguageLike] = None, currency: Optional[CurrencyLike] = None) -> Any:
        payload = {
            "card_id": required(card_id, "card_id"),
            "amount": wire(amount(amount_)),
            "order_id": required(order_id, "order_id"),
            "currency": self._currency(currency),
            "language": self._language(language),
            "description": optional(description, "description"),
        }
        return self._run(Op("payout", payload, Transaction.from_api, payment_state=True,
                            order_id=str(payload["order_id"])))

    def status(self, card_id: str) -> Any:
        payload = {"card_id": required(card_id, "card_id")}
        return self._run(Op("card_status", payload, Card.from_api, safe=True))


def split_parts(total: Amount, partner: str, partner_amount: Amount) -> dict[str, Any]:
    whole, part = amount(total), amount(partner_amount, "split_amount")
    if part > whole:
        raise InvalidRequestError(text("value.split_amount", split=part, amount=whole))
    return {"split_user": required(partner, "split_user"), "split_amount": wire(part)}


class Split(_Resource):

    def create(self, amount: Amount, order_id: str, partner: str, partner_amount: Amount, *,
               description: Optional[str] = None, language: Optional[LanguageLike] = None,
               currency: Optional[CurrencyLike] = None, success_url: Optional[str] = None,
               error_url: Optional[str] = None, other_attr: Any = None) -> Any:
        payload = self._checkout(amount, order_id, description, language, currency, success_url, error_url, other_attr)
        payload.update(split_parts(amount, partner, partner_amount))
        return self._run(Op("split_payment", payload, Redirect.from_api, order_id=str(payload["order_id"])))

    def charge(self, card_id: str, amount_: Amount, order_id: str, partner: str, partner_amount: Amount, *,
               description: Optional[str] = None, language: Optional[LanguageLike] = None,
               currency: Optional[CurrencyLike] = None) -> Any:
        payload = {
            "card_id": required(card_id, "card_id"),
            "amount": wire(amount(amount_)),
            "order_id": required(order_id, "order_id"),
            "currency": self._currency(currency),
            "language": self._language(language),
            "description": optional(description, "description"),
            **split_parts(amount_, partner, partner_amount),
        }
        return self._run(Op("split_charge", payload, Transaction.from_api, payment_state=True,
                            order_id=str(payload["order_id"])))

    def register_and_pay(self, amount: Amount, order_id: str, partner: str, partner_amount: Amount, *,
                         description: Optional[str] = None, language: Optional[LanguageLike] = None,
                         currency: Optional[CurrencyLike] = None, success_url: Optional[str] = None,
                         error_url: Optional[str] = None) -> Any:
        payload = self._checkout(amount, order_id, description, language, currency, success_url, error_url)
        payload.update(split_parts(amount, partner, partner_amount))
        return self._run(Op("split_register_pay", payload, CardRegistration.from_api,
                            order_id=str(payload["order_id"])))


def _plans(body: Any) -> list[InstallmentPlan]:
    rows = body if isinstance(body, list) else (body or {}).get("data") or (body or {}).get("installments") or []
    return [InstallmentPlan.from_api(row) for row in rows if isinstance(row, Mapping)]


class Installments(_Resource):
    def plans(self, order_id: str, amount_: Optional[Amount] = None, *, language: Optional[LanguageLike] = None,
              currency: Optional[CurrencyLike] = None) -> Any:
        payload = {
            "order_id": required(order_id, "order_id"),
            "amount": wire(amount(amount_)) if amount_ is not None else None,
            "currency": self._currency(currency),
            "language": self._language(language),
        }
        return self._run(Op("installment_plans", payload, _plans, safe=True))

    def create(self, amount: Amount, order_id: str, card_id: str, months: int, *, description: Optional[str] = None,
               language: Optional[LanguageLike] = None, currency: Optional[CurrencyLike] = None,
               success_url: Optional[str] = None, error_url: Optional[str] = None) -> Any:
        if isinstance(months, bool) or not isinstance(months, int) or months < 1:
            raise InvalidRequestError(text("value.months", value=months))
        payload = self._checkout(amount, order_id, description, language, currency, success_url, error_url)
        payload.update({"installment_card_id": required(card_id, "installment_card_id"), "installment_month": months})
        return self._run(Op("installment_payment", payload, Redirect.from_api, order_id=str(payload["order_id"])))


def _wallets(body: Any) -> list[Wallet]:
    if isinstance(body, Mapping) and isinstance(body.get("wallets"), list):
        return [Wallet.from_api(row) for row in body["wallets"] if isinstance(row, Mapping)]
    if isinstance(body, Mapping):
        skip = {"status", "trace_id", "message", "code"}
        return [Wallet(str(key), value) for key, value in body.items() if key not in skip and isinstance(value, str)]
    return []


class Wallets(_Resource):
    def list(self) -> Any:
        return self._run(Op("wallets", {}, _wallets, safe=True))

    def pay(self, wallet_id: str, amount_: Amount, order_id: str, *, description: Optional[str] = None,
            language: Optional[LanguageLike] = None, currency: Optional[CurrencyLike] = None) -> Any:
        payload = {
            "wallet_id": required(wallet_id, "wallet_id"),
            "amount": wire(amount(amount_)),
            "order_id": required(order_id, "order_id"),
            "currency": self._currency(currency),
            "language": self._language(language),
            "description": optional(description, "description"),
        }
        return self._run(Op("wallet_payment", payload, Redirect.from_api, order_id=str(payload["order_id"])))


class Widgets(_Resource):
    def create(self, amount_: Amount, order_id: str, description: str) -> Any:
        payload = {"amount": wire(amount(amount_)), "order_id": required(order_id, "order_id"),
                   "description": required(description, "description")}
        return self._run(Op("widget", payload, Widget.from_api, order_id=str(payload["order_id"])))

    def split(self, amount: Amount, order_id: str, partner: str, partner_amount: Amount, *,
              description: Optional[str] = None, language: Optional[LanguageLike] = None,
              currency: Optional[CurrencyLike] = None, success_url: Optional[str] = None,
              error_url: Optional[str] = None) -> Any:
        payload = self._checkout(amount, order_id, description, language, currency, success_url, error_url)
        payload.update(split_parts(amount, partner, partner_amount))
        return self._run(Op("widget_split", payload, Redirect.from_api, order_id=str(payload["order_id"])))


def _invoice_body(total: Amount, period_from: Union[date, str], period_to: Union[date, str], name: Optional[str],
                  description: Optional[str], phone: Optional[str], email: Optional[str], tin: Optional[str],
                  contract_number: Optional[str], merchant_order_id: Optional[str], display: bool,
                  save_as_template: bool, installment: bool) -> dict[str, Any]:
    return {
        "sum": wire(amount(total, "sum")),
        "period_from": day(period_from),
        "period_to": day(period_to),
        "name": optional(name, "name"),
        "description": optional(description, "description"),
        "phone": optional(phone, "phone", 32),
        "email": optional(email, "email", 254),
        "inn": optional(tin, "tin", 32),
        "contract_number": optional(contract_number, "contract_number"),
        "merchant_order_id": optional(merchant_order_id, "merchant_order_id"),
        "display": int(display),
        "save_as_template": int(save_as_template),
        "status_installment": int(installment),
    }


class Invoices(_Resource):
    def create(self, amount: Amount, period_from: Union[date, str], period_to: Union[date, str], *,
               name: Optional[str] = None, description: Optional[str] = None, phone: Optional[str] = None,
               email: Optional[str] = None, tin: Optional[str] = None, contract_number: Optional[str] = None,
               merchant_order_id: Optional[str] = None, display: bool = True, save_as_template: bool = False,
               installment: bool = False) -> Any:
        payload = _invoice_body(amount, period_from, period_to, name, description, phone, email, tin, contract_number,
                                merchant_order_id, display, save_as_template, installment)
        return self._run(Op("invoice_create", payload, lambda body: int(body["id"]) if body.get("id") else None))

    def update(self, invoice_id: int, amount: Amount, period_from: Union[date, str], period_to: Union[date, str], *,
               name: Optional[str] = None, description: Optional[str] = None, phone: Optional[str] = None,
               email: Optional[str] = None, tin: Optional[str] = None, contract_number: Optional[str] = None,
               merchant_order_id: Optional[str] = None, display: bool = True, save_as_template: bool = False,
               installment: bool = False) -> Any:
        payload = _invoice_body(amount, period_from, period_to, name, description, phone, email, tin, contract_number,
                                merchant_order_id, display, save_as_template, installment)
        payload["id"] = int(invoice_id)
        return self._run(Op("invoice_update", payload, Result.from_api))

    def get(self, invoice_id: int) -> Any:
        return self._run(Op("invoice_view", {"id": int(invoice_id)},
                            lambda body: Invoice.from_api(body.get("invoice") or {}), safe=True))

    def list(self, *, kind: Optional[str] = None, order: Optional[str] = None) -> Any:
        return self._run(Op("invoice_list", {"type": kind, "order": order},
                            lambda body: [Invoice.from_api(row) for row in body.get("invoices") or []], safe=True))

    def send_sms(self, invoice_id: int, phone: str) -> Any:
        payload = {"id": int(invoice_id), "phone": required(phone, "phone", 32)}
        return self._run(Op("invoice_sms", payload, Result.from_api))

    def send_email(self, invoice_id: int, email: str) -> Any:
        payload = {"id": int(invoice_id), "email": required(email, "email", 254)}
        return self._run(Op("invoice_email", payload, Result.from_api))


class Transfers(_Resource):
    def create(self, order_id: str, amount_: Amount, *, iban: str, name: str, tin: str, bank_code: str,
               description: str, bank_name: Optional[str] = None, email: Optional[str] = None,
               address: Optional[str] = None, additional_info: Optional[str] = None,
               webhook_url: Optional[str] = None) -> Any:
        payload = {
            "order_id": required(order_id, "order_id"),
            "amount": wire(amount(amount_)),
            "description": required(description, "description"),
            "iban": required(iban, "iban", 34).replace(" ", "").upper(),
            "name": required(name, "name"),
            "tin": required(tin, "tin", 32),
            "bank_code": required(bank_code, "bank_code", 32),
            "bank_name": optional(bank_name, "bank_name"),
            "email": optional(email, "email", 254),
            "address": optional(address, "address"),
            "additional_info": optional(additional_info, "additional_info"),
            "webhook_url": optional(webhook_url, "webhook_url", 2048),
        }
        return self._run(Op("b2b_transfer", payload, Transfer.from_api, json_body=True,
                            order_id=str(payload["order_id"])))

    def status(self, order_id: str) -> Any:
        key = required(order_id, "order_id")
        return self._run(Op("b2b_status", None, Transfer.from_api, safe=True, method="GET", signed=False,
                            path_params={"order_id": key}))
