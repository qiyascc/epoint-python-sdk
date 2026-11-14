# Bölünmüş ödəniş

Bölünmüş ödəniş müştəridən bir ödəniş alır və onun bir hissəsini başqa Epoint tacirinə, yəni tərəfdaşa verir. Marketpleyslər bundan satıcılara ödəmək, platformalar isə gəliri satış tərəfdaşları ilə bölüşmək üçün istifadə edir.

Hər bölünmüş ödəniş sorğusu iki əlavə dəyər qəbul edir:

`partner`
: Tərəfdaşın Epoint açıq açarı, məsələn `i000000002`. `split_user` adı ilə göndərilir.

`partner_amount`
: Tərəfdaşın payı. Düzgün məbləğ olmalıdır və ümumi məbləğdən böyük ola bilməz. Daha böyük pay heç nə göndərilməzdən əvvəl `InvalidRequestError` qaldırır.

## Ödəniş səhifəsində

```python
checkout = ep.split.create(
    "100.00",
    "ORDER-5001",
    "i000000002",
    "85.00",
    description="Nur Studiyasından əl işi çıraq",
)
redirect(checkout.redirect_url)
```

İlk dörd arqument ümumi məbləğ, sifariş identifikatoru, tərəfdaş və tərəfdaşın payıdır. Açar sözlü arqumentlər `installment` istisna olmaqla `payments.create()` ilə eynidir. Cavab `Redirect` olur.

## Yadda saxlanmış kartla

```python
tx = ep.split.charge(card_id, "100.00", "ORDER-5002", "i000000002", "85.00")
```

`cards.charge()` kimi pulu dərhal çıxır və `Transaction` qaytarır. Kart rədd ediləndə `failed` xassəsi `True` olan tranzaksiya qayıdır.

## Kartı bölünmüş ödənişlə yadda saxlamaq

```python
reg = ep.split.register_and_pay("100.00", "ORDER-5003", "i000000002", "85.00")
redirect(reg.redirect_url)
```

Cavab `CardRegistration` olur.

## Callback-də

Bölünmüş ödənişin callback-i tərəfdaşın payını `split_amount` sahəsində gətirir:

```python
tx = ep.verify_callback(request.POST)
if tx.paid:
    record_sale(tx.order_id, total=tx.amount, partner_share=tx.split_amount)
```

## Apple Pay və Google Pay

Vidjetin də bölünmüş variantı var: `ep.widgets.split(...)`. Bax: [Apple Pay və Google Pay](apple-google-pay.md#vidjetdə-bölünmüş-ödəniş).
