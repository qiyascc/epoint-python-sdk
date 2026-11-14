# Mesajlar

SDK-nın yaratdığı bütün mesajlar, yoxlama xətalarından şəbəkə xətalarına qədər, paketin içindəki bir YAML faylında saxlanılır: `epoint_sdk/messages.yaml`. Heç biri kodun içinə yazılmayıb, ona görə mesajları tərcümə edə və ya istifadəçiləriniz üçün yenidən yaza bilərsiniz.

## Mesajları əvəz etmək

Fayldan:

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

Və ya nöqtəli açarları olan lüğətdən:

```python
messages.use({"value.empty": "{field} boş ola bilməz"})
```

İç-içə lüğətlər də işləyir:

```python
messages.use({"error": {"refused": "Epoint sorğunu qəbul etmədi"}})
```

Yalnız dəyişmək istədiyiniz mesajları yazmaq kifayətdir. Qalanları standart mətnində qalır.

## Qaydalar

- Açarlar paketdəki faylda artıq mövcud olmalıdır. Naməlum açar adı ilə birlikdə `KeyError` qaldırır, beləliklə hərf səhvi dərhal üzə çıxır.
- `{field}` və `{value}` kimi fiqurlu mötərizədəki yer tutucular `str.format` ilə doldurulur. Orijinal mesajdakı yer tutucuları saxlayın.
- `messages.use()` mesajları bütün proses üçün dəyişir. Onu tətbiq işə düşəndə bir dəfə çağırın.
- `messages.reset()` paketdəki mətnlərə qaytarır.

## Mesajları oxumaq

```python
messages.text("value.empty", field="order_id")   # "order_id cannot be empty"
messages.catalog()["error.refused"]              # "Epoint refused the request"
```

## Bütün açarlar

Ayarların təsvirləri
: `settings.description`, `settings.public_key`, `settings.private_key`, `settings.base_url`, `settings.endpoints`, `settings.language`, `settings.currency`, `settings.success_url`, `settings.error_url`, `settings.timeout`, `settings.connect_timeout`, `settings.max_retries`, `settings.backoff_base`, `settings.backoff_cap`, `settings.user_agent`, `settings.allow_insecure_http`

Yoxlama
: `value.amount_type`, `value.amount_positive`, `value.amount_scale`, `value.amount_finite`, `value.empty`, `value.too_long`, `value.months`, `value.split_amount`

Xətalar
: `error.missing_keys`, `error.insecure`, `error.base_url`, `error.too_large`, `error.signature`, `error.data`, `error.data_object`, `error.callback_fields`, `error.connect`, `error.timeout`, `error.unknown_outcome`, `error.status`, `error.body`, `error.refused`

Ayarların təsvirləri paket import ediləndə bir dəfə oxunur, ona görə onları sonradan dəyişmək `Settings` sinfinə təsir etmir. Yoxlama və xəta mesajları isə hər dəfə qaldırılanda yenidən oxunur.
