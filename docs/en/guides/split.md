# Split payments

A split payment takes one payment from the customer and gives part of it to another Epoint merchant, the partner. Marketplaces use it to pay sellers, and platforms use it to share revenue with resellers.

Every split call takes two extra values:

`partner`
: The partner's Epoint public key, for example `i000000002`. It is sent as `split_user`.

`partner_amount`
: The partner's share. It must be a valid amount and may not be larger than the total. A larger share raises `InvalidRequestError` before anything is sent.

## On the payment page

```python
checkout = ep.split.create(
    "100.00",
    "ORDER-5001",
    "i000000002",
    "85.00",
    description="Handmade lamp from Studio Nur",
)
redirect(checkout.redirect_url)
```

The first four arguments are the total, your order id, the partner and the partner's share. The keyword arguments are the same as for `payments.create()` except `installment`. The answer is a `Redirect`.

## With a saved card

```python
tx = ep.split.charge(card_id, "100.00", "ORDER-5002", "i000000002", "85.00")
```

Like `cards.charge()`, this charges at once and returns a `Transaction`. A declined card returns a transaction with `failed` set.

## Saving a card with a split payment

```python
reg = ep.split.register_and_pay("100.00", "ORDER-5003", "i000000002", "85.00")
redirect(reg.redirect_url)
```

The answer is a `CardRegistration`.

## In the callback

The callback of a split payment carries the partner's share in `split_amount`:

```python
tx = ep.verify_callback(request.POST)
if tx.paid:
    record_sale(tx.order_id, total=tx.amount, partner_share=tx.split_amount)
```

## Apple Pay and Google Pay

The widget has a split variant too: `ep.widgets.split(...)`. See [Apple Pay and Google Pay](apple-google-pay.md#split-payments-in-the-widget).
