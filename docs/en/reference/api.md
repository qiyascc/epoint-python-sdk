# API reference

This page lists the public classes and functions of `epoint_sdk`, generated from the source code. The guides explain how to use them. Everything here can be imported directly from `epoint_sdk`.

## Clients

`Epoint` is the sync client and `AsyncEpoint` the async one. Both take `public_key` and `private_key` as the first two arguments, and the keyword arguments `settings`, `config_file`, `http_client` and any setting from [Configuration](../configuration.md).

```{eval-rst}
.. autoclass:: epoint_sdk.Epoint(public_key=None, private_key=None, *, settings=None, config_file=None, http_client=None, **overrides)
   :members: heartbeat, request, verify_callback, close, sign

.. autoclass:: epoint_sdk.AsyncEpoint(public_key=None, private_key=None, *, settings=None, config_file=None, http_client=None, **overrides)
   :members: heartbeat, request, verify_callback, close, sign
```

## Namespaces

Each client has these attributes. The async client has the same methods as coroutines.

| Attribute | Class |
| --- | --- |
| `payments` | {py:class}`epoint_sdk.resources.Payments` |
| `cards` | {py:class}`epoint_sdk.resources.Cards` |
| `split` | {py:class}`epoint_sdk.resources.Split` |
| `installments` | {py:class}`epoint_sdk.resources.Installments` |
| `wallets` | {py:class}`epoint_sdk.resources.Wallets` |
| `widgets` | {py:class}`epoint_sdk.resources.Widgets` |
| `invoices` | {py:class}`epoint_sdk.resources.Invoices` |
| `transfers` | {py:class}`epoint_sdk.resources.Transfers` |

```{eval-rst}
.. autoclass:: epoint_sdk.resources.Payments
.. autoclass:: epoint_sdk.resources.Cards
.. autoclass:: epoint_sdk.resources.Split
.. autoclass:: epoint_sdk.resources.Installments
.. autoclass:: epoint_sdk.resources.Wallets
.. autoclass:: epoint_sdk.resources.Widgets
.. autoclass:: epoint_sdk.resources.Invoices
.. autoclass:: epoint_sdk.resources.Transfers
```

## Results

All result classes are frozen dataclasses. Each has a `raw` field with the full answer from Epoint.

```{eval-rst}
.. autoclass:: epoint_sdk.Redirect
   :members: redirect_url, transaction, trace_id, message, raw

.. autoclass:: epoint_sdk.Transaction
   :members: status, transaction, order_id, amount, code, message, bank_transaction, bank_response, operation_code, rrn, card_id, card_name, card_mask, split_amount, other_attr, trace_id, raw, paid, returned, failed, pending, final, matches

.. autoclass:: epoint_sdk.Result
   :members: status, transaction, message, trace_id, raw, ok

.. autoclass:: epoint_sdk.CardRegistration
   :members: card_id, redirect_url, transaction, trace_id, raw

.. autoclass:: epoint_sdk.Card
   :members: id, status, name, mask, expiry, description, trace_id, raw, usable

.. autoclass:: epoint_sdk.Widget
   :members: widget_url, transaction, trace_id, raw, origin

.. autoclass:: epoint_sdk.WidgetMessage
   :members: status, order_id, transaction, amount, card_mask, message, raw, from_event, looks_paid

.. autoclass:: epoint_sdk.InstallmentPlan
   :members: card_id, name, months

.. autoclass:: epoint_sdk.Wallet
   :members: id, name

.. autoclass:: epoint_sdk.Invoice
   :members: id, amount, status, name, description, phone, email, period_from, period_to, raw

.. autoclass:: epoint_sdk.Transfer
   :members: order_id, status, bulk_id, amount, payee_iban, payee_name, raw

.. autoclass:: epoint_sdk.CheckoutForm
   :members: action, data, signature, fields
```

`Callback` is the same class as `Transaction`.

## Enums

All enums are `str` subclasses, so they compare equal to their values: `Status.SUCCESS == "success"`.

```{eval-rst}
.. autoclass:: epoint_sdk.Status
   :members:
   :undoc-members:
   :exclude-members: of

.. autoclass:: epoint_sdk.CardStatus
   :members:
   :undoc-members:
   :exclude-members: of

.. autoclass:: epoint_sdk.OperationCode
   :members:
   :undoc-members:

.. autoclass:: epoint_sdk.Language
   :members:
   :undoc-members:

.. autoclass:: epoint_sdk.Currency
   :members:
   :undoc-members:
```

## Callbacks and signing

```{eval-rst}
.. autofunction:: epoint_sdk.verify_callback

.. autofunction:: epoint_sdk.callback_form

.. autofunction:: epoint_sdk.origin_of

.. automodule:: epoint_sdk.signing
   :members: encode, sign, matches, decode, verify
```

## Settings

```{eval-rst}
.. autofunction:: epoint_sdk.load_settings

.. autoclass:: epoint_sdk.Settings
   :members: keys, url, check_transport, resolved_user_agent
   :no-index-entry:
```

## Messages

```{eval-rst}
.. automodule:: epoint_sdk.messages
   :members: use, reset, text, catalog
```

## Exceptions

```{eval-rst}
.. autoexception:: epoint_sdk.EpointError
.. autoexception:: epoint_sdk.ConfigurationError
.. autoexception:: epoint_sdk.InvalidRequestError
.. autoexception:: epoint_sdk.SignatureError
.. autoexception:: epoint_sdk.TransportError
.. autoexception:: epoint_sdk.NotSentError
.. autoexception:: epoint_sdk.OutcomeUnknownError
.. autoexception:: epoint_sdk.HTTPStatusError
.. autoexception:: epoint_sdk.GatewayError
```
