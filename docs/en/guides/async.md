# Async

`AsyncEpoint` has exactly the same namespaces and methods as `Epoint`. The only difference is that you `await` every call that talks to the gateway.

```python
import asyncio
from epoint_sdk import AsyncEpoint

async def main():
    async with AsyncEpoint("i000000001", "PRIVATE_KEY") as ep:
        checkout = await ep.payments.create("19.90", "ORDER-1042", description="Pro plan")
        print(checkout.redirect_url)

        tx = await ep.payments.status(checkout.transaction)
        print(tx.status)

asyncio.run(main())
```

## What is awaited and what is not

| Call | Awaited |
| --- | --- |
| Every method under `payments`, `cards`, `split`, `installments`, `wallets`, `widgets`, `invoices`, `transfers` that calls Epoint | yes |
| `heartbeat()`, `request()` | yes |
| `close()` | yes |
| `verify_callback()` | **no**, it only checks a signature locally |
| `payments.form()` | **no**, it only signs locally |

```python
tx = ep.verify_callback(form)   # no await
```

## One client per application

Create the client once, at start up, and close it at shut down. In FastAPI that is the lifespan:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from epoint_sdk import AsyncEpoint

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.epoint = AsyncEpoint()
    yield
    await app.state.epoint.close()

app = FastAPI(lifespan=lifespan)
```

The complete application is in the [FastAPI example](../examples/fastapi.md).

## Running calls side by side

Read calls can run concurrently:

```python
results = await asyncio.gather(*(ep.payments.status(t) for t in pending_ids))
```

Keep the number reasonable. Epoint answers too many requests with HTTP 429, and although the SDK retries 429, firing hundreds of calls at once only makes everything slower. An `asyncio.Semaphore` is an easy limit.

## Your own AsyncClient

```python
import httpx

http = httpx.AsyncClient(timeout=15)
ep = AsyncEpoint(http_client=http)
...
await http.aclose()
```

When you pass your own client, you close it yourself.

## Errors and retries

The rules are the same as for the sync client. See [Errors](errors.md) and [Reliability](reliability.md).
