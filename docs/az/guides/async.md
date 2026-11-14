# Asinxron iş

`AsyncEpoint` sinfinin bölmələri və metodları `Epoint` ilə tam eynidir. Yeganə fərq ödəniş sisteminə müraciət edən hər çağırışın `await` ilə gözlənilməsidir.

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

## Hansı çağırışlara await lazımdır

| Çağırış | `await` lazımdır |
| --- | --- |
| `payments`, `cards`, `split`, `installments`, `wallets`, `widgets`, `invoices`, `transfers` altında Epoint-ə müraciət edən hər metod | bəli |
| `heartbeat()`, `request()` | bəli |
| `close()` | bəli |
| `verify_callback()` | **xeyr**, o, imzanı yalnız lokal yoxlayır |
| `payments.form()` | **xeyr**, o, yalnız lokal imzalayır |

```python
tx = ep.verify_callback(form)   # await yoxdur
```

## Bütün tətbiq üçün bir klient

Klienti tətbiq işə düşəndə bir dəfə yaradın və dayananda bağlayın. FastAPI-də bunun yeri lifespan funksiyasıdır:

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

Tam tətbiq [FastAPI nümunəsindədir](../examples/fastapi.md).

## Çağırışları paralel işlətmək

Oxuma sorğuları eyni vaxtda işləyə bilər:

```python
results = await asyncio.gather(*(ep.payments.status(t) for t in pending_ids))
```

Sayı ağlabatan saxlayın. Epoint həddindən çox sorğuya HTTP 429 ilə cavab verir. SDK 429 cavabından sonra təkrar cəhd etsə də, yüzlərlə sorğunu birdən göndərmək hər şeyi yalnız yavaşladır. `asyncio.Semaphore` sadə məhdudiyyət üsuludur.

## Öz AsyncClient obyektiniz

```python
import httpx

http = httpx.AsyncClient(timeout=15)
ep = AsyncEpoint(http_client=http)
...
await http.aclose()
```

Öz klientinizi verirsinizsə, onu özünüz bağlayırsınız.

## Xətalar və təkrar cəhdlər

Qaydalar sinxron klientdəki kimidir. Bax: [Xətalar](errors.md) və [Etibarlılıq](reliability.md).
