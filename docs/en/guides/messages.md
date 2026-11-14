# Messages

Every message the SDK produces, from validation errors to network errors, lives in one YAML file inside the package: `epoint_sdk/messages.yaml`. Nothing is hard coded, so you can translate the messages or reword them for your users.

## Replacing messages

From a file:

```yaml
value:
  amount_positive: "{field} sıfırdan böyük olmalıdır, verilən: {value}"
  empty: "{field} boş ola bilməz"
error:
  connect: "Epoint ilə əlaqə qurulmadı, heç nə göndərilmədi: {error}"
```

```python
from epoint_sdk import messages

messages.use("messages.az.yaml")
```

Or from a dict with dotted keys:

```python
messages.use({"value.empty": "{field} boş ola bilməz"})
```

Nested dicts work too:

```python
messages.use({"error": {"refused": "Epoint sorğunu qəbul etmədi"}})
```

You only need to list the messages you want to change. The rest keep their default text.

## Rules

- Keys must already exist in the packaged file. An unknown key raises `KeyError` with its name, so a typo is caught at once.
- Placeholders in braces, such as `{field}` and `{value}`, are filled in with `str.format`. Keep the ones the original message uses.
- `messages.use()` changes the messages for the whole process. Call it once at start up.
- `messages.reset()` goes back to the packaged text.

## Reading messages

```python
messages.text("value.empty", field="order_id")   # "order_id cannot be empty"
messages.catalog()["error.refused"]              # "Epoint refused the request"
```

## All keys

Settings descriptions
: `settings.description`, `settings.public_key`, `settings.private_key`, `settings.base_url`, `settings.endpoints`, `settings.language`, `settings.currency`, `settings.success_url`, `settings.error_url`, `settings.timeout`, `settings.connect_timeout`, `settings.max_retries`, `settings.backoff_base`, `settings.backoff_cap`, `settings.user_agent`, `settings.allow_insecure_http`

Validation
: `value.amount_type`, `value.amount_positive`, `value.amount_scale`, `value.amount_finite`, `value.empty`, `value.too_long`, `value.months`, `value.split_amount`

Errors
: `error.missing_keys`, `error.insecure`, `error.base_url`, `error.too_large`, `error.signature`, `error.data`, `error.data_object`, `error.callback_fields`, `error.connect`, `error.timeout`, `error.unknown_outcome`, `error.status`, `error.body`, `error.refused`

The settings descriptions are read once, when the package is imported, so overriding them later does not change `Settings`. The validation and error messages are read every time they are raised.
