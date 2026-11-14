# API arayışı

Bu səhifədə `epoint_sdk` paketinin açıq sinifləri və funksiyaları sadalanır. Siyahı mənbə kodundan avtomatik yaradılır. Onlardan istifadə qaydası bələdçilərdə izah olunur. Buradakı hər şeyi birbaşa `epoint_sdk` paketindən import etmək olar.

## Klientlər

`Epoint` sinxron, `AsyncEpoint` isə asinxron klientdir. Hər ikisi ilk iki arqument kimi `public_key` və `private_key`, açar sözlü arqument kimi isə `settings`, `config_file`, `http_client` və [Konfiqurasiya](../configuration.md) səhifəsindəki istənilən ayarı qəbul edir.

```{eval-rst}
.. autoclass:: epoint_sdk.Epoint(public_key=None, private_key=None, *, settings=None, config_file=None, http_client=None, **overrides)
   :members: heartbeat, request, verify_callback, close, sign

.. autoclass:: epoint_sdk.AsyncEpoint(public_key=None, private_key=None, *, settings=None, config_file=None, http_client=None, **overrides)
   :members: heartbeat, request, verify_callback, close, sign
```

## Bölmələr

Hər klientin bu atributları var. Asinxron klientdə eyni metodlar korutin şəklindədir.

| Atribut | Sinif |
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

## Nəticələr

Bütün nəticə sinifləri dəyişdirilməyən (frozen) dataclass-lardır. Hər birində Epoint-in bütöv cavabını saxlayan `raw` sahəsi var.

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

`Callback` və `Transaction` eyni sinifdir.

## Sadalamalar (enum)

Bütün sadalamalar `str` sinfindən törəyir, ona görə öz dəyərlərinə bərabər sayılır: `Status.SUCCESS == "success"`.

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

## Callback-lər və imzalama

```{eval-rst}
.. autofunction:: epoint_sdk.verify_callback

.. autofunction:: epoint_sdk.callback_form

.. autofunction:: epoint_sdk.origin_of

.. automodule:: epoint_sdk.signing
   :members: encode, sign, matches, decode, verify
```

## Ayarlar

```{eval-rst}
.. autofunction:: epoint_sdk.load_settings

.. autoclass:: epoint_sdk.Settings
   :members: keys, url, check_transport, resolved_user_agent
   :no-index-entry:
```

## Mesajlar

```{eval-rst}
.. automodule:: epoint_sdk.messages
   :members: use, reset, text, catalog
```

## İstisnalar

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
