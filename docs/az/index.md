# Epoint Python SDK

Azərbaycanın [Epoint](https://epoint.az) ödəniş sistemi üçün tipli Python klienti. Epoint-in bütün endpoint-lərini əhatə edir, həm sinxron, həm asinxron kodda işləyir, callback imzalarını sizin əvəzinizə yoxlayır və elə qurulub ki, eyni ödəniş təsadüfən iki dəfə göndərilməsin.

```python
from epoint_sdk import Epoint

with Epoint("i000000001", "PRIVATE_KEY",
            success_url="https://shop.az/ok", error_url="https://shop.az/fail") as ep:
    checkout = ep.payments.create("19.90", "ORDER-1042", description="Pro plan")
    print(checkout.redirect_url)
```

Müştəri `redirect_url` ünvanını açır, Epoint səhifəsində ödəniş edir və saytınıza qayıdır. Bundan sonra Epoint serverinizə imzalanmış callback göndərir. Bir sətir kod onu tipli nəticəyə çevirir:

```python
tx = ep.verify_callback(request.POST)
if tx.paid:
    fulfil(tx.order_id, tx.amount, tx.transaction)
```

## SDK nə verir

- **Bütün endpoint-lər.** Kartla ödəniş, yadda saxlanmış kartlar, karta ödəniş (payout), geri qaytarma, ön avtorizasiya, bölünmüş ödəniş, taksit, elektron pul kisələri, Apple Pay və Google Pay, hesab-fakturalar və B2B bank köçürmələri.
- **İmzalı sorğular və callback-lər.** Sorğular məxfi açarınızla imzalanır. Callback-dən heç bir məlumat oxunmazdan əvvəl onun imzası sabit vaxtda yoxlanılır.
- **İkiqat ödəniş yoxdur.** Pul hərəkət etdirən sorğu nəticəsi bəlli olmayan xətadan sonra heç vaxt təkrar göndərilmir. Əvəzində `order_id` ilə birlikdə `OutcomeUnknownError` alırsınız və yenidən cəhd etməzdən əvvəl vəziyyəti yoxlaya bilirsiniz.
- **Dəqiq məbləğlər.** Məbləğlər əvvəldən axıradək `Decimal` tipindədir. `1.005`, `0`, `NaN` və `True` kimi dəyərlər heç bir sorğu göndərilmədən rədd edilir.
- **Sinxron və asinxron.** `Epoint` və `AsyncEpoint` siniflərinin metodları eynidir.
- **Rahat konfiqurasiya.** Açarlar və ayarlar koddan, `EPOINT_*` mühit dəyişənlərindən və ya konfiqurasiya faylından oxunur.

## Haradan başlamalı

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Quraşdırma
:link: installation
:link-type: doc

Virtual mühitin yaradılması və paketin Linux, macOS və ya Windows-da quraşdırılması.
:::

:::{grid-item-card} Tacir hesabı və açarlar
:link: keys
:link-type: doc

Açıq və məxfi açar nədir, haradan alınır və necə qorunur.
:::

:::{grid-item-card} Sürətli başlanğıc
:link: quickstart
:link-type: doc

Sorğudan təsdiqlənmiş callback-ə qədər ilk ödənişiniz, addım-addım.
:::

:::{grid-item-card} Callback-lər
:link: guides/callbacks
:link-type: doc

Ödənişi düzgün təsdiqləmək qaydası və nəticənin hər sahəsinin mənası.
:::

:::{grid-item-card} Nümunələr
:link: examples/django
:link-type: doc

Django, FastAPI və Flask üçün tam ödəniş və callback kodu.
:::

:::{grid-item-card} API arayışı
:link: reference/api
:link-type: doc

Bütün siniflər, metodlar və ayarlar bir yerdə.
:::
::::

## Tələblər

Python 3.10, 3.11, 3.12 və ya 3.13. SDK [httpx](https://www.python-httpx.org/), [goodconf](https://github.com/lincolnloop/goodconf), pydantic və PyYAML paketlərindən istifadə edir. Real ödənişlər üçün Epoint tacir hesabı lazımdır. Kodu yazarkən isə [lokal sandbox](guides/testing.md) kifayət edir.

```{toctree}
:hidden:
:caption: Başlanğıc

installation
keys
quickstart
configuration
```

```{toctree}
:hidden:
:caption: Bələdçilər

guides/payments
guides/callbacks
guides/refunds
guides/preauth
guides/saved-cards
guides/split
guides/installments
guides/wallets
guides/apple-google-pay
guides/invoices
guides/transfers
guides/async
guides/errors
guides/reliability
guides/messages
guides/security
guides/testing
```

```{toctree}
:hidden:
:caption: Nümunələr

examples/django
examples/fastapi
examples/flask
examples/subscriptions
examples/reconciliation
```

```{toctree}
:hidden:
:caption: Arayış

reference/api
reference/endpoints
reference/changelog
faq
```

```{toctree}
:hidden:
:caption: Layihə

development
about
```
