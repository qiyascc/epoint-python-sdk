# FastAPI

`AsyncEpoint` ilə asinxron inteqrasiya. FastAPI-də formaları oxumaq üçün `python-multipart` lazımdır:

```console
$ pip install fastapi uvicorn python-multipart epoint-python-sdk
```

## Tətbiq

`app.py`:

```python
from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse

from epoint_sdk import AsyncEpoint, NotSentError, OutcomeUnknownError, SignatureError

ORDERS: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.epoint = AsyncEpoint()
    yield
    await app.state.epoint.close()


app = FastAPI(lifespan=lifespan)


@app.post("/orders/{number}/pay")
async def pay(number: str, request: Request):
    order = ORDERS.get(number)
    if order is None:
        raise HTTPException(404)

    order["attempt"] += 1
    order["epoint_order_id"] = f"{number}-{order['attempt']}"

    try:
        checkout = await request.app.state.epoint.payments.create(
            order["total"], order["epoint_order_id"], description=order["title"]
        )
    except NotSentError:
        raise HTTPException(503, "Payment service unavailable, try again shortly")
    except OutcomeUnknownError:
        order["state"] = "needs_check"
        return JSONResponse({"state": "needs_check"}, status_code=202)

    order["transaction"] = checkout.transaction
    order["state"] = "pending"
    return RedirectResponse(checkout.redirect_url, status_code=303)


@app.post("/payments/epoint/callback", response_class=PlainTextResponse)
async def callback(request: Request):
    form = await request.form()
    try:
        tx = request.app.state.epoint.verify_callback(form)
    except SignatureError:
        raise HTTPException(400)

    order = next((o for o in ORDERS.values() if o.get("epoint_order_id") == tx.order_id), None)
    if order is None or not tx.matches(order_id=order["epoint_order_id"], amount=order["total"]):
        return "OK"

    if tx.paid:
        order["state"] = "paid"
    elif tx.failed and order["state"] == "pending":
        order["state"] = "failed"
    return "OK"


@app.get("/orders/{number}/state")
async def state(number: str, request: Request):
    order = ORDERS.get(number)
    if order is None:
        raise HTTPException(404)
    if order["state"] in ("pending", "needs_check") and order.get("transaction"):
        tx = await request.app.state.epoint.payments.status(order["transaction"])
        if tx.paid and tx.matches(order_id=order["epoint_order_id"], amount=order["total"]):
            order["state"] = "paid"
    return {"state": order["state"]}


ORDERS["A1"] = {"total": Decimal("19.90"), "title": "Pro plan", "attempt": 0, "state": "new"}
```

`ORDERS` burada verilənlər bazanızı əvəz edir. Real tətbiqdə sifarişləri cədvəldə saxlayın və callback-dən yeniləyəndə sətri kilidləyin.

Qeydlər:

- `verify_callback` `await` ilə çağırılmır. O, yalnız imzanı yoxlayır.
- `await request.form()` `verify_callback` metodunun birbaşa oxuduğu mapping obyekti qaytarır.
- Sifariş hələ gözləmədədirsə, `/orders/{number}/state` ünvanı `payments.status()` çağırır. Bu, gecikən və ya itən callback halını əhatə edir.

İşə salın:

```console
$ uvicorn app:app --reload
```
