from __future__ import annotations

import httpx
import pytest

from epoint_sdk import (
    CardStatus,
    ConfigurationError,
    Epoint,
    GatewayError,
    HTTPStatusError,
    InvalidRequestError,
    Language,
    Status,
)

from .conftest import PUBLIC


def test_create_payment(gw, ep):
    gw.reply({"status": "success", "transaction": "te001", "redirect_url": "https://epoint.az/pay/x", "trace_id": "t"})
    result = ep.payments.create("10.5", "ORD-1", description="Plan", success_url="https://s.test/ok",
                                language=Language.EN)
    assert result.redirect_url == "https://epoint.az/pay/x" and result.transaction == "te001"
    assert gw.paths == ["/api/1/request"]
    sent = gw.payload()
    assert sent == {"public_key": PUBLIC, "amount": 10.5, "order_id": "ORD-1", "currency": "AZN", "language": "en",
                    "description": "Plan", "success_redirect_url": "https://s.test/ok"}


def test_defaults_from_settings(gw):
    client = Epoint(PUBLIC, "k", http_client=httpx.Client(transport=httpx.MockTransport(gw)),
                    success_url="https://a/ok", error_url="https://a/no", language="ru")
    gw.reply({"status": "success", "redirect_url": "u"})
    client.payments.create(1, "o")
    form = gw.form()
    from epoint_sdk import signing

    sent = signing.decode(form["data"])
    assert (sent["success_redirect_url"], sent["error_redirect_url"], sent["language"]) == ("https://a/ok", "https://a/no",
                                                                                            "ru")


def test_validation_happens_before_sending(gw, ep):
    with pytest.raises(InvalidRequestError):
        ep.payments.create("1.001", "o")
    with pytest.raises(InvalidRequestError):
        ep.payments.create(1, " ")
    with pytest.raises(ValueError):
        ep.payments.create(1, "o", currency="GBP")
    with pytest.raises(InvalidRequestError):
        ep.split.create(10, "o", "i000000002", 11)
    assert gw.requests == []


def test_gateway_refusal(gw, ep):
    gw.reply({"status": "error", "message": "order_id already used", "code": "E12", "trace_id": "tr"})
    with pytest.raises(GatewayError) as info:
        ep.payments.create(1, "o")
    assert info.value.code == "E12" and info.value.trace_id == "tr" and "already used" in str(info.value)


def test_status_returns_failed_payment_instead_of_raising(gw, ep):
    gw.reply({"status": "error", "transaction": "te9", "amount": 3, "bank_response": "116", "message": "Declined"})
    tx = ep.payments.status("te9")
    assert tx.failed and not tx.paid and tx.final and tx.bank_response == "116"
    gw.reply({"status": "new", "transaction": "te9"})
    assert ep.payments.status("te9").pending
    gw.reply({"status": "error", "message": "Unknown transaction"})
    with pytest.raises(GatewayError):
        ep.payments.status("nope")


def test_unknown_status_value_is_pending(gw, ep):
    gw.reply({"status": "processing", "transaction": "te1"})
    tx = ep.payments.status("te1")
    assert tx.status is Status.UNKNOWN and tx.pending


def test_saved_card_charge_and_status(gw, ep):
    gw.reply({"status": "failed", "transaction": "te2", "amount": 5, "message": "Insufficient funds"})
    tx = ep.cards.charge("ce1", 5, "o2")
    assert tx.failed and gw.paths[-1] == "/api/1/execute-pay"
    gw.reply({"id": "ce1", "status": "active", "mask": "4111****1111", "expired_date": "12/29", "name": "VISA"})
    card = ep.cards.status("ce1")
    assert card.usable and card.status is CardStatus.ACTIVE and card.expiry == "12/29"


def test_card_registration_and_payout(gw, ep):
    gw.reply({"status": "success", "card_id": "ce5", "redirect_url": "https://r"})
    reg = ep.cards.register(payouts=True)
    assert reg.card_id == "ce5" and gw.payload()["refund"] == 1
    gw.reply({"status": "success", "transaction": "te3", "amount": 2})
    assert ep.cards.payout("ce5", 2, "p1").paid and gw.paths[-1] == "/api/1/refund-request"


def test_reverse_and_capture(gw, ep):
    gw.reply({"status": "success", "message": ""})
    assert ep.payments.reverse("te1").ok
    assert "amount" not in gw.payload()
    gw.reply({"status": "success", "transaction": "te1"})
    assert ep.payments.capture("te1", "4.20").ok and gw.payload()["amount"] == 4.2


def test_checkout_form_is_signed_locally(gw, ep):
    form = ep.payments.form(7, "o9")
    assert form.action == "https://epoint.az/api/1/checkout" and set(form.fields) == {"data", "signature"}
    assert gw.requests == []


def test_lists(gw, ep):
    gw.reply({"wallet_epul": "E-Pul", "status": "success", "trace_id": "x"})
    assert [(w.id, w.name) for w in ep.wallets.list()] == [("wallet_epul", "E-Pul")]
    gw.reply([{"name": "Birbank", "installment_card_id": "1", "installment_months": [3, 6]}])
    assert ep.installments.plans("o").pop().months == (3, 6)
    gw.reply({"status": "success", "invoices": [{"id": 4, "sum": 9.5, "status": "paid"}]})
    assert ep.invoices.list()[0].amount is not None


def test_transfer_status_is_unsigned_get(gw, ep):
    gw.reply({"status": "SUCCESS", "order_id": "b/1", "bulkId": "77"})
    transfer = ep.transfers.status("b/1")
    assert transfer.bulk_id == "77" and gw.requests[-1].method == "GET"
    assert gw.requests[-1].url.raw_path == b"/api/1/b2b/payment/b%2F1"


def test_heartbeat(gw, ep):
    gw.reply({"status": "ok", "trace_id": "x"})
    assert ep.heartbeat() is True


def test_http_error(gw, ep):
    gw.reply({"detail": "Missing required parameter: iban"}, status=422)
    with pytest.raises(HTTPStatusError) as info:
        ep.invoices.get(1)
    assert info.value.status_code == 422


def test_keys_required_and_secret_hidden(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("EPOINT_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("EPOINT_PRIVATE_KEY", raising=False)
    with pytest.raises(ConfigurationError):
        Epoint()
    monkeypatch.setenv("EPOINT_PUBLIC_KEY", "i1")
    monkeypatch.setenv("EPOINT_PRIVATE_KEY", "very-secret")
    client = Epoint()
    assert "very-secret" not in repr(client) and "very-secret" not in repr(client.settings)


def test_endpoint_override(gw):
    client = Epoint(PUBLIC, "k", http_client=httpx.Client(transport=httpx.MockTransport(gw)),
                    base_url="http://localhost:8181/", endpoints={"payment": "/v2/pay"})
    gw.reply({"status": "success"})
    client.payments.create(1, "o")
    assert str(gw.requests[-1].url) == "http://localhost:8181/v2/pay"
