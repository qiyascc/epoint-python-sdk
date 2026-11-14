# Epoint Python SDK

Azerbaycan'daki [Epoint](https://epoint.az) ödeme altyapısı için tip güvenli bir Python istemcisi. Epoint'in tüm uç noktalarını kapsar, hem senkron hem asenkron kodda çalışır, callback imzalarını sizin yerinize doğrular ve aynı ödemenin yanlışlıkla iki kez gönderilmemesi için tasarlanmıştır.

```python
from epoint_sdk import Epoint

with Epoint("i000000001", "PRIVATE_KEY",
            success_url="https://shop.az/ok", error_url="https://shop.az/fail") as ep:
    checkout = ep.payments.create("19.90", "ORDER-1042", description="Pro plan")
    print(checkout.redirect_url)
```

Müşteri `redirect_url` adresini açar, Epoint sayfasında ödemeyi yapar ve sitenize döner. Ardından Epoint sunucunuza imzalı bir callback gönderir. Tek satırlık kod bunu tipli bir sonuca dönüştürür:

```python
tx = ep.verify_callback(request.POST)
if tx.paid:
    fulfil(tx.order_id, tx.amount, tx.transaction)
```

## SDK neler sunar

- **Tüm uç noktalar.** Kartla ödeme, kayıtlı kartlar, karta ödeme (payout), iadeler, ön provizyon, bölünmüş ödeme, taksit, dijital cüzdanlar, Apple Pay ve Google Pay, faturalar ve B2B banka transferleri.
- **İmzalı istekler ve callback'ler.** İstekler gizli anahtarınızla imzalanır. Callback'ten herhangi bir veri okunmadan önce imzası sabit sürede doğrulanır.
- **Çift çekim yok.** Para hareketi yaratan bir istek, sonucu belirsiz bir hatadan sonra asla yeniden gönderilmez. Bunun yerine `order_id` ile birlikte `OutcomeUnknownError` alırsınız ve yeniden denemeden önce durumu kontrol edebilirsiniz.
- **Kesin tutarlar.** Tutarlar baştan sona `Decimal` olarak işlenir. `1.005`, `0`, `NaN` ve `True` gibi değerler hiçbir istek gönderilmeden reddedilir.
- **Senkron ve asenkron.** `Epoint` ve `AsyncEpoint` sınıflarının metotları aynıdır.
- **Esnek yapılandırma.** Anahtarlar ve ayarlar koddan, `EPOINT_*` ortam değişkenlerinden veya bir yapılandırma dosyasından okunur.

## Nereden başlamalı

::::{grid} 1 2 2 2
:gutter: 3

:::{grid-item-card} Kurulum
:link: installation
:link-type: doc

Sanal ortamın oluşturulması ve paketin Linux, macOS veya Windows'a kurulması.
:::

:::{grid-item-card} Üye işyeri hesabı ve anahtarlar
:link: keys
:link-type: doc

Açık ve gizli anahtar nedir, nereden alınır ve nasıl korunur.
:::

:::{grid-item-card} Hızlı başlangıç
:link: quickstart
:link-type: doc

İstekten doğrulanmış callback'e kadar ilk ödemeniz, adım adım.
:::

:::{grid-item-card} Callback'ler
:link: guides/callbacks
:link-type: doc

Bir ödemeyi doğru şekilde onaylamak ve sonucun her alanının anlamı.
:::

:::{grid-item-card} Örnekler
:link: examples/django
:link-type: doc

Django, FastAPI ve Flask için eksiksiz ödeme ve callback kodu.
:::

:::{grid-item-card} API başvurusu
:link: reference/api
:link-type: doc

Tüm sınıflar, metotlar ve ayarlar tek bir yerde.
:::
::::

## Gereksinimler

Python 3.10, 3.11, 3.12 veya 3.13. SDK [httpx](https://www.python-httpx.org/), [goodconf](https://github.com/lincolnloop/goodconf), pydantic ve PyYAML paketlerini kullanır. Gerçek ödemeler için bir Epoint üye işyeri hesabı gerekir. Geliştirme sırasında [yerel sandbox](guides/testing.md) yeterlidir.

```{toctree}
:hidden:
:caption: Başlarken

installation
keys
quickstart
configuration
```

```{toctree}
:hidden:
:caption: Kılavuzlar

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
:caption: Örnekler

examples/django
examples/fastapi
examples/flask
examples/subscriptions
examples/reconciliation
```

```{toctree}
:hidden:
:caption: Başvuru

reference/api
reference/endpoints
reference/changelog
faq
```

```{toctree}
:hidden:
:caption: Proje

development
about
```
