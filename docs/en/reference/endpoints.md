# Endpoints and raw requests

Every API path is a setting, so you can follow a change on Epoint's side without waiting for a new SDK release.

## Default paths

| Name | Default path | Used by |
| --- | --- | --- |
| `payment` | `/api/1/request` | `payments.create` |
| `checkout` | `/api/1/checkout` | `payments.form` (form action) |
| `status` | `/api/1/get-status` | `payments.status` |
| `reverse` | `/api/1/reverse` | `payments.reverse` |
| `hold` | `/api/1/pre-auth-request` | `payments.hold` |
| `capture` | `/api/1/pre-auth-complete` | `payments.capture` |
| `card_register` | `/api/1/card-registration` | `cards.register` |
| `card_register_pay` | `/api/1/card-registration-with-pay` | `cards.register_and_pay` |
| `card_charge` | `/api/1/execute-pay` | `cards.charge` |
| `card_status` | `/api/1/get-status-card` | `cards.status` |
| `payout` | `/api/1/refund-request` | `cards.payout` |
| `split_payment` | `/api/1/split-request` | `split.create` |
| `split_charge` | `/api/1/split-execute-pay` | `split.charge` |
| `split_register_pay` | `/api/1/split-card-registration-with-pay` | `split.register_and_pay` |
| `installment_plans` | `/api/1/get-installment-request` | `installments.plans` |
| `installment_payment` | `/api/1/installment-request` | `installments.create` |
| `wallets` | `/api/1/wallet/status` | `wallets.list` |
| `wallet_payment` | `/api/1/wallet/payment` | `wallets.pay` |
| `widget` | `/api/1/token/widget` | `widgets.create` |
| `widget_split` | `/api/1/token/split-payment` | `widgets.split` |
| `invoice_create` | `/api/1/invoices/create` | `invoices.create` |
| `invoice_update` | `/api/1/invoices/update` | `invoices.update` |
| `invoice_view` | `/api/1/invoices/view` | `invoices.get` |
| `invoice_list` | `/api/1/invoices/list` | `invoices.list` |
| `invoice_sms` | `/api/1/invoices/send-sms` | `invoices.send_sms` |
| `invoice_email` | `/api/1/invoices/send-email` | `invoices.send_email` |
| `b2b_transfer` | `/api/1/b2b/payment` | `transfers.create` |
| `b2b_status` | `/api/1/b2b/payment/{order_id}` | `transfers.status` |
| `heartbeat` | `/api/heartbeat` | `heartbeat` |

Paths are relative to `base_url`. Values in braces are filled in and URL encoded for each call.

## Overriding a path

In code:

```python
ep = Epoint(endpoints={"payment": "/api/2/request"})
```

Only the paths you list change. The others keep their defaults.

In a config file:

```toml
[endpoints]
payment = "/api/2/request"
```

From the environment, with a double underscore between the parts:

```console
$ export EPOINT_ENDPOINTS__PAYMENT=/api/2/request
```

## Calling an endpoint the SDK does not wrap

`request()` signs any payload and posts it to any endpoint. Give it an endpoint name from the table or a path that starts with `/`:

```python
answer = ep.request("/api/1/some-new-call", {"order_id": "A-1", "amount": 10})
```

The answer is the decoded JSON, without any parsing. Errors are handled the same way as for the other calls: `status: error` raises `GatewayError`, HTTP errors raise `HTTPStatusError`.

By default `request()` is treated as a call that moves money and is never retried after an unclear failure. For a read only call, pass `safe=True` to allow retries:

```python
ep.request("/api/1/some-report", {"date": "2026-03-01"}, safe=True)
```

Your `public_key` is added to the payload, and empty values (`None` or `""`) are dropped before signing.
