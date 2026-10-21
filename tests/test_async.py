from __future__ import annotations

import httpx
import pytest

from epoint_sdk import OutcomeUnknownError


async def test_async_payment_and_status(gw, aep):
    gw.reply({"status": "success", "redirect_url": "u", "transaction": "te1"})
    gw.reply({"status": "success", "transaction": "te1", "amount": 1})
    assert (await aep.payments.create(1, "o")).transaction == "te1"
    assert (await aep.payments.status("te1")).paid
    await aep.close()


async def test_async_never_resends(gw, aep):
    gw.fail(httpx.ReadTimeout("t"))
    with pytest.raises(OutcomeUnknownError):
        await aep.cards.charge("c", 1, "o")
    assert len(gw.requests) == 1


async def test_async_heartbeat_and_callback(gw, aep):
    from epoint_sdk import callback_form

    from .conftest import PRIVATE

    gw.reply({"status": "ok"})
    assert await aep.heartbeat()
    form = callback_form(PRIVATE, {"status": "success", "order_id": "o"})
    assert aep.verify_callback(form).paid
