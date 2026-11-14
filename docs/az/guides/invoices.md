# Hesab-fakturalar

Epoint hesab-fakturaları müştəriyə SMS və ya e-poçt ilə göndərdiyiniz ödəniş tələbləridir. Müştəri linki açır və Epoint səhifəsində ödəyir. Kirayə, təhsil haqqı və ya texniki xidmət kimi dövri hesablanan xidmətlər üçün əlverişlidir.

## Hesab-faktura yaratmaq

```python
from datetime import date

invoice_id = ep.invoices.create(
    "350.00",
    date(2026, 3, 1),
    date(2026, 3, 31),
    name="Ofis kirayəsi, mart",
    description="4B saylı otaq",
    phone="+994501234567",
    email="client@example.com",
)
```

İlk üç arqument məbləğ, dövrün başlanğıcı və sonudur. Tarixləri `date` obyekti və ya `"2026-03-01"` kimi ISO sətri şəklində vermək olar. Qalan hər şey açar sözlü arqumentdir:

| Arqument | Standart dəyər | Mənası |
| --- | --- | --- |
| `name` | yoxdur | Hesab-fakturanın başlığı |
| `description` | yoxdur | Daha geniş mətn |
| `phone` | yoxdur | Müştərinin telefonu, 32 simvola qədər |
| `email` | yoxdur | Müştərinin e-poçtu, 254 simvola qədər |
| `tin` | yoxdur | Müştərinin VÖEN-i, `inn` adı ilə göndərilir |
| `contract_number` | yoxdur | Müqavilə nömrəniz |
| `merchant_order_id` | yoxdur | Öz istinad nömrəniz |
| `display` | `True` | Hesab-fakturanın göstərilib-göstərilməməsi |
| `save_as_template` | `False` | Onu kabinetdə şablon kimi saxlamaq |
| `installment` | `False` | Taksitlə ödəməyə icazə vermək |

`create()` yeni hesab-fakturanın identifikatorunu `int` kimi qaytarır. Epoint identifikator göndərməyibsə, `None` qaytarır.

## Yeniləmək

`update()` əvvəlcə hesab-fakturanın identifikatorunu, sonra `create()` ilə eyni arqumentləri qəbul edir:

```python
result = ep.invoices.update(invoice_id, "380.00", "2026-03-01", "2026-03-31", name="Ofis kirayəsi, mart")
result.ok
```

## Oxumaq

```python
invoice = ep.invoices.get(invoice_id)
print(invoice.status, invoice.amount, invoice.period_from, invoice.period_to)

for invoice in ep.invoices.list():
    print(invoice.id, invoice.name, invoice.status)
```

`list()` `kind` və `order` arqumentlərini qəbul edir. Onlar Epoint-ə `type` və `order` filtrləri kimi ötürülür. Hər element `id`, `amount`, `status`, `name`, `description`, `phone`, `email`, `period_from`, `period_to` və `raw` sahələri olan {py:class}`~epoint_sdk.Invoice` obyektidir. Oxuma sorğularını təkrarlamaq təhlükəsizdir, ona görə onlar şəbəkə xətalarında yenidən göndərilir.

## Göndərmək

```python
ep.invoices.send_sms(invoice_id, "+994501234567")
ep.invoices.send_email(invoice_id, "client@example.com")
```

Hər ikisi `Result` qaytarır.

## Ödənişi almaq

Müştəri hesab-fakturanı ödəyəndə nəticə adi imzalı callback ilə gəlir. Onu öz qeydlərinizlə əlaqələndirmək üçün `merchant_order_id` və ya dövrdən istifadə edin.
