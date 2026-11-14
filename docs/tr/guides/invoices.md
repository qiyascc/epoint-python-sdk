# Faturalar

Epoint faturaları, müşteriye SMS veya e-posta ile gönderdiğiniz ödeme talepleridir. Müşteri bağlantıyı açar ve Epoint sayfasında öder. Kira, okul ücreti veya bakım gibi dönemsel olarak faturalanan hizmetler için uygundur.

## Fatura oluşturmak

```python
from datetime import date

invoice_id = ep.invoices.create(
    "350.00",
    date(2026, 3, 1),
    date(2026, 3, 31),
    name="Ofis kirası, mart",
    description="4B numaralı ofis",
    phone="+994501234567",
    email="client@example.com",
)
```

İlk üç argüman tutar, dönemin başlangıcı ve sonudur. Tarihler `date` nesnesi veya `"2026-03-01"` gibi ISO string olarak verilebilir. Geri kalan her şey anahtar kelimeli argümandır:

| Argüman | Varsayılan | Anlamı |
| --- | --- | --- |
| `name` | yok | Fatura başlığı |
| `description` | yok | Daha uzun metin |
| `phone` | yok | Müşterinin telefonu, en fazla 32 karakter |
| `email` | yok | Müşterinin e-postası, en fazla 254 karakter |
| `tin` | yok | Müşterinin vergi numarası (VÖEN), `inn` adıyla gönderilir |
| `contract_number` | yok | Sözleşme numaranız |
| `merchant_order_id` | yok | Kendi referansınız |
| `display` | `True` | Faturanın gösterilip gösterilmeyeceği |
| `save_as_template` | `False` | Panelde şablon olarak saklamak |
| `installment` | `False` | Taksitle ödemeye izin vermek |

`create()` yeni faturanın kimliğini `int` olarak döndürür, Epoint kimlik göndermezse `None` döndürür.

## Güncellemek

`update()` önce fatura kimliğini, ardından `create()` ile aynı argümanları alır:

```python
result = ep.invoices.update(invoice_id, "380.00", "2026-03-01", "2026-03-31", name="Ofis kirası, mart")
result.ok
```

## Okumak

```python
invoice = ep.invoices.get(invoice_id)
print(invoice.status, invoice.amount, invoice.period_from, invoice.period_to)

for invoice in ep.invoices.list():
    print(invoice.id, invoice.name, invoice.status)
```

`list()`, Epoint'e `type` ve `order` filtreleri olarak iletilen `kind` ve `order` argümanlarını kabul eder. Her öğe `id`, `amount`, `status`, `name`, `description`, `phone`, `email`, `period_from`, `period_to` ve `raw` alanlarına sahip bir {py:class}`~epoint_sdk.Invoice` nesnesidir. Okuma çağrılarını tekrarlamak güvenlidir, bu yüzden ağ hatalarında yeniden denenir.

## Göndermek

```python
ep.invoices.send_sms(invoice_id, "+994501234567")
ep.invoices.send_email(invoice_id, "client@example.com")
```

İkisi de bir `Result` döndürür.

## Ödemeyi almak

Müşteri faturayı ödediğinde sonuç her zamanki imzalı callback ile gelir. Onu kendi kayıtlarınızla eşleştirmek için `merchant_order_id` değerini veya dönemi kullanın.
