# Saved cards

Saving a card lets you charge the customer again without sending them to the payment page. This is what subscriptions, one click checkout and top ups are built on. The card itself stays with Epoint. You only keep a `card_id`.

## Saving a card without a payment

```python
reg = ep.cards.register(description="Save your card for faster checkout")
user.pending_card_id = reg.card_id
redirect(reg.redirect_url)
```

`register()` takes only keyword arguments:

| Argument | Default | Meaning |
| --- | --- | --- |
| `payouts` | `False` | `True` registers the card for payouts, so you can send money to it later |
| `description` | none | Text on the Epoint page |
| `language` | setting | Page language |
| `success_url` | setting | Where the customer returns on success |
| `error_url` | setting | Where the customer returns on failure |

It returns a {py:class}`~epoint_sdk.CardRegistration` with `card_id`, `redirect_url`, `transaction`, `trace_id` and `raw`. The `card_id` is known straight away, but the card can only be used after the customer finishes the page.

## Saving a card with the first payment

Most shops save the card while the customer pays for the first time:

```python
reg = ep.cards.register_and_pay("9.90", "SUB-1001-1", description="Monthly plan")
redirect(reg.redirect_url)
```

It takes the same arguments as `payments.create()` except `installment` and `other_attr`, and returns a `CardRegistration`.

## Checking the card

```python
card = ep.cards.status(card_id)
if card.usable:
    user.save_card(card.id, card.mask, card.expiry)
```

{py:class}`~epoint_sdk.Card` has these fields:

| Field | Meaning |
| --- | --- |
| `id` | The card id |
| `status` | A {py:class}`~epoint_sdk.CardStatus`: `new`, `active`, `pending`, `rejected`, `expired`, `session_expired` or `unknown` |
| `usable` | `True` only when the status is `active` |
| `name` | Card name, if Epoint sent it |
| `mask` | Masked number |
| `expiry` | Expiry date as Epoint sent it |
| `description` | The description you gave |

You can also learn about the new card from the callback: its `operation_code` is `001` or `200`, and `card_id` and `card_mask` are filled in. See [Callbacks](callbacks.md#operation-codes).

## Charging a saved card

```python
tx = ep.cards.charge(user.card_id, "9.90", "SUB-1001-2", description="Monthly plan, March")
if tx.paid:
    extend_subscription(user)
elif tx.failed:
    notify_card_declined(user, tx.message)
```

The arguments are `card_id`, amount and `order_id`, in that order, plus the keyword arguments `description`, `language` and `currency`.

The charge happens immediately and the answer is a `Transaction`. A declined card does **not** raise: you get a transaction with `failed` set and the bank's `code` and `message`. Only a refusal of the request itself, such as an unknown card id, raises `GatewayError`.

Charging a saved card moves money, so it is never retried after an unclear failure. Use a fresh `order_id` for each billing period and reuse it only when you retry the same period.

## Payouts

A payout sends money **to** a card, for cashback, winnings or marketplace earnings. The card must have been registered with `payouts=True`:

```python
reg = ep.cards.register(payouts=True, description="Card for withdrawals")
```

Then:

```python
tx = ep.cards.payout(seller.payout_card_id, "120.00", "PAYOUT-5531", description="Earnings, week 12")
```

Payouts are a separate feature of your merchant account. If it is not enabled, Epoint refuses the call and the SDK raises `GatewayError`.

## Storing cards responsibly

- Store `card_id`, the mask and the expiry. Never try to store the full card number. You never see it anyway.
- Let users remove a saved card from their account page, and stop charging it at once.
- Show the mask, for example `**** 1111`, so the user knows which card will be charged.

A full monthly billing job is in the [subscriptions example](../examples/subscriptions.md).
