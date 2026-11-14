# B2B köçürmələr

B2B köçürmələr Epoint balansınızdan şirkətin bank hesabına IBAN ilə pul göndərir. Təchizatçılara ödəmək və ya tərəfdaşlarla hesablaşmaq üçün əlverişlidir. Bu imkanı Epoint hər tacir üçün ayrıca aktivləşdirir.

## Köçürmə göndərmək

```python
transfer = ep.transfers.create(
    "PAY-2026-0042",
    "1500.00",
    iban="AZ21NABZ00000000137010001944",
    name="Nur Studio MMC",
    tin="1234567890",
    bank_code="505000",
    description="42 nömrəli hesab-faktura, fevral",
    bank_name="Nümunə Bank",
    email="finance@nur.az",
    webhook_url="https://shop.az/epoint/b2b-webhook/",
)
print(transfer.status)
```

Əvvəlcə sifariş identifikatoru və məbləğ gəlir. Qalanları açar sözlü arqumentlərdir:

| Arqument | Mütləqdir | Mənası |
| --- | --- | --- |
| `iban` | bəli | Alanın IBAN-ı, 34 simvola qədər. Boşluqlar silinir, hərflər böyük hərfə çevrilir |
| `name` | bəli | Alan şirkətin adı |
| `tin` | bəli | Alanın VÖEN-i |
| `bank_code` | bəli | Alanın bank kodu |
| `description` | bəli | Ödənişin təyinatı |
| `bank_name` | xeyr | Alanın bankının adı |
| `email` | xeyr | Alanın e-poçtu |
| `address` | xeyr | Alanın ünvanı |
| `additional_info` | xeyr | Digər məlumatlar |
| `webhook_url` | xeyr | Epoint-in köçürmənin nəticəsini bildirəcəyi ünvan |

Digər sorğulardan fərqli olaraq bu sorğu imzalı JSON gövdəsi ilə göndərilir. Cavab `order_id`, `status`, `bulk_id`, `amount`, `payee_iban`, `payee_name` və `raw` sahələri olan {py:class}`~epoint_sdk.Transfer` obyektidir.

Nümunədəki hesab rekvizitləri uydurmadır. Təchizatçının hesab-fakturasındakı real rekvizitlərdən istifadə edin.

## Köçürməni yoxlamaq

```python
transfer = ep.transfers.status("PAY-2026-0042")
print(transfer.status)
```

Bu, sifariş identifikatoru ilə adi `GET` sorğusudur. İmzalanmır və şəbəkə xətalarında təkrarlanır.

## Təhlükəsizlik

Köçürmə yaratmaq pul hərəkət etdirir, ona görə nəticəsi bəlli olmayan xətadan sonra heç vaxt təkrarlanmır. `OutcomeUnknownError` alsanız, yenidən cəhd etməzdən əvvəl eyni sifariş identifikatoru ilə `transfers.status()` çağırın.
