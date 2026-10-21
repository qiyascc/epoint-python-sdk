from __future__ import annotations

import base64
import hashlib
import json

import pytest

from epoint_sdk import SignatureError, callback_form, signing, verify_callback

from .conftest import PRIVATE


def test_signature_is_base64_of_raw_sha1():
    data = base64.b64encode(json.dumps({"a": 1}).encode()).decode()
    expected = base64.b64encode(hashlib.sha1((PRIVATE + data + PRIVATE).encode()).digest()).decode()
    assert signing.sign(PRIVATE, data) == expected
    assert len(base64.b64decode(expected)) == 20


def test_known_vector():
    data = "eyJwdWJsaWNfa2V5IjoiaTAwMDAwMDAwMSIsImFtb3VudCI6MTB9"
    digest = hashlib.sha1(f"secret{data}secret".encode()).digest()
    assert signing.sign("secret", data) == base64.b64encode(digest).decode()


def test_round_trip_and_tamper():
    data = signing.encode({"order_id": "A-1", "amount": 10.5, "name": "Əli"})
    sig = signing.sign(PRIVATE, data)
    assert signing.verify(PRIVATE, data, sig)["name"] == "Əli"
    with pytest.raises(SignatureError):
        signing.verify(PRIVATE, data, signing.sign("other", data))
    with pytest.raises(SignatureError):
        signing.verify(PRIVATE, data[:-4] + "AAAA", sig)
    assert not signing.matches(PRIVATE, data, "")
    assert not signing.matches("", data, sig)


@pytest.mark.parametrize("data", ["not base64!", base64.b64encode(b"[1,2]").decode(), base64.b64encode(b"{x").decode()])
def test_bad_data(data):
    with pytest.raises(SignatureError):
        signing.decode(data)


def test_callback_from_form():
    form = callback_form(PRIVATE, {"status": "success", "order_id": "A-1", "transaction": "te1", "amount": 12.3,
                                   "card_mask": "411111******1111"})
    tx = verify_callback(PRIVATE, {"data": [form["data"]], "signature": form["signature"]})
    assert tx.paid and tx.order_id == "A-1" and str(tx.amount) == "12.30" and tx.card_mask.endswith("1111")
    with pytest.raises(SignatureError):
        verify_callback(PRIVATE, {"data": form["data"]})
    with pytest.raises(SignatureError):
        verify_callback("wrong", form["data"], form["signature"])
