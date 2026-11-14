# Installments

With installments the customer pays in monthly parts with a bank card that supports it, while you receive the payment as usual. Installments must be enabled for your merchant account.

There are two ways to offer them.

## Let the customer choose on the Epoint page

Add `installment=True` to a normal payment:

```python
ep.payments.create("1200.00", "ORDER-6001", description="Laptop", installment=True)
```

Epoint shows the available plans on its page.

## Show the plans on your own page

### Step 1. Load the plans

```python
plans = ep.installments.plans("ORDER-6002", "1200.00")
for plan in plans:
    print(plan.card_id, plan.name, plan.months)
```

`plans()` takes your order id and, optionally, the amount, plus `language` and `currency` as keywords. It returns a list of {py:class}`~epoint_sdk.InstallmentPlan`:

| Field | Meaning |
| --- | --- |
| `card_id` | The installment card program, sent back when you pay |
| `name` | Its display name |
| `months` | The month counts it supports, as a tuple of ints |

Loading plans is safe to repeat, so the SDK retries it on network errors.

### Step 2. Show them

```html
{% for plan in plans %}
  <fieldset>
    <legend>{{ plan.name }}</legend>
    {% for m in plan.months %}
      <label>
        <input type="radio" name="plan" value="{{ plan.card_id }}:{{ m }}">
        {{ m }} months
      </label>
    {% endfor %}
  </fieldset>
{% endfor %}
```

### Step 3. Pay with the chosen plan

```python
card_id, months = request.POST["plan"].split(":")
checkout = ep.installments.create(
    "1200.00",
    "ORDER-6002",
    card_id,
    int(months),
    description="Laptop",
)
redirect(checkout.redirect_url)
```

`months` must be a positive whole number, otherwise `InvalidRequestError` is raised. The other keyword arguments match `payments.create()`. The answer is a `Redirect`, and the result comes in the usual callback.

Always check on the server that the plan and month count the customer sent really came from `plans()`. Form values can be changed in the browser.
