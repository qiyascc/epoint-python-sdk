from __future__ import annotations

import httpx
import pytest

from epoint_sdk import (
    ConfigurationError,
    Epoint,
    InvalidRequestError,
    SignatureError,
    Status,
    WidgetMessage,
    callback_form,
    origin_of,
    signing,
    verify_callback,
)

from .conftest import PRIVATE, PUBLIC


def test_widget_for_apple_and_google_pay(gw, ep):
    gw.reply({"status": "success", "widget_url": "https://epoint.az/widget/abc?x=1", "transaction": "te7"})
    widget = ep.widgets.create("12.50", "W-1", "Balance top-up")
    assert widget.transaction == "te7" and widget.origin == "https://epoint.az"
    assert gw.paths == ["/api/1/token/widget"]
    assert gw.payload() == {"public_key": PUBLIC, "amount": 12.5, "order_id": "W-1", "description": "Balance top-up"}


def test_widget_needs_a_description(gw, ep):
    with pytest.raises(InvalidRequestError):
        ep.widgets.create(5, "W-2", " ")
    assert gw.requests == []


def test_widget_split(gw, ep):
    gw.reply({"status": "success", "redirect_url": "https://epoint.az/pay/x", "transaction": "te8"})
    ep.widgets.split(20, "W-3", "i000000002", 5, description="Split")
    sent = gw.payload()
    assert gw.paths[-1] == "/api/1/token/split-payment"
    assert (sent["split_user"], sent["split_amount"], sent["amount"]) == ("i000000002", 5.0, 20.0)
    with pytest.raises(InvalidRequestError):
        ep.widgets.split(5, "W-4", "i000000002", 6)


def test_widget_message_is_parsed_but_only_a_hint():
    message = WidgetMessage.from_event({"status": "success", "payment": {"order_id": "W-1", "status": "success",
                                                                         "transaction": "te7", "amount": 12.5}})
    assert message.looks_paid and message.order_id == "W-1" and str(message.amount) == "12.50"
    assert WidgetMessage.from_event({"status": "error"}).status is Status.ERROR
    assert WidgetMessage.from_event({"payment": "junk"}).status is Status.UNKNOWN


def test_origin_of():
    assert origin_of("https://Epoint.az:443/w/1") == "https://epoint.az:443"
    assert origin_of("javascript:alert(1)") is None and origin_of(None) is None


def test_plain_http_is_refused(gw):
    with pytest.raises(ConfigurationError):
        Epoint(PUBLIC, PRIVATE, base_url="http://epoint.example.com")
    Epoint(PUBLIC, PRIVATE, base_url="http://127.0.0.1:8181")
    Epoint(PUBLIC, PRIVATE, base_url="http://sandbox.lan", allow_insecure_http=True)
    with pytest.raises(ValueError):
        Epoint(PUBLIC, PRIVATE, base_url="ftp://epoint.az")


def test_oversized_callback_is_rejected_before_hashing():
    data = "A" * 70000
    assert not signing.matches(PRIVATE, data, signing.sign(PRIVATE, data))
    with pytest.raises(SignatureError):
        verify_callback(PRIVATE, data, signing.sign(PRIVATE, data))


def test_transaction_matches():
    tx = verify_callback(PRIVATE, callback_form(PRIVATE, {"status": "success", "order_id": "A", "amount": 9.9,
                                                           "transaction": "te1"}))
    assert tx.matches(order_id="A", amount="9.90", transaction="te1")
    assert not tx.matches(amount=10)
    assert not tx.matches(order_id="B")


def test_async_widget(gw):
    import asyncio

    from epoint_sdk import AsyncEpoint

    async def run():
        async with AsyncEpoint(PUBLIC, PRIVATE, http_client=httpx.AsyncClient(transport=httpx.MockTransport(gw))) as ep:
            gw.reply({"status": "success", "widget_url": "https://epoint.az/w", "transaction": "te9"})
            return await ep.widgets.create(1, "W-9", "x")

    assert asyncio.run(run()).transaction == "te9"
