# FAQ and troubleshooting

## The client fails at start up with "Epoint public_key and private_key are required"

The keys did not reach the client. Check that `EPOINT_PUBLIC_KEY` and `EPOINT_PRIVATE_KEY` are set in the environment of the process that runs your app (not only in your shell), or that the config file is in the working directory or named by `EPOINT_CONFIG`.

## "Refusing to send signed requests over plain http"

`base_url` starts with `http://` and points at something other than localhost. Use `https`. For a sandbox on a private network, set `allow_insecure_http=True` there and nowhere else.

## Every callback fails with SignatureError

- The private key on the server is not the one Epoint uses for your merchant. Check for stray spaces or a key from another environment.
- Something between Epoint and your app changes the body: a proxy that rewrites forms, or a framework that reads the body before your view. Pass the original `data` and `signature` values.
- You are testing with a callback signed by a different key, for example the sandbox key against the live configuration.

## GatewayError on the second attempt to pay

Epoint refuses an `order_id` it has already seen. Use a new id for a new attempt, for example the order number plus an attempt counter. See [Payments](guides/payments.md#order-ids).

## GatewayError on Apple Pay, installments, wallets or B2B transfers

These features are enabled by Epoint per merchant. Ask Epoint to enable them for your account.

## The customer came back to the success page, but the order is still pending

The callback has not arrived yet, or it failed. Show a "confirming" message, poll your own backend, and fall back to `payments.status()` on the server. See [Callbacks](guides/callbacks.md#the-success-page-is-not-a-confirmation).

## I got OutcomeUnknownError. Was the customer charged?

Maybe. The request reached Epoint, but no clear answer came back. Do not resend with a new order id. Check the status, wait for the callback, or retry with the same order id. See [Reliability](guides/reliability.md#handling-outcomeunknownerror).

## InvalidRequestError for an amount that looks fine

Amounts may have at most two decimal places. A float such as `0.1 + 0.2` is `0.30000000000000004` and is rejected. Use strings or `Decimal` for money.

## Can I use the SDK from several threads?

Yes. The sync client uses an `httpx.Client`, which is thread safe. Create one client and share it.

## Can I use it with Django's async views?

Use `AsyncEpoint` in async views and `Epoint` in sync views. Do not call the sync client from an async view, it blocks the event loop.

## How do I see what was sent?

Turn on httpx logging:

```python
import logging

logging.basicConfig(level=logging.WARNING)
logging.getLogger("httpx").setLevel(logging.INFO)
```

This logs the method, URL and status of each request. The signed body is not logged.

## Where do I report a bug?

Open an issue at [github.com/qiyascc/epoint-python-sdk/issues](https://github.com/qiyascc/epoint-python-sdk/issues). Include the SDK version, the method you called, and the `trace_id` if you have one. Never include your private key.
