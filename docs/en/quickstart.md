# Quickstart

This page takes one payment from start to finish: create the request, send the customer to Epoint, and confirm the result on your server. It assumes you have [installed](installation.md) the package and have your [keys](keys.md).

## How a payment flows

1. Your server asks Epoint for a payment page. Epoint answers with a `redirect_url` and a `transaction` id.
2. You redirect the customer to `redirect_url`. They enter their card on the Epoint page.
3. Epoint sends the customer back to your success or error page.
4. Epoint posts a signed callback to your result address. **This** is the moment you mark the order as paid.

Step 3 is only for the customer. Anyone can open your success page by hand, so it proves nothing. Step 4 is signed with your private key, so it can be trusted once the signature is checked.

## Step 1. Create the client

```python
from epoint_sdk import Epoint

ep = Epoint(
    "i000000001",
    "PRIVATE_KEY",
    success_url="https://shop.az/payment/ok",
    error_url="https://shop.az/payment/fail",
)
```

- The first two arguments are your public and private key.
- `success_url` and `error_url` become the defaults for every payment. You can still override them per call.
- The language of the payment page defaults to `az` and the currency to `AZN`.

Create one client when your application starts and reuse it. It keeps an HTTP connection pool open. Call `ep.close()` when you shut down, or use it in a `with` block for short scripts.

## Step 2. Create the payment

```python
checkout = ep.payments.create(
    "19.90",
    "ORDER-1042",
    description="Pro plan, 1 month",
)
```

Line by line:

- `"19.90"` is the amount. Pass a string or a `Decimal`, not a float, so you never meet rounding surprises. More than two decimal places, zero, negative numbers, `NaN` and booleans are rejected with `InvalidRequestError` before the request is sent.
- `"ORDER-1042"` is your order id. It must be unique for every payment. Epoint refuses an id it has already seen, and that is what protects you from charging twice.
- `description` is shown to the customer on the payment page.

The result is a `Redirect`:

```python
>>> checkout
Redirect(redirect_url='https://epoint.az/...', transaction='te001...', trace_id=None, message=None)
```

Save `checkout.transaction` next to your order. You need it to check the status or to refund later.

## Step 3. Send the customer to Epoint

How you redirect depends on your framework. In Django:

```python
from django.shortcuts import redirect

return redirect(checkout.redirect_url)
```

## Step 4. Confirm the payment in the callback

Epoint posts two form fields to your result address: `data` and `signature`. Pass the whole form to `verify_callback`:

```python
from epoint_sdk import SignatureError

def epoint_callback(request):
    try:
        tx = ep.verify_callback(request.POST)
    except SignatureError:
        return HttpResponseBadRequest()

    order = Order.objects.get(number=tx.order_id)
    if tx.paid and tx.matches(order_id=order.number, amount=order.total):
        order.mark_paid(transaction=tx.transaction)
    return HttpResponse("OK")
```

- `verify_callback` checks the signature in constant time and only then decodes the data. A forged or broken callback raises `SignatureError`.
- `tx.paid` is `True` only when the status is `success`.
- `tx.matches(...)` checks that the callback is about the order and amount you expect. A valid callback for a different, cheaper order must not unlock this one.

The full, production ready version of this view is in the [Django example](examples/django.md).

## Step 5. Ask the gateway when in doubt

If a callback never arrives, ask Epoint directly:

```python
tx = ep.payments.status(checkout.transaction)
print(tx.status, tx.paid, tx.pending)
```

`status()` never raises for a declined card. It returns a `Transaction` whose `failed` property is `True`.

## Step 6. Close the client

```python
ep.close()
```

or use the client as a context manager:

```python
with Epoint() as ep:
    ...
```

## What next

- [Configuration](configuration.md) shows every setting and how to load keys from the environment or a file.
- [Payments](guides/payments.md) covers the other options of `create`, the signed HTML form and installments.
- [Callbacks](guides/callbacks.md) explains every field of a result.
- [Errors](guides/errors.md) and [Reliability](guides/reliability.md) explain what to do when the network fails.
