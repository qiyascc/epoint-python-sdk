# Errors

Every exception the SDK raises inherits from `EpointError`, so one `except` can catch them all. Each one carries a readable `message`.

```text
EpointError
├── ConfigurationError
├── InvalidRequestError        (also a ValueError)
├── SignatureError
├── TransportError
│   ├── NotSentError
│   └── OutcomeUnknownError
├── HTTPStatusError
└── GatewayError
```

## When each one is raised

| Exception | When | What to do |
| --- | --- | --- |
| `ConfigurationError` | A key is missing, or `base_url` is plain `http` outside localhost | Fix the configuration. It happens when the client is created |
| `InvalidRequestError` | An argument is wrong: bad amount, empty order id, text too long, split share larger than the total, months not a positive int | Fix the input. Nothing was sent |
| `SignatureError` | A callback has no data or signature, a wrong signature, too much data or data that is not base64 JSON | Answer HTTP 400 and ignore the request |
| `NotSentError` | The connection failed before anything was sent, after all retries | Safe to try again later with the same order id |
| `OutcomeUnknownError` | A call that moves money reached Epoint but no clear answer came back | Do **not** blindly retry. Check the status first |
| `TransportError` | A read call (status, lists) failed on every retry | Try again later |
| `HTTPStatusError` | Epoint answered with an HTTP error, or with a body that is not JSON | Log it, look at `status_code` and `body` |
| `GatewayError` | Epoint answered with `status: error` | Read `code` and the message. Often a business rule, such as a reused order id |

## Attributes

`TransportError`, `NotSentError` and `OutcomeUnknownError`
: `path` is the URL that was called, `order_id` is the order the call was for, when there was one. `OutcomeUnknownError` also has `status_code` when the problem was a 5xx answer.

`HTTPStatusError`
: `status_code`, `body` (parsed JSON or the first 200 characters of text) and `path`.

`GatewayError`
: `code` (Epoint's error code or `None`), `trace_id`, `status_code`, `payload` (the full answer) and `path`. `str(exc)` looks like `[CODE] message (trace TRACE_ID)`.

## A declined card is not an exception

Calls that charge immediately, `cards.charge()`, `cards.payout()` and `split.charge()`, and `payments.status()` return a `Transaction` for a declined or failed payment instead of raising. Check `tx.paid` and `tx.failed`. Only a request that Epoint refuses without creating a transaction raises `GatewayError`.

## A typical checkout handler

```python
from epoint_sdk import (
    GatewayError,
    InvalidRequestError,
    NotSentError,
    OutcomeUnknownError,
)

def start_payment(order):
    try:
        checkout = ep.payments.create(order.total, order.attempt_id, description=order.title)
    except InvalidRequestError as exc:
        return show_error(f"Cannot start the payment: {exc.message}")
    except NotSentError:
        return show_error("The payment service is not reachable. Please try again in a minute.")
    except OutcomeUnknownError:
        order.mark_needs_check()
        return show_error("We could not confirm the payment request. We will check it and let you know.")
    except GatewayError as exc:
        log.warning("Epoint refused %s: %s", order.attempt_id, exc)
        return show_error("The payment could not be started.")
    order.epoint_transaction = checkout.transaction
    order.save()
    return redirect(checkout.redirect_url)
```

## Changing the messages

All messages come from a YAML file inside the package and can be replaced or translated. See [Messages](messages.md).
