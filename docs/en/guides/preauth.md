# Pre-authorisation

A pre-authorisation reserves money on the customer's card without taking it. You capture the amount later, for example when the goods are shipped or the service is delivered. Hotels, car rentals and marketplaces that confirm stock by hand use this pattern.

## Step 1. Hold the money

`hold()` works like `payments.create()`: it returns a page for the customer.

```python
checkout = ep.payments.hold(
    "150.00",
    "BOOKING-77",
    description="Room deposit",
)
redirect(checkout.redirect_url)
```

It accepts `description`, `language`, `currency`, `success_url`, `error_url` and `other_attr`, just like `create()`. Store `checkout.transaction` with the booking.

The callback arrives in the usual way. Verify it as described in [Callbacks](callbacks.md).

## Step 2. Capture

When you are ready to charge, capture the amount:

```python
result = ep.payments.capture(booking.epoint_transaction, "150.00")
if result.ok:
    booking.mark_charged()
```

The amount is the second positional argument. Whether you may capture less than you held is decided by Epoint and your acquiring bank, so confirm it with Epoint before you rely on partial captures.

## Releasing a hold

To let the money go without charging, reverse the transaction:

```python
ep.payments.reverse(booking.epoint_transaction)
```

## Safety

Both `hold()` and `capture()` move money, so neither is retried after an unclear failure. A timeout raises `OutcomeUnknownError`. Check with `payments.status()` before trying again.

## How long a hold lasts

Card networks release a hold after a while if it is never captured. The exact time depends on the bank, so capture as soon as you can and do not plan around long holds.
