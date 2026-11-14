# Security

A payment integration is attacked in a few predictable places. This page lists them and shows what the SDK does about each one, and what is left for you to do.

## 1. Trust only the signed callback

The redirect to your `success_url` proves nothing. Anyone can type that address into a browser. Mark an order as paid only after one of these:

- a callback that passed `verify_callback`, or
- a `payments.status()` call made by your server.

## 2. Check that the callback is about this order

A valid signature means Epoint sent the callback, not that it belongs to the order you are about to unlock. An attacker could pay 1 AZN for a cheap order and try to replay that callback against an expensive one. Compare it with your records:

```python
if tx.paid and tx.matches(order_id=order.number, amount=order.total, transaction=order.epoint_transaction):
    order.mark_paid()
```

## 3. Keep the private key on the server

- Never send it to a browser or a mobile app. Signing happens on the server only.
- Keep it out of your repository and out of logs. The SDK stores it as a `SecretStr`, so printing settings shows `**********`, and `repr(ep)` shows only the public key.
- Load it from the environment or a secrets manager.
- If it may have leaked, ask Epoint for a new key pair at once.

## 4. Only https

Signed requests are refused over plain `http`, except to localhost or when you explicitly set `allow_insecure_http` for a private sandbox. Never set that flag in production.

## 5. Validate before sending

Amounts are checked before any request leaves your server: no floats with hidden rounding, no `NaN`, no negative values, no booleans posing as `1`. Order ids and texts have length limits. Let these errors surface to the developer, not to the customer.

## 6. Protect the callback endpoint from abuse

- The SDK rejects callback data over 64 KB and signatures over 128 characters before hashing.
- Signatures are compared with `hmac.compare_digest`, so timing tells an attacker nothing.
- Answer invalid callbacks with HTTP 400 and do no other work.
- Rate limit the endpoint at your proxy if it is exposed to the internet.

## 7. Treat browser messages as hints

The Apple Pay and Google Pay widget reports its result with `postMessage`. Check `event.origin` against `widget.origin`, and even then only use the message to ask your own server to look the payment up. `WidgetMessage.looks_paid` is named that way to remind you.

## 8. Never double charge

Calls that move money are not retried after an unclear failure. Keep it that way in your own code: on `OutcomeUnknownError`, check first and retry only with the same order id. See [Reliability](reliability.md).

## 9. Log carefully

Log `order_id`, `transaction`, `trace_id`, status and amounts. Do not log the private key, full callback bodies in production, or anything the customer typed. The `trace_id` is what Epoint support asks for.

## Checklist before going live

- [ ] `base_url` is `https://epoint.az` and `allow_insecure_http` is not set.
- [ ] The private key comes from the environment or a secrets manager.
- [ ] The callback view verifies the signature and calls `matches()`.
- [ ] Orders are marked paid only in the callback or after `payments.status()`.
- [ ] The callback handler is idempotent.
- [ ] `OutcomeUnknownError` leads to a status check, not a new order id.
- [ ] A job checks orders that stay pending too long.
- [ ] The widget page sends `Permissions-Policy: payment=(self "https://epoint.az")`.
