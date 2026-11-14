# Payments

A standard card payment happens on a page hosted by Epoint. Your server creates the payment, the customer pays on Epoint's page, and the result comes back in a signed callback. This page covers every way to start such a payment.

## Creating a payment

```python
checkout = ep.payments.create(
    "49.00",
    "ORDER-2001",
    description="Annual subscription",
    language="en",
    currency="AZN",
    success_url="https://shop.az/payment/ok?order=ORDER-2001",
    error_url="https://shop.az/payment/fail?order=ORDER-2001",
)
```

| Argument | Required | Meaning |
| --- | --- | --- |
| `amount` | yes | Amount as `str`, `Decimal` or `int`. At most two decimal places, above zero |
| `order_id` | yes | Your unique order id, up to 255 characters |
| `description` | no | Text shown on the payment page, up to 1000 characters |
| `language` | no | `az`, `en` or `ru`. Defaults to the `language` setting |
| `currency` | no | `AZN`, `USD`, `EUR` or `RUB`. Defaults to the `currency` setting |
| `success_url` | no | Where the customer goes after paying. Defaults to the `success_url` setting |
| `error_url` | no | Where the customer goes after a failure. Defaults to the `error_url` setting |
| `installment` | no | `True` lets the customer pick an installment plan on the page, when your account allows it |
| `other_attr` | no | Extra data that Epoint keeps with the payment. It comes back as `other_attr` in the result |

Arguments after `order_id` are keyword only.

The call returns a {py:class}`~epoint_sdk.Redirect`:

| Field | Meaning |
| --- | --- |
| `redirect_url` | The Epoint page to send the customer to |
| `transaction` | Epoint's id for this payment. Store it with the order |
| `trace_id` | Epoint's trace id, useful when you contact support |
| `message` | A message from the gateway, if any |
| `raw` | The full JSON answer as a dict |

## Order ids

The order id is your idempotency key. Epoint refuses an order id it has already accepted, so:

- generate it once per payment attempt and store it before you call Epoint,
- reuse the **same** id if you retry the same attempt after a network error,
- create a **new** id only when the customer starts a genuinely new attempt, for example after a declined card.

A simple pattern is your order number plus an attempt counter: `ORDER-2001-1`, `ORDER-2001-2`.

## Amounts

The SDK turns every amount into a `Decimal` with two decimal places before sending:

```python
ep.payments.create("10", "A-1")       # 10.00
ep.payments.create(Decimal("9.9"), "A-2")  # 9.90
```

These raise `InvalidRequestError` and nothing is sent:

```python
ep.payments.create("1.005", "A-3")   # more than two decimals
ep.payments.create(0, "A-4")         # not above zero
ep.payments.create("NaN", "A-5")     # not finite
ep.payments.create(True, "A-6")      # a bool is not an amount
```

Floats are accepted, but a string or `Decimal` is always the safer choice.

## The signed form instead of a redirect

`payments.form()` takes the same arguments as `create()`, but does not call Epoint. It signs the request locally and gives you a form to post from the customer's browser:

```python
form = ep.payments.form("19.90", "ORDER-1042", description="Pro plan")
form.action   # https://epoint.az/api/1/checkout
form.fields   # {"data": "...", "signature": "..."}
```

In a template:

```html
<form method="post" action="{{ form.action }}">
  <input type="hidden" name="data" value="{{ form.data }}">
  <input type="hidden" name="signature" value="{{ form.signature }}">
  <button type="submit">Pay 19.90 AZN</button>
</form>
```

Use it when you want the browser to go to Epoint directly, for example from a plain HTML page. The callback works exactly as with `create()`.

## Checking the status

```python
tx = ep.payments.status("te001234")
```

The answer is a {py:class}`~epoint_sdk.Transaction`. Its helper properties are the easiest way to read it:

| Property | `True` when the status is |
| --- | --- |
| `paid` | `success` |
| `failed` | `failed` or `error` |
| `returned` | `returned` (the payment was reversed) |
| `pending` | `new`, `server_error` or anything unknown |
| `final` | anything that is not pending |

A declined card is a normal answer, not an error: `status()` returns the transaction with `failed` set instead of raising. A status call is safe to repeat, so the SDK retries it on timeouts and server errors.

## Installments on the payment page

If installments are enabled for your account, `installment=True` lets the customer pick a plan on the Epoint page:

```python
ep.payments.create("1200", "ORDER-3001", description="Laptop", installment=True)
```

To choose the plan yourself on your own page, see [Installments](installments.md).

## Passing your own data

`other_attr` lets you attach extra data to the payment. It is part of the signed request and comes back in `Transaction.other_attr`:

```python
ep.payments.create("5", "ORDER-4001", other_attr={"customer": 77})
```

The format Epoint accepts for this field is decided by Epoint, so check with them before you rely on nested data.

## Other ways to take money

- [Saved cards](saved-cards.md): charge a card without sending the customer to Epoint again.
- [Pre-authorisation](preauth.md): hold the money now, capture it later.
- [Split payments](split.md): share one payment with a partner.
- [Apple Pay and Google Pay](apple-google-pay.md): an embedded widget instead of a redirect.
- [Wallets](wallets.md): pay with a wallet that Epoint supports.
