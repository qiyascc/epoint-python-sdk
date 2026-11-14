# Ön avtorizasiya

Ön avtorizasiya müştərinin kartında pulu çıxmadan bloklayır. Məbləği sonra, məsələn mal göndəriləndə və ya xidmət göstəriləndə silirsiniz. Otellər, avtomobil icarəsi şirkətləri və anbar qalığını əllə təsdiqləyən marketpleyslər bu üsuldan istifadə edir.

## 1-ci addım. Pulu bloklayın

`hold()` metodu `payments.create()` kimi işləyir: müştəri üçün ödəniş səhifəsi qaytarır.

```python
checkout = ep.payments.hold(
    "150.00",
    "BOOKING-77",
    description="Otaq üçün depozit",
)
redirect(checkout.redirect_url)
```

O da `create()` kimi `description`, `language`, `currency`, `success_url`, `error_url` və `other_attr` arqumentlərini qəbul edir. `checkout.transaction` dəyərini bronla birlikdə saxlayın.

Callback adi qaydada gəlir. Onu [Callback-lər](callbacks.md) səhifəsində göstərildiyi kimi yoxlayın.

## 2-ci addım. Məbləği silin

Pulu çıxmağa hazır olanda məbləği silin:

```python
result = ep.payments.capture(booking.epoint_transaction, "150.00")
if result.ok:
    booking.mark_charged()
```

Məbləğ ikinci mövqe arqumentidir. Bloklanandan az məbləğ silmək olub-olmadığını Epoint və ekvayer bankınız müəyyən edir, ona görə qismən silməyə güvənməzdən əvvəl bunu Epoint ilə dəqiqləşdirin.

## Bloku açmaq

Məbləği silmədən bloku açmaq üçün tranzaksiyanı ləğv edin:

```python
ep.payments.reverse(booking.epoint_transaction)
```

## Təhlükəsizlik

`hold()` və `capture()` pul hərəkət etdirir, ona görə nəticəsi bəlli olmayan xətadan sonra heç biri təkrarlanmır. Gözləmə müddəti bitəndə `OutcomeUnknownError` qaldırılır. Yenidən cəhd etməzdən əvvəl `payments.status()` ilə yoxlayın.

## Blok nə qədər qalır

Kart şəbəkələri silinməyən bloku müəyyən müddətdən sonra açır. Dəqiq müddət bankdan asılıdır, ona görə məbləği mümkün qədər tez silin və uzun bloklara əsaslanan plan qurmayın.
