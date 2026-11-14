# Callbacks

The callback is how Epoint tells your server what happened to a payment. It is the only part of the flow you can trust, because it is signed with your private key. This page shows how to receive it, check it and act on it.

## What Epoint sends

Epoint makes a `POST` request to the result address registered for your merchant account. The body is a form with two fields:

`data`
: The result as JSON, encoded with base64.

`signature`
: `base64(sha1(private_key + data + private_key))`, computed with your private key.

Because only you and Epoint know the private key, a matching signature proves that Epoint produced this exact `data`.

## Verifying a callback

Pass the whole form to `verify_callback`:

```python
from epoint_sdk import SignatureError

try:
    tx = ep.verify_callback(request.POST)
except SignatureError:
    return bad_request()
```

It works with any mapping: Django's `request.POST`, Flask's `request.form`, the result of `await request.form()` in Starlette and FastAPI, or a plain `dict`. If a field arrives as a list, the first value is used.

If you already have the two values separately, pass them as two arguments:

```python
tx = ep.verify_callback(data, signature)
```

Without a client, for example in a small worker, use the module level function with the private key:

```python
from epoint_sdk import verify_callback

tx = verify_callback(PRIVATE_KEY, request.POST)
```

### What is checked, in this order

1. Both `data` and `signature` are present and not empty.
2. `data` is at most 64 KB and `signature` at most 128 characters. Anything larger is rejected before hashing.
3. The signature matches, compared in constant time.
4. `data` is valid base64 that decodes to a JSON object.

Any failure raises `SignatureError` and no field of the callback is read. Answer such a request with HTTP 400 and do nothing else.

## Reading the result

`verify_callback` returns a {py:class}`~epoint_sdk.Transaction`, the same type `payments.status()` returns. `Callback` is another name for it.

| Field | Meaning |
| --- | --- |
| `status` | A {py:class}`~epoint_sdk.Status`: `new`, `success`, `failed`, `error`, `returned`, `server_error` or `unknown` |
| `transaction` | Epoint's transaction id |
| `order_id` | Your order id |
| `amount` | The amount as `Decimal`, or `None` |
| `code` | The bank response code, if Epoint sent one |
| `message` | A human readable message from Epoint or the bank |
| `bank_transaction` | The bank's transaction id |
| `bank_response` | The raw bank response |
| `operation_code` | Which operation this result is about, see below |
| `rrn` | Retrieval reference number from the card network |
| `card_id` | The saved card id, for card registration flows |
| `card_name` | Card holder name, if Epoint sent it |
| `card_mask` | Masked card number such as `411111******1111` |
| `split_amount` | The partner's share for split payments |
| `other_attr` | The extra data you sent with the payment |
| `trace_id` | Epoint's trace id |
| `raw` | The decoded JSON as a dict |

The status is turned into helper properties:

```python
tx.paid       # status is success
tx.failed     # status is failed or error
tx.returned   # status is returned
tx.pending    # new, server_error or unknown
tx.final      # not pending
```

An unknown status value never raises. It becomes `Status.UNKNOWN`, which counts as pending, so your code waits instead of guessing.

### Operation codes

`operation_code` tells you which kind of operation the callback belongs to. Compare it with {py:class}`~epoint_sdk.OperationCode`:

| Value | Constant | Operation |
| --- | --- | --- |
| `001` | `OperationCode.CARD_REGISTRATION` | A card was saved without a payment |
| `100` | `OperationCode.PAYMENT` | A payment |
| `200` | `OperationCode.REGISTRATION_WITH_PAYMENT` | A card was saved together with a payment |

```python
from epoint_sdk import OperationCode

if tx.operation_code == OperationCode.CARD_REGISTRATION:
    save_card(tx.card_id, tx.card_mask)
```

## Matching the callback to your order

A correct signature only proves that Epoint sent the callback. It does not prove that it is about the order you are looking at. Always compare it with what you stored:

```python
order = Order.objects.get(number=tx.order_id)

if not tx.matches(order_id=order.number, amount=order.total, transaction=order.epoint_transaction):
    log.warning("Callback does not match order %s", order.number)
    return HttpResponse("OK")
```

`matches()` returns `False` when:

- `order_id` is given and differs,
- `transaction` is given, the callback has a transaction id, and they differ,
- `amount` is given and differs. The amount is compared as `Decimal`, so `"19.9"` and `Decimal("19.90")` are equal.

Arguments you leave out are not checked.

## Making the handler safe to repeat

Treat every callback as something that can arrive more than once, and make the handler idempotent:

```python
if tx.paid and order.status != "paid":
    order.mark_paid(transaction=tx.transaction)
```

Do the work inside a database transaction, lock the order row if your database supports it, and only then answer.

## Answering

Answer quickly with HTTP 200 once you have recorded the result. Heavy work such as sending e-mails or building invoices belongs in a background job, so a slow mail server does not turn into a slow or failed callback.

Callbacks are server to server requests, so they carry no CSRF token. Exempt the callback view from CSRF protection, as the [Django example](../examples/django.md) does.

## The success page is not a confirmation

When the customer lands on your `success_url`, show a friendly "we are confirming your payment" page and read the order status from your own database. If the callback has not arrived yet, poll your own backend from the page, or call `ep.payments.status(transaction)` on the server.

## When a callback never comes

Networks fail. Run a periodic job that looks for orders that stayed pending too long and asks Epoint directly. The [reconciliation example](../examples/reconciliation.md) shows a complete job.

## Building a callback in tests

`callback_form` builds a correctly signed form from a payload, exactly as Epoint would:

```python
from epoint_sdk import callback_form

form = callback_form(PRIVATE_KEY, {
    "status": "success",
    "order_id": "ORDER-1042",
    "transaction": "te001",
    "amount": 19.9,
})
response = client.post("/payments/epoint/callback/", form)
```

More in [Testing](testing.md).
