# Invoices

Epoint invoices are payment requests you send to a customer by SMS or e-mail. The customer opens the link and pays on the Epoint page. They suit services billed by period, such as rent, tuition or maintenance.

## Creating an invoice

```python
from datetime import date

invoice_id = ep.invoices.create(
    "350.00",
    date(2026, 3, 1),
    date(2026, 3, 31),
    name="Office rent, March",
    description="Unit 4B",
    phone="+994501234567",
    email="client@example.com",
)
```

The first three arguments are the amount and the period. Dates can be `date` objects or ISO strings such as `"2026-03-01"`. Everything else is a keyword argument:

| Argument | Default | Meaning |
| --- | --- | --- |
| `name` | none | Invoice title |
| `description` | none | Longer text |
| `phone` | none | Customer phone, up to 32 characters |
| `email` | none | Customer e-mail, up to 254 characters |
| `tin` | none | Customer tax id (VÖEN), sent as `inn` |
| `contract_number` | none | Your contract number |
| `merchant_order_id` | none | Your own reference |
| `display` | `True` | Whether the invoice is shown |
| `save_as_template` | `False` | Keep it as a template in the cabinet |
| `installment` | `False` | Allow paying it in installments |

`create()` returns the new invoice id as an `int`, or `None` if Epoint did not send one.

## Updating

`update()` takes the invoice id first, then the same arguments as `create()`:

```python
result = ep.invoices.update(invoice_id, "380.00", "2026-03-01", "2026-03-31", name="Office rent, March")
result.ok
```

## Reading

```python
invoice = ep.invoices.get(invoice_id)
print(invoice.status, invoice.amount, invoice.period_from, invoice.period_to)

for invoice in ep.invoices.list():
    print(invoice.id, invoice.name, invoice.status)
```

`list()` accepts `kind` and `order`, which are passed to Epoint as its `type` and `order` filters. Each item is an {py:class}`~epoint_sdk.Invoice` with `id`, `amount`, `status`, `name`, `description`, `phone`, `email`, `period_from`, `period_to` and `raw`. Reading is safe to repeat, so these calls are retried on network errors.

## Sending

```python
ep.invoices.send_sms(invoice_id, "+994501234567")
ep.invoices.send_email(invoice_id, "client@example.com")
```

Both return a `Result`.

## Getting paid

When the customer pays an invoice, the result arrives in the usual signed callback. Use `merchant_order_id` or the period to connect it to your own records.
