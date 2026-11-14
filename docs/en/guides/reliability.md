# Reliability

Networks fail in two very different ways, and a payment client has to tell them apart:

- **Nothing was sent.** The connection was refused or never opened. Trying again is harmless.
- **Something was sent, but no clear answer came back.** A timeout, a dropped connection or a 5xx error after the request left your server. Epoint may have charged the card. Sending the same request again could charge it twice.

The SDK sorts every call into one of two groups and applies different rules.

## Two kinds of calls

Calls that move money
: `payments.create`, `payments.reverse`, `payments.hold`, `payments.capture`, `cards.register`, `cards.register_and_pay`, `cards.charge`, `cards.payout`, all `split` calls, `installments.create`, `wallets.pay`, all `widgets` calls, `invoices.create`, `invoices.update`, `invoices.send_sms`, `invoices.send_email`, `transfers.create`, and `request()` unless you pass `safe=True`.

Calls that only read
: `payments.status`, `cards.status`, `installments.plans`, `wallets.list`, `invoices.get`, `invoices.list`, `transfers.status` and `heartbeat`.

## What happens on each failure

| Failure | Calls that move money | Calls that only read |
| --- | --- | --- |
| Connection refused, connect timeout, pool timeout | Retried, then `NotSentError` | Retried, then `NotSentError` |
| Read timeout, dropped connection after sending | **Not retried**, `OutcomeUnknownError` | Retried, then `TransportError` |
| HTTP 429 | Retried, then `HTTPStatusError` | Retried, then `HTTPStatusError` |
| HTTP 500, 502, 503, 504 | **Not retried**, `OutcomeUnknownError` | Retried, then `HTTPStatusError` |
| Other 5xx | `OutcomeUnknownError` | `HTTPStatusError` |
| 2xx with a body that is not JSON | `OutcomeUnknownError` | `HTTPStatusError` |
| Other 4xx | `HTTPStatusError` | `HTTPStatusError` |
| JSON with `status: error` | `GatewayError` | `GatewayError` |

HTTP 429 means Epoint did not process the request, so it is retried even for payments.

## How long the SDK waits

`max_retries` (default 2) is the number of extra attempts. Before attempt `n` (counting from 0) the SDK waits

```text
min(backoff_cap, backoff_base * 2 ** n) + random(0, backoff_base / 2)
```

seconds. With the defaults that is about 0.5, then 1 second. The random part keeps many workers from retrying at the same moment.

Each attempt waits at most `connect_timeout` (default 10) seconds to connect and `timeout` (default 30) seconds for each read and write.

```python
ep = Epoint(timeout=15, connect_timeout=5, max_retries=3, backoff_base=0.3, backoff_cap=4)
```

`max_retries=0` turns retries off completely.

## Handling OutcomeUnknownError

The exception carries the `order_id`. Do not create a new order id and do not resend the request. Find out what happened first:

```python
from epoint_sdk import OutcomeUnknownError

try:
    tx = ep.cards.charge(card_id, "9.90", "SUB-1001-3")
except OutcomeUnknownError as exc:
    queue_check(exc.order_id)
```

Later, a job looks the payment up. For payments that went through the hosted page you have the `transaction` id and can call `payments.status()`. For a direct card charge, wait for the callback or retry **with the same order id**: Epoint refuses an order id it has already accepted, so a second charge cannot happen. A `GatewayError` on that retry tells you the first attempt reached Epoint, and the callback tells you how it ended.

## Retrying safely yourself

1. Store the order id before the first call.
2. On `NotSentError`, retry with the same order id whenever you like.
3. On `OutcomeUnknownError`, check first. Retry only with the same order id.
4. Never generate a new order id to "get past" an error. That is how double charges happen.

## Request size limits

- Text fields are checked before sending: `order_id` up to 255 characters, `description` up to 1000, phones up to 32, e-mails up to 254, IBAN up to 34.
- Callback `data` over 64 KB and signatures over 128 characters are rejected before any hashing, so a huge forged request cannot keep your server busy.
