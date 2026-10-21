# Changelog

## 0.2.0

- Apple Pay and Google Pay: `widgets.create` returns `Widget.origin` for `postMessage` checks, `widgets.split` covers `token/split-payment`
- `WidgetMessage.from_event` reads the widget `postMessage` as an untrusted hint
- `Transaction.matches(order_id, amount, transaction)` for callback cross checks
- Signed requests are refused over plain http outside localhost unless `allow_insecure_http` is set
- Callback `data` over 64 KB and signatures over 128 characters are rejected before hashing

## 0.1.0

- Sync `Epoint` and async `AsyncEpoint`
- Payments, saved cards, payouts, split, pre-auth, installments, wallets, Apple Pay and Google Pay widget, invoices, B2B transfers
- Callback verification from a raw pair or a form mapping
- Calls that move money are never resent after an ambiguous failure; `OutcomeUnknownError` carries the `order_id`
- Reads retry with backoff, connection failures retry because nothing was sent
- Strict `Decimal` amounts, constant time signature checks, private key kept as a secret
- goodconf settings, endpoint paths and messages are configurable
