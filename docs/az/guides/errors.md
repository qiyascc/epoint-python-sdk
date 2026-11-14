# Xətalar

SDK-nın qaldırdığı bütün istisnalar `EpointError` sinfindən törəyir, ona görə bir `except` bloku hamısını tuta bilir. Hər birində oxunaqlı `message` sahəsi var.

```text
EpointError
├── ConfigurationError
├── InvalidRequestError        (həm də ValueError)
├── SignatureError
├── TransportError
│   ├── NotSentError
│   └── OutcomeUnknownError
├── HTTPStatusError
└── GatewayError
```

## Hansı istisna nə vaxt qaldırılır

| İstisna | Nə vaxt | Nə etməli |
| --- | --- | --- |
| `ConfigurationError` | Açar yoxdur və ya `base_url` localhost xaricində adi `http` ünvanıdır | Konfiqurasiyanı düzəldin. Bu, klient yaradılanda baş verir |
| `InvalidRequestError` | Arqument səhvdir: yanlış məbləğ, boş sifariş identifikatoru, çox uzun mətn, ümumi məbləğdən böyük tərəfdaş payı, müsbət tam ədəd olmayan ay sayı | Giriş məlumatını düzəldin. Heç nə göndərilməyib |
| `SignatureError` | Callback-də data və ya imza yoxdur, imza səhvdir, məlumat çox böyükdür və ya base64 JSON deyil | HTTP 400 ilə cavab verin və sorğunu nəzərə almayın |
| `NotSentError` | Bağlantı bütün cəhdlərdə qurulmayıb, heç nə göndərilməyib | Sonra eyni sifariş identifikatoru ilə yenidən cəhd etmək təhlükəsizdir |
| `OutcomeUnknownError` | Pul hərəkət etdirən sorğu Epoint-ə çatıb, amma aydın cavab gəlməyib | Kor-koranə **təkrarlamayın**. Əvvəlcə vəziyyəti yoxlayın |
| `TransportError` | Oxuma sorğusu (status, siyahılar) bütün cəhdlərdə uğursuz olub | Sonra yenidən cəhd edin |
| `HTTPStatusError` | Epoint HTTP xətası ilə və ya JSON olmayan gövdə ilə cavab verib | Loqa yazın, `status_code` və `body` sahələrinə baxın |
| `GatewayError` | Epoint `status: error` ilə cavab verib | `code` və mesajı oxuyun. Çox vaxt bu, biznes qaydasıdır, məsələn təkrar istifadə olunmuş sifariş identifikatoru |

## Atributlar

`TransportError`, `NotSentError` və `OutcomeUnknownError`
: `path` çağırılan URL-dir, `order_id` isə sorğunun aid olduğu sifarişdir, əgər varsa. `OutcomeUnknownError` problem 5xx cavabı olanda `status_code` da daşıyır.

`HTTPStatusError`
: `status_code`, `body` (açılmış JSON və ya mətnin ilk 200 simvolu) və `path`.

`GatewayError`
: `code` (Epoint-in xəta kodu və ya `None`), `trace_id`, `status_code`, `payload` (bütöv cavab) və `path`. `str(exc)` `[CODE] message (trace TRACE_ID)` şəklində olur.

## Rədd edilmiş kart istisna deyil

Pulu dərhal çıxan çağırışlar, yəni `cards.charge()`, `cards.payout()` və `split.charge()`, həmçinin `payments.status()` rədd edilmiş və ya uğursuz ödəniş üçün xəta qaldırmır, `Transaction` qaytarır. `tx.paid` və `tx.failed` xassələrini yoxlayın. Yalnız Epoint-in tranzaksiya yaratmadan rədd etdiyi sorğu `GatewayError` qaldırır.

## Tipik ödəniş handler-i

```python
from epoint_sdk import (
    GatewayError,
    InvalidRequestError,
    NotSentError,
    OutcomeUnknownError,
)

def start_payment(order):
    try:
        checkout = ep.payments.create(order.total, order.attempt_id, description=order.title)
    except InvalidRequestError as exc:
        return show_error(f"Ödənişə başlamaq mümkün olmadı: {exc.message}")
    except NotSentError:
        return show_error("Ödəniş xidməti əlçatan deyil. Bir dəqiqədən sonra yenidən cəhd edin.")
    except OutcomeUnknownError:
        order.mark_needs_check()
        return show_error("Ödəniş sorğusunu təsdiqləyə bilmədik. Yoxlayıb sizə xəbər verəcəyik.")
    except GatewayError as exc:
        log.warning("Epoint %s sorğusunu rədd etdi: %s", order.attempt_id, exc)
        return show_error("Ödənişə başlamaq mümkün olmadı.")
    order.epoint_transaction = checkout.transaction
    order.save()
    return redirect(checkout.redirect_url)
```

## Mesajları dəyişmək

Bütün mesajlar paketin içindəki YAML faylından gəlir və onları dəyişmək və ya tərcümə etmək olar. Bax: [Mesajlar](messages.md).
