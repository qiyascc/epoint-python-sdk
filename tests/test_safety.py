from __future__ import annotations

import httpx
import pytest

from epoint_sdk import HTTPStatusError, NotSentError, OutcomeUnknownError, TransportError


def test_payment_is_never_resent_after_a_timeout(gw, ep):
    gw.fail(httpx.ReadTimeout("slow"))
    with pytest.raises(OutcomeUnknownError) as info:
        ep.payments.create(10, "ORD-7")
    assert len(gw.requests) == 1 and info.value.order_id == "ORD-7"


@pytest.mark.parametrize("exc", [httpx.RemoteProtocolError("cut"), httpx.ReadError("reset"), httpx.WriteTimeout("w")])
def test_any_ambiguous_failure_is_unknown(gw, ep, exc):
    gw.fail(exc)
    with pytest.raises(OutcomeUnknownError):
        ep.cards.charge("ce1", 5, "o1")
    assert len(gw.requests) == 1


def test_server_error_on_money_call_is_unknown_and_not_retried(gw, ep):
    gw.reply({"message": "boom"}, status=502)
    with pytest.raises(OutcomeUnknownError) as info:
        ep.cards.charge("ce1", 5, "o1")
    assert info.value.status_code == 502 and len(gw.requests) == 1


def test_garbage_success_body_on_money_call_is_unknown(gw, ep):
    gw.reply(b"<html>ok</html>")
    with pytest.raises(OutcomeUnknownError):
        ep.payments.create(1, "o")


def test_connection_refused_is_retried_because_nothing_was_sent(gw, ep):
    gw.fail(httpx.ConnectError("refused")).reply({"status": "success", "redirect_url": "u"})
    assert ep.payments.create(1, "o").redirect_url == "u"
    assert len(gw.requests) == 2
    assert gw.form(0) == gw.form(1)


def test_connection_failures_give_up(gw, ep):
    for _ in range(3):
        gw.fail(httpx.ConnectTimeout("t"))
    with pytest.raises(NotSentError):
        ep.payments.create(1, "o")
    assert len(gw.requests) == 3


def test_rate_limit_is_retried_even_for_payments(gw, ep):
    gw.reply({"message": "slow down"}, status=429).reply({"status": "success", "redirect_url": "u"})
    assert ep.payments.create(1, "o").redirect_url == "u"


def test_safe_calls_retry_server_errors_and_timeouts(gw, ep):
    gw.reply(status=503).fail(httpx.ReadTimeout("t")).reply({"status": "success", "transaction": "te1"})
    assert ep.payments.status("te1").paid
    assert len(gw.requests) == 3


def test_safe_calls_give_up(gw, ep):
    for _ in range(3):
        gw.fail(httpx.ReadTimeout("t"))
    with pytest.raises(TransportError) as info:
        ep.payments.status("te1")
    assert not isinstance(info.value, OutcomeUnknownError)


def test_client_errors_are_not_retried(gw, ep):
    gw.reply({"detail": "bad"}, status=400)
    with pytest.raises(HTTPStatusError):
        ep.payments.status("te1")
    assert len(gw.requests) == 1
