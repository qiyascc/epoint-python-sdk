# Merchant account and keys

Every call to Epoint is made on behalf of a merchant. A merchant is identified by two values: a public key and a private key. This page explains what they are, where they come from and how to keep them safe.

## The two keys

`public_key`
: The merchant identifier. It looks like `i000000001`: the letter `i` followed by digits. It travels inside every request, so it is not a secret.

`private_key`
: The shared secret. The SDK uses it to sign every request and to check the signature of every callback. Anyone who has it can send requests in your name and forge callbacks that look like real payments. Treat it like a password.

## Getting the keys

The keys are issued by Epoint when you sign a merchant agreement with them. In the merchant cabinet you register your website and the addresses Epoint should use:

- the success page the customer returns to after paying,
- the error page the customer returns to after a failed payment,
- the result address, where Epoint sends the signed callback.

You then receive the key pair. The exact screens can change, so if something is unclear, ask Epoint support.

```{note}
The SDK never sends the result address with a request. Epoint knows it from the cabinet. The success and error pages, on the other hand, can be set per request or as defaults in the SDK settings.
```

## Features that need to be enabled

Some features are switched on by Epoint per merchant, on request. Until that happens, the gateway refuses the call and the SDK raises a `GatewayError`. Ask Epoint before you build on any of these:

- Apple Pay and Google Pay (the widget),
- installments,
- wallets,
- B2B bank transfers,
- American Express cards.

## Test or live

Epoint does not publish test cards. To build and test without a merchant account, run the community [epoint-sandbox](https://github.com/martian56/epoint-sandbox), which copies the gateway API and signs callbacks the same way. Point `base_url` at it, use its demo keys, and switch back to `https://epoint.az` with your real keys when you go live. The [Testing](guides/testing.md) page shows the full setup.

## Giving the keys to the SDK

Pass them in code:

```python
from epoint_sdk import Epoint

ep = Epoint("i000000001", "PRIVATE_KEY")
```

or set environment variables and create the client without arguments:

::::{tab-set}

:::{tab-item} Linux and macOS
```console
$ export EPOINT_PUBLIC_KEY=i000000001
$ export EPOINT_PRIVATE_KEY=your-private-key
```
:::

:::{tab-item} Windows (CMD)
```bat
set EPOINT_PUBLIC_KEY=i000000001
set EPOINT_PRIVATE_KEY=your-private-key
```
:::

::::

```python
ep = Epoint()
```

If either key is missing or empty, the constructor raises `ConfigurationError` straight away, so a broken deployment fails at start up and not in the middle of a checkout. All other ways to configure the client are on the [Configuration](configuration.md) page.

## Keeping the private key safe

- Keep it on the server only. Never put it in JavaScript, a mobile app or a template.
- Keep it out of version control. Use environment variables or a secrets manager.
- The SDK stores it as a pydantic `SecretStr`, so it shows up as `**********` when settings are printed or logged, and `repr(ep)` shows only the public key.
- If it leaks, ask Epoint for a new pair. Old signatures stop working as soon as the key changes.

More on this in [Security](guides/security.md).
