# Refunds and reversals

There are two ways to give money back with Epoint, and they are not the same thing:

- **Reversal** cancels or refunds an existing payment, in full or in part. The money goes back to the card that paid.
- **Payout** sends money to a saved card that was registered for payouts. It is not tied to an earlier payment. See [Saved cards](saved-cards.md#payouts).

For a normal "the customer wants their money back" case, use a reversal.

## Full reversal

```python
result = ep.payments.reverse("te001234")
if result.ok:
    order.mark_refunded()
```

Pass the `transaction` id you stored when the payment was created.

## Partial reversal

Pass an amount as the second argument:

```python
result = ep.payments.reverse("te001234", "5.00")
```

The amount follows the same rules as for payments: above zero, at most two decimal places.

```{note}
The amount is the second positional argument. Its parameter name is `amount_`, so write `reverse(transaction, "5.00")` and not `reverse(transaction, amount="5.00")`.
```

`currency` and `language` can be passed as keyword arguments and default to your settings.

## The result

`reverse()` returns a {py:class}`~epoint_sdk.Result`:

| Field | Meaning |
| --- | --- |
| `status` | A `Status` value |
| `ok` | `True` when the status is `success` |
| `transaction` | The transaction id from the answer |
| `message` | Message from the gateway |
| `trace_id` | Epoint's trace id |
| `raw` | The full JSON answer |

If Epoint refuses the reversal outright, for example because the payment was already returned, the SDK raises `GatewayError` with Epoint's `code` and message:

```python
from epoint_sdk import GatewayError

try:
    ep.payments.reverse("te001234")
except GatewayError as exc:
    log.warning("Refund refused: %s", exc)
```

After a successful full reversal, `payments.status(transaction)` reports the payment as `returned`.

## A reversal is never sent twice

A reversal moves money, so the SDK treats it like a payment: if the request times out or the connection drops after it was sent, it is **not** retried. You get `OutcomeUnknownError` instead. Check the payment status before you try again:

```python
from epoint_sdk import OutcomeUnknownError

try:
    ep.payments.reverse(tx_id, "5.00")
except OutcomeUnknownError:
    tx = ep.payments.status(tx_id)
    if tx.returned:
        ...
```

Read [Reliability](reliability.md) for the full rules.

## Recording refunds

Keep a refunds table next to your orders: amount, time, who asked for it and the `Result` you got back. Partial refunds add up, and you need the history when a customer asks what happened.

A complete refund flow is part of the [reconciliation example](../examples/reconciliation.md).
