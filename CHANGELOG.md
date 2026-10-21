# Changelog

## 0.1.0

- Sync `Epoint` and async `AsyncEpoint`
- Payments, saved cards, payouts, split, pre-auth, installments, wallets, Apple Pay and Google Pay widget, invoices, B2B transfers
- Callback verification from a raw pair or a form mapping
- Calls that move money are never resent after an ambiguous failure; `OutcomeUnknownError` carries the `order_id`
- Reads retry with backoff, connection failures retry because nothing was sent
- Strict `Decimal` amounts, constant time signature checks, private key kept as a secret
- goodconf settings, endpoint paths and messages are configurable
