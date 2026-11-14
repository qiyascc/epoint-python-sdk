# Development

How to work on the SDK itself.

## Setting up

```console
$ git clone https://github.com/qiyascc/epoint-python-sdk.git
$ cd epoint-python-sdk
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install -e ".[dev]"
```

## Checks

```console
$ pytest
$ ruff check .
$ mypy src
```

The tests use `httpx.MockTransport` and a small fake gateway in `tests/conftest.py`, so they never touch the real API. CI runs them on Python 3.10 to 3.13.

## Project layout

| Path | Contents |
| --- | --- |
| `src/epoint_sdk/client.py` | `Epoint` and `AsyncEpoint` |
| `src/epoint_sdk/_core.py` | Sending, retries and error mapping |
| `src/epoint_sdk/resources.py` | The namespaces: payments, cards, split and the rest |
| `src/epoint_sdk/models.py` | Result dataclasses |
| `src/epoint_sdk/signing.py` | Signing and checking `data` and `signature` |
| `src/epoint_sdk/callbacks.py` | `verify_callback` and `callback_form` |
| `src/epoint_sdk/money.py` | Amount parsing |
| `src/epoint_sdk/config.py` | `Settings` and the endpoint paths |
| `src/epoint_sdk/messages.yaml` | Every message text |
| `tests/` | The test suite |
| `docs/` | This documentation in Azerbaijani, English and Turkish |

## Building the docs

```console
$ pip install -r docs/requirements.txt
$ sphinx-build -W -b html docs/en docs/en/_build/html
$ sphinx-build -W -b html docs/az docs/az/_build/html
$ sphinx-build -W -b html docs/tr docs/tr/_build/html
```

Each language is a separate Sphinx project with its own `conf.py`. Shared settings, templates and styles live in `docs/_common/`.

## Rules for changes

- A call that moves money must never be retried after an unclear failure. Add a test for every new call that says which group it belongs to.
- Every user facing message goes into `messages.yaml`.
- New endpoint paths go into `Endpoints` in `config.py`, never into the code that calls them.
- Update `CHANGELOG.md` and all three languages of the docs.
