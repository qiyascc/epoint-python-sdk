# Testing your integration

You can test at three levels: unit tests with a fake gateway, integration tests against a local sandbox, and a final check with real money on the live gateway.

## Unit tests with a mock transport

Pass an `httpx.Client` with an `httpx.MockTransport` and the SDK never touches the network. The handler receives every request and returns whatever answer you need:

```python
import httpx
import pytest
from epoint_sdk import Epoint, signing

PRIVATE = "test_private_key"
sent = []

def gateway(request: httpx.Request) -> httpx.Response:
    sent.append(request)
    if request.url.path == "/api/1/request":
        return httpx.Response(200, json={
            "status": "success",
            "redirect_url": "https://epoint.az/checkout/abc",
            "transaction": "te001",
        })
    return httpx.Response(404, json={"detail": "not found"})

@pytest.fixture
def ep():
    http = httpx.Client(transport=httpx.MockTransport(gateway))
    return Epoint("i000000001", PRIVATE, http_client=http)

def test_checkout(ep):
    checkout = ep.payments.create("19.90", "ORDER-1")
    assert checkout.transaction == "te001"
```

### Looking inside a request

Requests are sent as a form with `data` and `signature`. The `gateway` above keeps every request in `sent`, so you can decode them and check what your code sent:

```python
from urllib.parse import parse_qs

def test_amount_is_sent_as_number(ep):
    ep.payments.create("19.90", "ORDER-2")
    form = {k: v[0] for k, v in parse_qs(sent[-1].content.decode()).items()}
    assert signing.matches(PRIVATE, form["data"], form["signature"])
    payload = signing.decode(form["data"])
    assert payload["amount"] == 19.9
    assert payload["order_id"] == "ORDER-2"
```

### Simulating failures

Raise an httpx exception from the handler to test your error handling:

```python
from epoint_sdk import OutcomeUnknownError

def timeout(request):
    raise httpx.ReadTimeout("slow", request=request)

def test_charge_timeout_is_not_retried():
    ep = Epoint("i000000001", PRIVATE, http_client=httpx.Client(transport=httpx.MockTransport(timeout)))
    with pytest.raises(OutcomeUnknownError) as info:
        ep.cards.charge("card-1", "5", "SUB-9")
    assert info.value.order_id == "SUB-9"
```

To keep retry tests fast, set `max_retries=0`, or small `backoff_base` and `backoff_cap` values.

## Testing the callback view

`callback_form` signs a payload exactly as Epoint does:

```python
from epoint_sdk import callback_form

def test_callback_marks_order_paid(client, order):
    form = callback_form(PRIVATE, {
        "status": "success",
        "order_id": order.number,
        "transaction": "te001",
        "amount": str(order.total),
    })
    response = client.post("/payments/epoint/callback/", form)
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == "paid"

def test_forged_callback_is_rejected(client, order):
    form = callback_form("wrong-key", {"status": "success", "order_id": order.number})
    response = client.post("/payments/epoint/callback/", form)
    assert response.status_code == 400
```

Write tests for the cases that cost money when they go wrong: a forged signature, a callback for another order, a wrong amount, a repeated callback and a failed status.

## Integration tests with epoint-sandbox

[epoint-sandbox](https://github.com/martian56/epoint-sandbox) is a community project that copies the Epoint API on your own machine: a payment page, test cards, a dashboard, and signed callbacks sent to your result address. It is not made by Epoint.

### Step 1. Start it

```console
$ docker run -d -p 8181:8181 --name epoint \
    --add-host=host.docker.internal:host-gateway \
    ghcr.io/martian56/epoint-sandbox
```

The dashboard is at `http://localhost:8181`.

### Step 2. Point the SDK at it

```console
$ export EPOINT_BASE_URL=http://localhost:8181
$ export EPOINT_PUBLIC_KEY=i000000001
$ export EPOINT_PRIVATE_KEY=sandbox_private_key_0000000001
```

`http://localhost` is allowed without `allow_insecure_http`. If the sandbox runs on another machine in your network, set `EPOINT_ALLOW_INSECURE_HTTP=true` as well, and only there.

### Step 3. Tell it where to send callbacks

Callbacks are sent from inside the container, where `localhost` is the container itself. Use `host.docker.internal` to reach your machine:

```console
$ curl -X PATCH http://localhost:8181/_sandbox/merchants/i000000001 \
    -H "Content-Type: application/json" \
    -d '{"result_url": "http://host.docker.internal:8000/payments/epoint/callback/"}'
```

### Step 4. Pay with a test card

Create a payment from your app, open `redirect_url` and pay with `4111 1111 1111 1111`, any future expiry and any CVV. The sandbox README lists more cards for declines, 3-D Secure and timeouts.

The sandbox dashboard shows every request, the decoded payload and every callback attempt with your server's answer, which makes signature problems easy to see.

## The final check on the live gateway

Before launch, make one real payment with a small amount and a real card, then refund it with `payments.reverse()`. Watch the callback arrive, check that the order is marked paid exactly once, and that the refund shows up as `returned`.
