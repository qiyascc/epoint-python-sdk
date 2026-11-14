# Installation

This page walks through a clean install: a virtual environment, the package itself, a quick check that it works, and how to upgrade or remove it later.

## Requirements

- Python 3.10, 3.11, 3.12 or 3.13.
- Network access to `https://epoint.az` from the server that makes the calls.
- An Epoint merchant account for real payments. While you build, the [local sandbox](guides/testing.md) is enough.

Check your Python version first:

::::{tab-set}

:::{tab-item} Linux and macOS
```console
$ python3 --version
Python 3.12.3
```
:::

:::{tab-item} Windows (CMD)
```bat
py --version
```
:::

::::

## Step 1. Create a virtual environment

A virtual environment keeps the packages of one project apart from everything else on the machine. Create one in your project folder:

::::{tab-set}

:::{tab-item} Linux and macOS
```console
$ cd my-shop
$ python3 -m venv .venv
$ source .venv/bin/activate
```
:::

:::{tab-item} Windows (CMD)
```bat
cd my-shop
py -m venv .venv
.venv\Scripts\activate.bat
```
:::

::::

Once it is active, the prompt starts with `(.venv)`. Every `pip install` from now on goes into this folder only.

## Step 2. Install the package

::::{tab-set}

:::{tab-item} pip
```console
$ pip install epoint-python-sdk
```
:::

:::{tab-item} uv
```console
$ uv add epoint-python-sdk
```
In a project that is not managed by uv, use `uv pip install epoint-python-sdk`.
:::

:::{tab-item} Poetry
```console
$ poetry add epoint-python-sdk
```
:::

::::

The distribution is called `epoint-python-sdk` and the import name is `epoint_sdk`:

```python
from epoint_sdk import Epoint
```

### Optional extras

Settings can be read from a file (see [Configuration](configuration.md)). JSON files work out of the box. Two extras add the other formats:

| Extra | Install | When you need it |
| --- | --- | --- |
| `yaml` | `pip install "epoint-python-sdk[yaml]"` | You keep settings in `epoint.yaml` or `epoint.yml` |
| `toml` | `pip install "epoint-python-sdk[toml]"` | You keep settings in `epoint.toml` and run Python 3.10. Python 3.11 and newer read TOML without it |

## Step 3. Check the install

```console
$ python -c "import epoint_sdk; print(epoint_sdk.__version__)"
0.2.0
```

If you already have keys, you can also ask the gateway whether it is up. `heartbeat()` is not signed and returns `True` when Epoint answers `ok`:

```python
from epoint_sdk import Epoint

with Epoint("i000000001", "PRIVATE_KEY") as ep:
    print(ep.heartbeat())
```

## Step 4. Pin the version

Payment code should not change under you without notice. Pin the version in your requirements file and upgrade on purpose:

```text
epoint-python-sdk==0.2.0
```

## Upgrading

```console
$ pip install --upgrade epoint-python-sdk
```

Read the [changelog](reference/changelog.md) before you upgrade, and run your payment tests afterwards.

## Uninstalling

```console
$ pip uninstall epoint-python-sdk
```

## Installing from source

To try an unreleased change, install straight from GitHub:

```console
$ pip install "git+https://github.com/qiyascc/epoint-python-sdk.git"
```

For working on the SDK itself, see [Development](development.md).

## Next step

Get your keys ready on the [Merchant account and keys](keys.md) page, then make your first payment with the [Quickstart](quickstart.md).
