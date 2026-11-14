# B2B transfers

B2B transfers send money from your Epoint balance to a company's bank account by IBAN. They are useful for paying suppliers or settling with partners. The feature is enabled by Epoint per merchant.

## Sending a transfer

```python
transfer = ep.transfers.create(
    "PAY-2026-0042",
    "1500.00",
    iban="AZ21NABZ00000000137010001944",
    name="Nur Studio LLC",
    tin="1234567890",
    bank_code="505000",
    description="Invoice 42, February",
    bank_name="Example Bank",
    email="finance@nur.az",
    webhook_url="https://shop.az/epoint/b2b-webhook/",
)
print(transfer.status)
```

The order id and amount come first. The rest are keyword arguments:

| Argument | Required | Meaning |
| --- | --- | --- |
| `iban` | yes | Recipient IBAN, up to 34 characters. Spaces are removed and letters upper cased |
| `name` | yes | Recipient company name |
| `tin` | yes | Recipient tax id (VÖEN) |
| `bank_code` | yes | Recipient bank code |
| `description` | yes | Purpose of the payment |
| `bank_name` | no | Recipient bank name |
| `email` | no | Recipient e-mail |
| `address` | no | Recipient address |
| `additional_info` | no | Any other details |
| `webhook_url` | no | Address where Epoint reports the transfer result |

Unlike the other calls, this request is sent as a signed JSON body. The answer is a {py:class}`~epoint_sdk.Transfer` with `order_id`, `status`, `bulk_id`, `amount`, `payee_iban`, `payee_name` and `raw`.

The account details in the example are made up. Use the real details from the supplier's invoice.

## Checking a transfer

```python
transfer = ep.transfers.status("PAY-2026-0042")
print(transfer.status)
```

This is a plain `GET` by order id. It is not signed and is retried on network errors.

## Safety

Creating a transfer moves money, so it is never retried after an unclear failure. If you get `OutcomeUnknownError`, call `transfers.status()` with the same order id before you try again.
