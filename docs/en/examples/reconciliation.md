# Reconciliation and refunds

Callbacks can be late or lost. This example adds a job that finds orders whose result is unknown and asks Epoint about them, plus an admin action for refunds.

## The reconciliation job

Run it every few minutes from cron, Celery beat or any scheduler:

```python
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from epoint_sdk import TransportError
from payments.epoint import epoint
from payments.models import Order


def reconcile():
    cutoff = timezone.now() - timedelta(minutes=10)
    stuck = Order.objects.filter(
        state__in=[Order.State.PENDING, Order.State.NEEDS_CHECK],
        updated_at__lt=cutoff,
    ).exclude(epoint_transaction="")

    for order in stuck:
        try:
            tx = epoint.payments.status(order.epoint_transaction)
        except TransportError:
            continue

        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order.pk)
            if not tx.matches(order_id=order.epoint_order_id, amount=order.total):
                order.state = Order.State.NEEDS_CHECK
            elif tx.paid:
                order.state = Order.State.PAID
                order.paid_at = order.paid_at or timezone.now()
            elif tx.failed:
                order.state = Order.State.FAILED
            elif tx.returned:
                order.state = Order.State.REFUNDED
            order.save()
```

This assumes the order model has an `updated_at = models.DateTimeField(auto_now=True)` field.

Notes:

- `payments.status()` is a read call, so the SDK already retries it a few times. `TransportError` covers both `NotSentError` and a read that kept timing out. The job simply tries again on its next run.
- A pending transaction stays pending. Nothing is decided until Epoint gives a final status.
- An order without a transaction id (the call failed before Epoint answered) cannot be looked up by transaction. Handle those by hand or wait for the callback.

## A refund action

```python
from epoint_sdk import GatewayError, OutcomeUnknownError


def refund(order, amount=None, by=None):
    try:
        result = epoint.payments.reverse(order.epoint_transaction, amount)
    except OutcomeUnknownError:
        Refund.objects.create(order=order, amount=amount or order.total, state="unknown", by=by)
        return "We could not confirm the refund. It will be checked automatically."
    except GatewayError as exc:
        Refund.objects.create(order=order, amount=amount or order.total, state="refused",
                              note=str(exc), by=by)
        return f"Epoint refused the refund: {exc.message}"

    Refund.objects.create(order=order, amount=amount or order.total,
                          state="done" if result.ok else "failed", by=by, trace_id=result.trace_id or "")
    if result.ok and amount is None:
        order.state = Order.State.REFUNDED
        order.save()
    return "Refund sent." if result.ok else "Refund failed."
```

Passing `None` as the amount reverses the full payment. A refund with an unknown outcome is checked by the same job: once `payments.status()` reports `returned`, the order is marked refunded.

## A daily report

```python
from decimal import Decimal


def daily_report(day):
    orders = Order.objects.filter(paid_at__date=day)
    total = sum((o.total for o in orders), start=Decimal("0"))
    return {"count": orders.count(), "total": total}
```

Compare this total with the payments listed in your Epoint cabinet for the same day. A difference points to an order your system missed.
