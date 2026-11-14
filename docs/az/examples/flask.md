# Flask

Sinxron klientlə kiçik Flask tətbiqi.

```console
$ pip install flask epoint-python-sdk
```

`app.py`:

```python
from decimal import Decimal

from flask import Flask, abort, jsonify, redirect, request

from epoint_sdk import Epoint, OutcomeUnknownError, SignatureError

app = Flask(__name__)
epoint = Epoint()

ORDERS = {"A1": {"total": Decimal("19.90"), "title": "Pro plan", "attempt": 0, "state": "new"}}


@app.post("/orders/<number>/pay")
def pay(number):
    order = ORDERS.get(number) or abort(404)
    order["attempt"] += 1
    order["epoint_order_id"] = f"{number}-{order['attempt']}"
    try:
        checkout = epoint.payments.create(order["total"], order["epoint_order_id"], description=order["title"])
    except OutcomeUnknownError:
        order["state"] = "needs_check"
        return "We are checking your payment.", 202
    order["transaction"] = checkout.transaction
    order["state"] = "pending"
    return redirect(checkout.redirect_url)


@app.post("/payments/epoint/callback")
def callback():
    try:
        tx = epoint.verify_callback(request.form)
    except SignatureError:
        abort(400)

    order = next((o for o in ORDERS.values() if o.get("epoint_order_id") == tx.order_id), None)
    if order and tx.matches(order_id=order["epoint_order_id"], amount=order["total"]):
        if tx.paid:
            order["state"] = "paid"
        elif tx.failed and order["state"] == "pending":
            order["state"] = "failed"
    return "OK"


@app.get("/orders/<number>/state")
def state(number):
    order = ORDERS.get(number) or abort(404)
    return jsonify(state=order["state"])
```

`request.form` `MultiDict` obyektidir və `verify_callback` onu istənilən digər mapping kimi oxuyur. Flask-da standart olaraq CSRF qoruması yoxdur. Flask-WTF-in `CSRFProtect` qorumasından istifadə edirsinizsə, callback view-unu `@csrf.exempt` ilə azad edin.

Klient import zamanı yaradılır və bütün sorğular tərəfindən paylaşılır. Bu təhlükəsizdir: `httpx.Client` bir neçə thread-dən istifadə oluna bilər.
