# Ön provizyon

Ön provizyon, müşterinin kartındaki parayı çekmeden bloke eder. Tutarı daha sonra, örneğin ürün kargolandığında veya hizmet verildiğinde tahsil edersiniz. Oteller, araç kiralama firmaları ve stoku elle onaylayan pazaryerleri bu yöntemi kullanır.

## 1. adım. Parayı bloke edin

`hold()`, `payments.create()` gibi çalışır: müşteri için bir ödeme sayfası döndürür.

```python
checkout = ep.payments.hold(
    "150.00",
    "BOOKING-77",
    description="Oda depozitosu",
)
redirect(checkout.redirect_url)
```

`create()` gibi `description`, `language`, `currency`, `success_url`, `error_url` ve `other_attr` argümanlarını kabul eder. `checkout.transaction` değerini rezervasyonla birlikte saklayın.

Callback her zamanki gibi gelir. [Callback'ler](callbacks.md) sayfasında anlatıldığı gibi doğrulayın.

## 2. adım. Tahsil edin

Çekime hazır olduğunuzda tutarı tahsil edin:

```python
result = ep.payments.capture(booking.epoint_transaction, "150.00")
if result.ok:
    booking.mark_charged()
```

Tutar ikinci konumsal argümandır. Bloke edilenden daha az tutar tahsil edip edemeyeceğinize Epoint ve üye işyeri bankanız karar verir, bu yüzden kısmi tahsilata güvenmeden önce Epoint ile teyit edin.

## Blokeyi kaldırmak

Parayı tahsil etmeden serbest bırakmak için işlemi iptal edin:

```python
ep.payments.reverse(booking.epoint_transaction)
```

## Güvenlik

`hold()` ve `capture()` para hareketi yaratır, bu yüzden sonucu belirsiz bir hatadan sonra ikisi de tekrarlanmaz. Zaman aşımında `OutcomeUnknownError` fırlatılır. Yeniden denemeden önce `payments.status()` ile kontrol edin.

## Bloke ne kadar sürer

Kart ağları tahsil edilmeyen bir blokeyi bir süre sonra kaldırır. Süre bankaya bağlıdır, bu yüzden mümkün olan en kısa sürede tahsil edin ve uzun blokelere dayanan bir plan kurmayın.
