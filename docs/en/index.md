# Epoint Python SDK

A typed Python client for the [Epoint](https://epoint.az) payment gateway in Azerbaijan. It covers every Epoint endpoint, works in both sync and async code, checks callback signatures for you and is built so that a payment is never sent twice by accident.

```python
from epoint_sdk import Epoint

with Epoint("i000000001", "PRIVATE_KEY",
            success_url="https://shop.az/ok", error_url="https://shop.az/fail") as ep:
    checkout = ep.payments.create("19.90", "ORDER-1042", description="Pro plan")
    print(checkout.redirect_url)
```

The customer opens `redirect_url`, pays on the Epoint page and comes back to your site. Epoint then sends a signed callback to your server, and one line turns it into a typed result:

```python
tx = ep.verify_callback(request.POST)
if tx.paid:
    fulfil(tx.order_id, tx.amount, tx.transaction)
```

## What the SDK gives you

- **Every endpoint.** Card payments, saved cards, payouts, refunds, pre-authorisation, split payments, installments, wallets, Apple Pay and Google Pay, invoices and B2B bank transfers.
- **Signed requests and callbacks.** Requests are signed with your private key, and callbacks are checked in constant time before anything is read from them.
- **No double charges.** A call that moves money is never retried after an unclear failure. You get an `OutcomeUnknownError` with the `order_id` instead, so you can check before trying again.
- **Exact amounts.** Amounts are `Decimal` from start to finish. `1.005`, `0`, `NaN` and `True` are rejected before anything leaves your server.
- **Sync and async.** `Epoint` and `AsyncEpoint` have the same methods.
- **Configuration your way.** Keys and settings come from code, `EPOINT_*` environment variables or a config file.

## Where to start

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Installation
:link: installation
:link-type: doc

Set up a virtual environment and install the package on Linux, macOS or Windows.
:::

:::{grid-item-card} Merchant account and keys
:link: keys
:link-type: doc

What the public and private keys are, where they come from and how to keep them safe.
:::

:::{grid-item-card} Quickstart
:link: quickstart
:link-type: doc

Your first payment, step by step, from the request to the confirmed callback.
:::

:::{grid-item-card} Callbacks
:link: guides/callbacks
:link-type: doc

How to confirm a payment the right way and what every field of a result means.
:::

:::{grid-item-card} Examples
:link: examples/django
:link-type: doc

Complete checkout and callback code for Django, FastAPI and Flask.
:::

:::{grid-item-card} API reference
:link: reference/api
:link-type: doc

Every class, method and setting in one place.
:::
::::

## Requirements

Python 3.10 to 3.13. The SDK depends on [httpx](https://www.python-httpx.org/), [goodconf](https://github.com/lincolnloop/goodconf), pydantic and PyYAML. You also need an Epoint merchant account, or the [local sandbox](guides/testing.md) while you build.

```{toctree}
:hidden:
:caption: Getting started

installation
keys
quickstart
configuration
```

```{toctree}
:hidden:
:caption: Guides

guides/payments
guides/callbacks
guides/refunds
guides/preauth
guides/saved-cards
guides/split
guides/installments
guides/wallets
guides/apple-google-pay
guides/invoices
guides/transfers
guides/async
guides/errors
guides/reliability
guides/messages
guides/security
guides/testing
```

```{toctree}
:hidden:
:caption: Examples

examples/django
examples/fastapi
examples/flask
examples/subscriptions
examples/reconciliation
```

```{toctree}
:hidden:
:caption: Reference

reference/api
reference/endpoints
reference/changelog
faq
```

```{toctree}
:hidden:
:caption: Project

development
about
```
