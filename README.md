# epoint-python-sdk

[![Python](https://img.shields.io/badge/python-3.10%20to%203.13-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![Epoint](https://img.shields.io/badge/gateway-epoint.az-0B5FFF)](https://epoint.az)
[![Typed](https://img.shields.io/badge/typing-mypy-2A6DB2)](https://mypy-lang.org)
[![Async](https://img.shields.io/badge/sync%20%2B%20async-httpx-5A45FF)](https://www.python-httpx.org)
[![Ruff](https://img.shields.io/badge/lint-ruff-D7FF64?logo=ruff&logoColor=black)](https://docs.astral.sh/ruff)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Typed Python client for the [Epoint](https://epoint.az) payment gateway. Sync and async, every endpoint, signed callbacks, and retry rules built so a payment is never sent twice.

```bash
pip install git+https://github.com/qiyascc/epoint-python-sdk.git
```

## Pay

```python
from epoint_sdk import Epoint

with Epoint("i000000001", "PRIVATE_KEY", success_url="https://shop.az/ok", error_url="https://shop.az/fail") as ep:
    checkout = ep.payments.create("19.90", "ORDER-1042", description="Pro plan")
    redirect(checkout.redirect_url)
```

## Confirm

```python
tx = ep.verify_callback(request.POST)
if tx.paid:
    fulfil(tx.order_id, tx.amount, tx.transaction)
```

Never trust the redirect alone. Use the signed callback, or ask the gateway:

```python
ep.payments.status(checkout.transaction).paid
```

## Safety

| Situation | What the client does |
| --- | --- |
| Connection refused, nothing sent | Retries, then `NotSentError` |
| Timeout, cut connection or 5xx on a call that moves money | No retry, `OutcomeUnknownError` with the `order_id` |
| Same failure on a read (status, card, lists) | Retries with backoff |
| 429 | Retries, the gateway did not process it |
| `status: error` from the gateway | `GatewayError` with `code` and `trace_id` |
| Declined card on a direct charge | Returns `Transaction` with `failed`, never raises |
| Amount like `1.005`, `0`, `NaN` or `True` | `InvalidRequestError` before anything is sent |

Reuse the same `order_id` when you retry. Epoint refuses a used one, so a double click or a crash can not charge twice. Amounts are `Decimal` end to end, and signatures are compared in constant time.

## Endpoints

| Namespace | Methods |
| --- | --- |
| `payments` | `create` `form` `status` `reverse` `hold` `capture` |
| `cards` | `register` `register_and_pay` `charge` `status` `payout` |
| `split` | `create` `charge` `register_and_pay` |
| `installments` | `plans` `create` |
| `wallets` | `list` `pay` |
| `widgets` | `create` (Apple Pay, Google Pay) |
| `invoices` | `create` `update` `get` `list` `send_sms` `send_email` |
| `transfers` | `create` `status` (B2B) |
| client | `heartbeat` `verify_callback` `request` |

`AsyncEpoint` has the same methods, awaited.

## Config

Pass values in code, or set `EPOINT_PUBLIC_KEY`, `EPOINT_PRIVATE_KEY`, `EPOINT_SUCCESS_URL`, `EPOINT_ERROR_URL`, `EPOINT_LANGUAGE`, `EPOINT_TIMEOUT`, `EPOINT_MAX_RETRIES`, or put them in `epoint.toml`. Every path is a setting (`EPOINT_ENDPOINTS__PAYMENT=...`) and `base_url` can point at a sandbox such as [epoint-sandbox](https://github.com/martian56/epoint-sandbox). Messages live in `messages.yaml` and can be replaced with `messages.use(...)`.

## Develop

```bash
pip install -e ".[dev]" && pytest && ruff check . && mypy src
```

MIT
