from __future__ import annotations

import base64
import json

import pytest

from epoint_sdk import GatewayError, InvalidRequestError, OutcomeUnknownError, PaymentMethod, Status

from .conftest import PUBLIC


def _sent_token(gw) -> str:
    return base64.b64decode(gw.payload()["token"]).decode()


def test_payment_methods_say_what_is_switched_on(gw, ep):
    gw.reply({"status": "success", "result": {
        "business": {"id": 42, "name": "GNET"},
        "methods": ["card", "google_pay", "installment"],
        "wallets": [{"id": "m10"}],
        "installment": {"min_amount": "50", "banks": ["kapital"]},
    }})
    methods = ep.payments.methods(language="en")
    assert gw.paths == ["/api/1/payment-methods"]
    assert gw.payload() == {"public_key": PUBLIC, "language": "en"}
    assert methods.google_pay and not methods.apple_pay and methods.has(PaymentMethod.INSTALLMENT)
    assert (methods.business_id, methods.business_name) == ("42", "GNET")
    assert str(methods.installment_min_amount) == "50.00" and methods.installment_banks == ("kapital",)


def test_payment_methods_tolerate_an_empty_answer(gw, ep):
    gw.reply({"status": "success"})
    methods = ep.payments.methods()
    assert methods.methods == () and not methods.google_pay and methods.installment_min_amount is None


def test_status_by_order_id(gw, ep):
    gw.reply({"status": "success", "transaction": "te1", "order_id": "O-1", "amount": 5})
    ep.payments.status(order_id="O-1")
    assert gw.paths == ["/api/1/get-status"]
    assert gw.payload() == {"public_key": PUBLIC, "order_id": "O-1"}
    with pytest.raises(InvalidRequestError):
        ep.payments.status()


def test_token_payment_then_apple_pay_charge(gw, ep):
    gw.reply({"status": "success", "payment": {"id": 991, "merchant_order_id": "A-1", "total": "25.50"}})
    record = ep.tokens.create("25.50", "A-1", description="Order")
    assert gw.paths == ["/api/1/token/payment"]
    assert gw.payload()["amount"] == 25.5 and gw.payload()["order_id"] == "A-1"
    assert (record.payment_id, record.order_id, str(record.amount)) == ("991", "A-1", "25.50")

    gw.reply({"status": "success", "order_id": "A-1", "payment_id": 991})
    data = {"version": "EC_v1", "data": "abc", "signature": "sig", "header": {}}
    charge = ep.tokens.apple_pay(record.payment_id, data, billing_contact={"emailAddress": "a@b.az"})
    assert gw.paths[-1] == "/api/1/token/apple/pay"
    sent = gw.payload()
    assert sent["id"] == 991 and sent["billingContact"] == {"emailAddress": "a@b.az"}
    assert json.loads(_sent_token(gw)) == data
    assert charge.ok and charge.order_id == "A-1"


def test_google_pay_token_is_sent_as_it_arrived(gw, ep):
    raw = '{"signature":"MEU","protocolVersion":"ECv2","signedMessage":"{}"}'
    gw.reply({"status": "new", "redirect_url": "https://epoint.az/3ds/x", "payment_id": 7})
    charge = ep.tokens.google_pay(7, raw)
    assert gw.paths == ["/api/1/token/google/pay"]
    assert _sent_token(gw) == raw and "billingContact" not in gw.payload()
    assert charge.status is Status.NEW and charge.redirect_url == "https://epoint.az/3ds/x" and not charge.ok


def test_a_declined_token_raises_with_the_gateway_answer(gw, ep):
    gw.reply({"status": "error", "code": "05", "message": "Do not honor"})
    with pytest.raises(GatewayError) as raised:
        ep.tokens.google_pay(7, "tok")
    assert raised.value.code == "05"


def test_a_token_charge_is_never_resent_after_a_server_error(gw, ep):
    gw.reply({"status": "error"}, status=502)
    with pytest.raises(OutcomeUnknownError):
        ep.tokens.apple_pay(1, {"data": "x"})
    assert len(gw.requests) == 1


def test_apple_session_needs_an_origin(gw, ep):
    with pytest.raises(InvalidRequestError):
        ep.tokens.apple_session(" ")
    gw.reply({"status": "success", "session": {"merchantSessionIdentifier": "s1"}})
    session = ep.tokens.apple_session("https://shop.az")
    assert gw.paths == ["/api/1/token/apple/session"] and gw.payload()["origin"] == "https://shop.az"
    assert session.session == {"merchantSessionIdentifier": "s1"}


def test_token_ids_and_tokens_are_required(gw, ep):
    with pytest.raises(InvalidRequestError):
        ep.tokens.google_pay("", "tok")
    with pytest.raises(InvalidRequestError):
        ep.tokens.google_pay(1, " ")
    assert gw.requests == []
