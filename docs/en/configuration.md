# Configuration

Settings are loaded with [goodconf](https://github.com/lincolnloop/goodconf). You can pass them in code, set environment variables, keep them in a file, or mix all three.

## Order of precedence

When the same setting comes from several places, the first one wins:

1. Arguments passed to `Epoint(...)` or `AsyncEpoint(...)`.
2. Environment variables that start with `EPOINT_`.
3. A config file.
4. The built-in default.

## In code

```python
from epoint_sdk import Epoint

ep = Epoint(
    "i000000001",
    "PRIVATE_KEY",
    success_url="https://shop.az/payment/ok",
    error_url="https://shop.az/payment/fail",
    language="en",
    timeout=20,
)
```

Any setting from the table below can be passed as a keyword argument.

## Environment variables

Every setting has a variable named `EPOINT_` plus the setting name in capitals:

```console
$ export EPOINT_PUBLIC_KEY=i000000001
$ export EPOINT_PRIVATE_KEY=your-private-key
$ export EPOINT_SUCCESS_URL=https://shop.az/payment/ok
$ export EPOINT_ERROR_URL=https://shop.az/payment/fail
$ export EPOINT_LANGUAGE=az
$ export EPOINT_TIMEOUT=30
$ export EPOINT_MAX_RETRIES=2
```

On Windows CMD use `set NAME=value` instead of `export`.

With the variables set, the client needs no arguments:

```python
ep = Epoint()
```

## Config file

With no arguments, the client also looks in the working directory for `epoint.toml`, `epoint.yaml`, `epoint.yml` or `epoint.json`, in that order:

```toml
public_key = "i000000001"
private_key = "your-private-key"
success_url = "https://shop.az/payment/ok"
error_url = "https://shop.az/payment/fail"
language = "az"
timeout = 30
```

To load a file from somewhere else, either point `EPOINT_CONFIG` at it or pass `config_file`:

```console
$ export EPOINT_CONFIG=/etc/myshop/epoint.toml
```

```python
ep = Epoint(config_file="/etc/myshop/epoint.toml")
```

YAML needs the `yaml` extra, and TOML on Python 3.10 needs the `toml` extra. See [Installation](installation.md#optional-extras).

```{warning}
A config file with the private key must not end up in your repository. Add it to `.gitignore`, or keep only the non secret settings in the file and the keys in the environment.
```

## All settings

| Setting | Environment variable | Default | Meaning |
| --- | --- | --- | --- |
| `public_key` | `EPOINT_PUBLIC_KEY` | (empty) | Merchant public key, for example `i000000001`. Required |
| `private_key` | `EPOINT_PRIVATE_KEY` | (empty) | Merchant private key. Signs requests and checks callbacks. Required |
| `base_url` | `EPOINT_BASE_URL` | `https://epoint.az` | Gateway address. Point it at a sandbox while testing |
| `endpoints.*` | `EPOINT_ENDPOINTS__<NAME>` | see [Endpoints](reference/endpoints.md) | Path of every API call, relative to `base_url` |
| `language` | `EPOINT_LANGUAGE` | `az` | Language of the hosted payment page: `az`, `en` or `ru` |
| `currency` | `EPOINT_CURRENCY` | `AZN` | Default currency: `AZN`, `USD`, `EUR` or `RUB` |
| `success_url` | `EPOINT_SUCCESS_URL` | none | Page the customer returns to after a successful payment |
| `error_url` | `EPOINT_ERROR_URL` | none | Page the customer returns to after a failed payment |
| `timeout` | `EPOINT_TIMEOUT` | `30` | Seconds to wait for an answer. Must be above zero |
| `connect_timeout` | `EPOINT_CONNECT_TIMEOUT` | `10` | Seconds to wait for a connection. Must be above zero |
| `max_retries` | `EPOINT_MAX_RETRIES` | `2` | Extra attempts for calls that are safe to repeat. From 0 to 10 |
| `backoff_base` | `EPOINT_BACKOFF_BASE` | `0.5` | First wait between retries, in seconds |
| `backoff_cap` | `EPOINT_BACKOFF_CAP` | `8` | Longest wait between retries, in seconds |
| `user_agent` | `EPOINT_USER_AGENT` | `epoint-python-sdk/{version}` | `User-Agent` header. `{version}` is replaced with the SDK version |
| `allow_insecure_http` | `EPOINT_ALLOW_INSECURE_HTTP` | `False` | Allow a plain `http` base URL outside localhost. Only for a sandbox on a private network |

Retries and timeouts are explained in detail on the [Reliability](guides/reliability.md) page.

Values are validated when the client is created. An unknown language, a currency in lower case (`usd` instead of `USD`), a timeout of zero or a `max_retries` above 10 raise pydantic's `ValidationError`, so a typo in the environment stops the application at start up.

## Defaults that a single call can override

`language`, `currency`, `success_url` and `error_url` are defaults. Most payment methods accept the same names as keyword arguments, and a value passed to the call wins:

```python
ep.payments.create("10", "ORDER-7", language="en", currency="USD",
                   success_url="https://shop.az/en/thanks")
```

## Building settings yourself

`load_settings` reads the environment and files the same way the client does, and returns a `Settings` object you can inspect or reuse:

```python
from epoint_sdk import Epoint, load_settings

settings = load_settings("/etc/myshop/epoint.toml", timeout=15)
print(settings.base_url, settings.timeout)

ep = Epoint(settings=settings)
```

If you pass both `settings` and keyword arguments, the keyword arguments are applied on top:

```python
staging = Epoint(settings=settings, base_url="http://localhost:8181")
```

## Plain http is refused

Signed requests are only sent over `https`. A `base_url` that starts with `http://` raises `ConfigurationError` when the client is created, with two exceptions:

- `localhost`, `127.0.0.1` and `::1` are always allowed, so a sandbox on your own machine works.
- `allow_insecure_http=True` allows any host. Use it only for a sandbox on a private network.

## Your own HTTP client

Pass an `httpx.Client` (or `httpx.AsyncClient` for `AsyncEpoint`) to use proxies, custom certificates or a mock transport in tests:

```python
import httpx
from epoint_sdk import Epoint

http = httpx.Client(proxy="http://proxy.internal:3128", timeout=20)
ep = Epoint(http_client=http)
```

When you pass your own client, its timeout settings are used instead of `timeout` and `connect_timeout`, and you are responsible for closing it. `ep.close()` only closes a client the SDK created itself.
