# Apple Pay and Google Pay

Apple Pay and Google Pay work through a widget that you embed on your own page, instead of a redirect. The customer taps the button, approves with Face ID, a fingerprint or a PIN, and stays on your site. These token payments are enabled by Epoint per merchant.

## How it works

1. Your server creates a widget with `ep.widgets.create()`. Epoint returns a `widget_url`.
2. Your page shows `widget_url` in an `iframe`.
3. When the customer finishes, the widget sends a `postMessage` to your page.
4. Your page tells your server, and the server confirms the payment with `payments.status()` or waits for the signed callback.

The `postMessage` in step 3 is only a hint. The browser can be tampered with, so the server must confirm the result in step 4.

## Step 1. Create the widget

```python
widget = ep.widgets.create("19.90", "ORDER-1043", "Pro plan")
order.epoint_transaction = widget.transaction
order.save()
```

All three arguments are required: amount, order id and description. The answer is a {py:class}`~epoint_sdk.Widget`:

| Field | Meaning |
| --- | --- |
| `widget_url` | The address to load in the `iframe` |
| `transaction` | Epoint's transaction id |
| `origin` | The scheme and host of `widget_url`, for checking `postMessage` |
| `trace_id` | Epoint's trace id |
| `raw` | The full answer |

## Step 2. Embed it

```html
<iframe src="{{ widget.widget_url }}" allow="payment" title="Apple Pay / Google Pay"
        style="width:100%;height:240px;border:0"></iframe>
```

The `allow="payment"` attribute is required. Your page must also send a `Permissions-Policy` header that allows payments from Epoint:

```text
Permissions-Policy: payment=(self "https://epoint.az")
```

In Django, for example, set it in a middleware or on the response:

```python
response["Permissions-Policy"] = 'payment=(self "https://epoint.az")'
```

## Step 3. Listen for the message

```html
<script>
addEventListener("message", (event) => {
  if (event.origin !== "{{ widget.origin }}") return;
  fetch("{% url 'order-check' order.number %}", {
    method: "POST",
    headers: {"X-CSRFToken": "{{ csrf_token }}"},
  }).then(() => location.reload());
});
</script>
```

Always compare `event.origin` with `widget.origin`. Messages from any other origin must be ignored.

If you want to read the message on the server, for logging or to show a message early, pass it to `WidgetMessage.from_event`:

```python
from epoint_sdk import WidgetMessage

hint = WidgetMessage.from_event(json.loads(request.body))
hint.looks_paid   # True if the widget says "success"
```

{py:class}`~epoint_sdk.WidgetMessage` reads `status`, `order_id`, `transaction`, `amount`, `card_mask` and `message`. The property is called `looks_paid`, not `paid`, on purpose: it is unverified data from the browser.

## Step 4. Confirm on the server

```python
def order_check(request, number):
    order = get_object_or_404(Order, number=number)
    tx = ep.payments.status(order.epoint_transaction)
    if tx.paid and tx.matches(order_id=order.number, amount=order.total):
        order.mark_paid(transaction=tx.transaction)
    return JsonResponse({"paid": order.is_paid})
```

The signed callback still arrives as well, so the order may already be paid by the time this view runs. Keep the handler idempotent.

## Split payments in the widget

```python
checkout = ep.widgets.split("100.00", "ORDER-5004", "i000000002", "85.00", description="Lamp")
```

The arguments follow `split.create()`. The SDK returns the answer as a `Redirect`, and the full JSON from Epoint is available in `checkout.raw`.

## Checking an origin yourself

`origin_of(url)` returns the lower case scheme and host of any URL, or `None` if it has none. `Widget.origin` uses it:

```python
from epoint_sdk import origin_of

origin_of("https://epoint.az/widget/abc?x=1")   # "https://epoint.az"
```
