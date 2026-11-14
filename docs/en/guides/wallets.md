# Wallets

Epoint can take payments from electronic wallets it works with. Wallet payments must be enabled for your merchant account.

## Listing wallets

```python
for wallet in ep.wallets.list():
    print(wallet.id, wallet.name)
```

Each item is a {py:class}`~epoint_sdk.Wallet` with an `id` and a `name`. The list is safe to load again and again, so you can cache it for a few minutes and show it on your checkout page.

## Paying with a wallet

```python
checkout = ep.wallets.pay(wallet_id, "25.00", "ORDER-7001", description="Gift card")
redirect(checkout.redirect_url)
```

The arguments are the wallet id, the amount and your order id, plus `description`, `language` and `currency` as keywords. The answer is a `Redirect`: send the customer to `redirect_url`, and wait for the callback as with a card payment.
