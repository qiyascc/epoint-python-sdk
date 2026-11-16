# Changelog

## 0.3.0

- `payments.methods()` reads `payment-methods`: which methods (card, Apple Pay, Google Pay, installments, wallets) are switched on, with `PaymentMethods.google_pay` / `.apple_pay` and the `PaymentMethod` enum
- `payments.status(order_id=...)` asks by your own order id when the transaction is not known
- Native Apple Pay / Google Pay buttons: `tokens.create` (`token/payment`), `tokens.apple_session` (`token/apple/session`), `tokens.apple_pay` and `tokens.google_pay` (`token/apple/pay`, `token/google/pay`); tokens are base64 encoded for you, charges are never resent after an ambiguous failure

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
