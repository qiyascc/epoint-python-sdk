# Üzləşmə və geri qaytarma

Callback-lər gecikə və ya itə bilər. Bu nümunə nəticəsi naməlum olan sifarişləri tapıb Epoint-dən soruşan tapşırığı, həmçinin geri qaytarma üçün admin əməliyyatını əlavə edir.

## Üzləşmə tapşırığı

Onu bir neçə dəqiqədən bir cron, Celery beat və ya istənilən planlayıcı ilə işə salın:

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

Burada sifariş modelində `updated_at = models.DateTimeField(auto_now=True)` sahəsinin olduğu güman edilir.

Qeydlər:

- `payments.status()` oxuma sorğusudur, ona görə SDK onu artıq bir neçə dəfə təkrarlayır. `TransportError` həm `NotSentError` halını, həm də hər dəfə vaxtı bitən oxuma sorğusunu əhatə edir. Tapşırıq sadəcə növbəti dəfə yenidən cəhd edir.
- Hələ gözləmədə olan tranzaksiyaya toxunulmur. Epoint yekun status verməyincə heç nə qərara alınmır.
- Sorğu Epoint cavab verməzdən əvvəl uğursuz olubsa, sifarişin tranzaksiya identifikatoru olmur və onu bu yolla axtarmaq mümkün deyil. Belə sifarişlərə əllə baxın və ya callback-i gözləyin.

## Geri qaytarma əməliyyatı

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

Məbləğ kimi `None` verilsə, ödəniş tam ləğv olunur. Nəticəsi naməlum qalan geri qaytarmanı eyni tapşırıq yoxlayır: `payments.status()` `returned` göstərən kimi sifariş geri qaytarılmış kimi qeyd olunur.

## Gündəlik hesabat

```python
from decimal import Decimal


def daily_report(day):
    orders = Order.objects.filter(paid_at__date=day)
    total = sum((o.total for o in orders), start=Decimal("0"))
    return {"count": orders.count(), "total": total}
```

Bu cəmi Epoint kabinetinizdə həmin gün üçün göstərilən ödənişlərlə müqayisə edin. Fərq sisteminizin buraxdığı sifarişə işarədir.
