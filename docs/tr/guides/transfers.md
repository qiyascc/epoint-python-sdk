# B2B transferler

B2B transferler, Epoint bakiyenizden bir şirketin banka hesabına IBAN ile para gönderir. Tedarikçilere ödeme yapmak veya iş ortaklarıyla hesaplaşmak için kullanışlıdır. Bu özelliği Epoint her üye işyeri için ayrıca açar.

## Transfer göndermek

```python
transfer = ep.transfers.create(
    "PAY-2026-0042",
    "1500.00",
    iban="AZ21NABZ00000000137010001944",
    name="Nur Studio MMC",
    tin="1234567890",
    bank_code="505000",
    description="42 numaralı fatura, şubat",
    bank_name="Örnek Banka",
    email="finance@nur.az",
    webhook_url="https://shop.az/epoint/b2b-webhook/",
)
print(transfer.status)
```

Önce sipariş kimliği ve tutar gelir. Geri kalanlar anahtar kelimeli argümanlardır:

| Argüman | Zorunlu | Anlamı |
| --- | --- | --- |
| `iban` | evet | Alıcının IBAN'ı, en fazla 34 karakter. Boşluklar silinir, harfler büyütülür |
| `name` | evet | Alıcı şirketin adı |
| `tin` | evet | Alıcının vergi numarası (VÖEN) |
| `bank_code` | evet | Alıcının banka kodu |
| `description` | evet | Ödemenin açıklaması |
| `bank_name` | hayır | Alıcının banka adı |
| `email` | hayır | Alıcının e-postası |
| `address` | hayır | Alıcının adresi |
| `additional_info` | hayır | Diğer bilgiler |
| `webhook_url` | hayır | Epoint'in transfer sonucunu bildireceği adres |

Diğer çağrılardan farklı olarak bu istek imzalı bir JSON gövdesiyle gönderilir. Yanıt `order_id`, `status`, `bulk_id`, `amount`, `payee_iban`, `payee_name` ve `raw` alanlarına sahip bir {py:class}`~epoint_sdk.Transfer` nesnesidir.

Örnekteki hesap bilgileri uydurmadır. Tedarikçinin faturasındaki gerçek bilgileri kullanın.

## Transferi sorgulamak

```python
transfer = ep.transfers.status("PAY-2026-0042")
print(transfer.status)
```

Bu, sipariş kimliğiyle yapılan düz bir `GET` isteğidir. İmzalanmaz ve ağ hatalarında yeniden denenir.

## Güvenlik

Transfer oluşturmak para hareketi yaratır, bu yüzden sonucu belirsiz bir hatadan sonra asla tekrarlanmaz. `OutcomeUnknownError` alırsanız yeniden denemeden önce aynı sipariş kimliğiyle `transfers.status()` çağırın.
