# Mesajlar

SDK'nın ürettiği tüm mesajlar, doğrulama hatalarından ağ hatalarına kadar, paketin içindeki tek bir YAML dosyasında durur: `epoint_sdk/messages.yaml`. Hiçbiri koda gömülü değildir, bu yüzden mesajları çevirebilir veya kullanıcılarınız için yeniden yazabilirsiniz.

## Mesajları değiştirmek

Bir dosyadan:

```yaml
value:
  amount_positive: "{field} sıfırdan büyük olmalı, verilen: {value}"
  empty: "{field} boş olamaz"
error:
  connect: "Epoint'e ulaşılamadı, hiçbir şey gönderilmedi: {error}"
```

```python
from epoint_sdk import messages

messages.use("messages.tr.yaml")
```

Veya noktalı anahtarlara sahip bir dict'ten:

```python
messages.use({"value.empty": "{field} boş olamaz"})
```

İç içe dict'ler de çalışır:

```python
messages.use({"error": {"refused": "Epoint isteği reddetti"}})
```

Yalnızca değiştirmek istediğiniz mesajları yazmanız yeterli. Diğerleri varsayılan metinlerinde kalır.

## Kurallar

- Anahtarlar paketteki dosyada zaten bulunmalıdır. Bilinmeyen bir anahtar adıyla birlikte `KeyError` fırlatır, böylece yazım hataları hemen yakalanır.
- `{field}` ve `{value}` gibi süslü parantez içindeki yer tutucular `str.format` ile doldurulur. Orijinal mesajın kullandığı yer tutucuları koruyun.
- `messages.use()` mesajları tüm süreç için değiştirir. Uygulama açılırken bir kez çağırın.
- `messages.reset()` paketteki metinlere geri döner.

## Mesajları okumak

```python
messages.text("value.empty", field="order_id")   # "order_id cannot be empty"
messages.catalog()["error.refused"]              # "Epoint refused the request"
```

## Tüm anahtarlar

Ayar açıklamaları
: `settings.description`, `settings.public_key`, `settings.private_key`, `settings.base_url`, `settings.endpoints`, `settings.language`, `settings.currency`, `settings.success_url`, `settings.error_url`, `settings.timeout`, `settings.connect_timeout`, `settings.max_retries`, `settings.backoff_base`, `settings.backoff_cap`, `settings.user_agent`, `settings.allow_insecure_http`

Doğrulama
: `value.amount_type`, `value.amount_positive`, `value.amount_scale`, `value.amount_finite`, `value.empty`, `value.too_long`, `value.months`, `value.split_amount`

Hatalar
: `error.missing_keys`, `error.insecure`, `error.base_url`, `error.too_large`, `error.signature`, `error.data`, `error.data_object`, `error.callback_fields`, `error.connect`, `error.timeout`, `error.unknown_outcome`, `error.status`, `error.body`, `error.refused`

Ayar açıklamaları paket içe aktarılırken bir kez okunur, bu yüzden onları sonradan değiştirmek `Settings` sınıfını etkilemez. Doğrulama ve hata mesajları ise her fırlatıldıklarında yeniden okunur.
