# Mutabakat ve iadeler

Callback'ler gecikebilir veya kaybolabilir. Bu örnek, sonucu bilinmeyen siparişleri bulup Epoint'e soran bir görev ve iadeler için bir yönetici işlemi ekler.

## Mutabakat görevi

Birkaç dakikada bir cron, Celery beat veya herhangi bir zamanlayıcıyla çalıştırın:

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

Sipariş modelinde `updated_at = models.DateTimeField(auto_now=True)` alanı olduğu varsayılıyor.

Notlar:

- `payments.status()` bir okuma çağrısıdır, bu yüzden SDK onu zaten birkaç kez yeniden dener. `TransportError` hem `NotSentError` durumunu hem de sürekli zaman aşımına uğrayan bir okumayı kapsar. Görev bir sonraki çalışmasında yeniden dener.
- Hâlâ beklemede olan bir işleme dokunulmaz. Epoint kesin bir durum verene kadar hiçbir karar alınmaz.
- İstek Epoint yanıt vermeden önce başarısız olduysa siparişin işlem kimliği yoktur ve bu yolla sorgulanamaz. Bu siparişlere elle bakın veya callback'i bekleyin.

## İade işlemi

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

Tutar olarak `None` verilirse ödemenin tamamı iptal edilir. Sonucu bilinmeyen bir iadeyi aynı görev kontrol eder: `payments.status()` `returned` gösterdiği anda sipariş iade edildi olarak işaretlenir.

## Günlük rapor

```python
from decimal import Decimal


def daily_report(day):
    orders = Order.objects.filter(paid_at__date=day)
    total = sum((o.total for o in orders), start=Decimal("0"))
    return {"count": orders.count(), "total": total}
```

Bu toplamı, Epoint panelinizde aynı gün için listelenen ödemelerle karşılaştırın. Bir fark, sisteminizin kaçırdığı bir siparişe işaret eder.
