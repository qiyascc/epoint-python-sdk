# Asenkron kullanım

`AsyncEpoint`, `Epoint` ile tamamen aynı bölümlere ve metotlara sahiptir. Tek fark, ödeme altyapısıyla konuşan her çağrıyı `await` ile beklemenizdir.

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

## Hangi çağrılar await ister

| Çağrı | `await` gerekir |
| --- | --- |
| `payments`, `cards`, `split`, `installments`, `wallets`, `widgets`, `invoices`, `transfers` altında Epoint'e istek atan her metot | evet |
| `heartbeat()`, `request()` | evet |
| `close()` | evet |
| `verify_callback()` | **hayır**, yalnızca imzayı yerelde kontrol eder |
| `payments.form()` | **hayır**, yalnızca yerelde imzalar |

```python
tx = ep.verify_callback(form)   # await yok
```

## Uygulama başına bir istemci

İstemciyi uygulama açılırken bir kez oluşturun ve kapanırken kapatın. FastAPI'de bunun yeri lifespan fonksiyonudur:

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

Uygulamanın tamamı [FastAPI örneğinde](../examples/fastapi.md).

## Çağrıları paralel çalıştırmak

Okuma çağrıları aynı anda çalışabilir:

```python
results = await asyncio.gather(*(ep.payments.status(t) for t in pending_ids))
```

Sayıyı makul tutun. Epoint çok fazla isteğe HTTP 429 ile yanıt verir ve SDK 429'dan sonra yeniden denese de yüzlerce isteği aynı anda göndermek her şeyi yalnızca yavaşlatır. Basit bir sınır için `asyncio.Semaphore` kullanabilirsiniz.

## Kendi AsyncClient nesneniz

```python
import httpx

http = httpx.AsyncClient(timeout=15)
ep = AsyncEpoint(http_client=http)
...
await http.aclose()
```

Kendi istemcinizi verdiğinizde onu kendiniz kapatırsınız.

## Hatalar ve yeniden denemeler

Kurallar senkron istemciyle aynıdır. Bkz. [Hatalar](errors.md) ve [Güvenilirlik](reliability.md).
