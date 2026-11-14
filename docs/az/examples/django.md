# Django

Tam Django inteqrasiyası: sifarişlər üçün model, ödənişə başlayan view, onu təsdiqləyən callback view-u və müştərinin qayıtdığı səhifələr.

## Ayarlar

Açarları mühit dəyişənlərində saxlayın:

```console
$ export EPOINT_PUBLIC_KEY=i000000001
$ export EPOINT_PRIVATE_KEY=your-private-key
$ export EPOINT_SUCCESS_URL=https://shop.az/payments/ok/
$ export EPOINT_ERROR_URL=https://shop.az/payments/fail/
```

## Bütün layihə üçün bir klient

`payments/epoint.py`:

```python
from epoint_sdk import Epoint

epoint = Epoint()
```

Bu modul import ediləndə bir bağlantı hovuzu olan bir klient yaranır. Açarlardan biri yoxdursa, Django ödəniş zamanı yox, elə işə düşəndə `ConfigurationError` ilə dayanır.

## Model

`payments/models.py`:

```python
from django.db import models


class Order(models.Model):
    class State(models.TextChoices):
        NEW = "new"
        PENDING = "pending"
        PAID = "paid"
        FAILED = "failed"
        REFUNDED = "refunded"
        NEEDS_CHECK = "needs_check"

    number = models.CharField(max_length=64, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    title = models.CharField(max_length=200)
    state = models.CharField(max_length=16, choices=State.choices, default=State.NEW)
    attempt = models.PositiveIntegerField(default=0)
    epoint_order_id = models.CharField(max_length=80, blank=True)
    epoint_transaction = models.CharField(max_length=64, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
```

`epoint_order_id` Epoint-ə göndərilən identifikatordur. O, sifariş nömrəsi və cəhd sayğacından ibarətdir, beləliklə müştəri kart rədd ediləndən sonra yenidən cəhd edə bilir.

## Ödənişə başlamaq

`payments/views.py`:

```python
from django.db import transaction
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from epoint_sdk import (
    GatewayError,
    InvalidRequestError,
    NotSentError,
    OutcomeUnknownError,
    SignatureError,
)

from .epoint import epoint
from .models import Order


@require_POST
def pay(request, number):
    order = get_object_or_404(Order, number=number, state__in=[Order.State.NEW, Order.State.FAILED])

    order.attempt += 1
    order.epoint_order_id = f"{order.number}-{order.attempt}"
    order.state = Order.State.PENDING
    order.save(update_fields=["attempt", "epoint_order_id", "state"])

    try:
        checkout = epoint.payments.create(order.total, order.epoint_order_id, description=order.title)
    except (InvalidRequestError, GatewayError):
        order.state = Order.State.FAILED
        order.save(update_fields=["state"])
        return render(request, "payments/error.html", {"order": order})
    except NotSentError:
        order.state = Order.State.NEW
        order.save(update_fields=["state"])
        return render(request, "payments/retry_later.html", {"order": order})
    except OutcomeUnknownError:
        order.state = Order.State.NEEDS_CHECK
        order.save(update_fields=["state"])
        return render(request, "payments/checking.html", {"order": order})

    order.epoint_transaction = checkout.transaction or ""
    order.save(update_fields=["epoint_transaction"])
    return redirect(checkout.redirect_url)
```

Cəhd identifikatoru sorğudan **əvvəl** saxlanılır, ona görə sorğu yarımçıq qalsa da məlum olur.

## Callback

```python
@csrf_exempt
@require_POST
def callback(request):
    try:
        tx = epoint.verify_callback(request.POST)
    except SignatureError:
        return HttpResponseBadRequest()

    with transaction.atomic():
        order = (
            Order.objects.select_for_update()
            .filter(epoint_order_id=tx.order_id)
            .first()
        )
        if order is None or not tx.matches(order_id=order.epoint_order_id, amount=order.total):
            return HttpResponse("OK")

        if tx.paid and order.state != Order.State.PAID:
            order.state = Order.State.PAID
            order.epoint_transaction = tx.transaction or order.epoint_transaction
            order.paid_at = timezone.now()
            order.save(update_fields=["state", "epoint_transaction", "paid_at"])
        elif tx.failed and order.state == Order.State.PENDING:
            order.state = Order.State.FAILED
            order.save(update_fields=["state"])
        elif tx.returned:
            order.state = Order.State.REFUNDED
            order.save(update_fields=["state"])

    return HttpResponse("OK")
```

Bu kod nə edir:

- `csrf_exempt` mütləqdir, çünki Epoint serverinin CSRF tokeni yoxdur.
- İmzası səhv olan sorğuya HTTP 400 qaytarılır və başqa heç nə baş vermir.
- `select_for_update()` sifariş sətrini kilidləyir, ona görə eyni callback-in iki nüsxəsi sifarişi iki dəfə ödənilmiş kimi qeyd edə bilmir.
- `matches()` callback-in məhz bu sifarişə və bu məbləğə aid olduğunu yoxlayır.
- Hər vəziyyət dəyişikliyi yalnız bir dəfə baş verir, ona görə təkrar gələn callback zərərsizdir.

E-poçt göndərmək və digər yavaş işləri tranzaksiya təsdiqlənəndən sonra siqnal və ya tapşırıq növbəsi ilə edin, məsələn `transaction.on_commit()` vasitəsilə.

## Qayıdış səhifələri

```python
def payment_ok(request):
    return render(request, "payments/ok.html")


def payment_fail(request):
    return render(request, "payments/fail.html")


def order_state(request, number):
    order = get_object_or_404(Order, number=number)
    return HttpResponse(order.state)
```

`ok.html` öz-özünə "ödənildi" deməməlidir. "Ödənişinizi təsdiqləyirik" yazın və bir az JavaScript ilə `order_state` ünvanını cavab `paid` olana qədər dövri olaraq soruşun.

## URL-lər

```python
from django.urls import path

from . import views

urlpatterns = [
    path("orders/<str:number>/pay/", views.pay, name="order-pay"),
    path("orders/<str:number>/state/", views.order_state, name="order-state"),
    path("payments/epoint/callback/", views.callback, name="epoint-callback"),
    path("payments/ok/", views.payment_ok, name="payment-ok"),
    path("payments/fail/", views.payment_fail, name="payment-fail"),
]
```

`https://shop.az/payments/epoint/callback/` ünvanını tacir hesabınızın nəticə ünvanı kimi qeyd etdirin.

## Test

```python
from decimal import Decimal

from django.test import TestCase
from epoint_sdk import callback_form

from payments.epoint import epoint
from payments.models import Order


class CallbackTests(TestCase):
    def test_paid(self):
        order = Order.objects.create(number="A1", total=Decimal("19.90"), title="Pro",
                                     state="pending", epoint_order_id="A1-1")
        form = callback_form(epoint.settings.private_key.get_secret_value(), {
            "status": "success", "order_id": "A1-1", "transaction": "te1", "amount": "19.90",
        })
        response = self.client.post("/payments/epoint/callback/", form)
        self.assertEqual(response.status_code, 200)
        order.refresh_from_db()
        self.assertEqual(order.state, "paid")
```
