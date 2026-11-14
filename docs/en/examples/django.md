# Django

A complete Django integration: a model for orders, a view that starts the payment, a callback view that confirms it, and the pages the customer returns to.

## Settings

Keep the keys in the environment:

```console
$ export EPOINT_PUBLIC_KEY=i000000001
$ export EPOINT_PRIVATE_KEY=your-private-key
$ export EPOINT_SUCCESS_URL=https://shop.az/payments/ok/
$ export EPOINT_ERROR_URL=https://shop.az/payments/fail/
```

## One client for the whole project

`payments/epoint.py`:

```python
from epoint_sdk import Epoint

epoint = Epoint()
```

Importing this module creates one client with one connection pool. If a key is missing, Django fails at start up with `ConfigurationError`, not during a checkout.

## The model

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

`epoint_order_id` is the id sent to Epoint. It is the order number plus an attempt counter, so a customer can try again after a declined card.

## Starting the payment

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

The attempt id is saved **before** the call, so it is known even if the call fails halfway.

## The callback

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

What this does:

- `csrf_exempt` is required, because Epoint's server has no CSRF token.
- A bad signature gets HTTP 400 and nothing else happens.
- `select_for_update()` locks the order row, so two copies of the same callback cannot both mark it paid.
- `matches()` makes sure the callback is about this order and this amount.
- Each state change happens only once, so a repeated callback is harmless.

Send e-mails and other slow work from a signal or a task queue after the transaction commits, for example with `transaction.on_commit()`.

## The return pages

```python
def payment_ok(request):
    return render(request, "payments/ok.html")


def payment_fail(request):
    return render(request, "payments/fail.html")


def order_state(request, number):
    order = get_object_or_404(Order, number=number)
    return HttpResponse(order.state)
```

`ok.html` should not say "paid" on its own. Say "we are confirming your payment" and poll `order_state` with a little JavaScript until it turns `paid`.

## URLs

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

Register `https://shop.az/payments/epoint/callback/` as the result address of your merchant account.

## A test

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
