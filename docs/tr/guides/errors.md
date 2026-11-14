# Hatalar

SDK'nın fırlattığı tüm istisnalar `EpointError` sınıfından türer, bu yüzden tek bir `except` hepsini yakalayabilir. Her birinde okunabilir bir `message` alanı vardır.

```text
EpointError
├── ConfigurationError
├── InvalidRequestError        (aynı zamanda ValueError)
├── SignatureError
├── TransportError
│   ├── NotSentError
│   └── OutcomeUnknownError
├── HTTPStatusError
└── GatewayError
```

## Hangisi ne zaman fırlatılır

| İstisna | Ne zaman | Ne yapmalı |
| --- | --- | --- |
| `ConfigurationError` | Bir anahtar eksik veya `base_url` localhost dışında düz `http` | Yapılandırmayı düzeltin. İstemci oluşturulurken oluşur |
| `InvalidRequestError` | Bir argüman hatalı: geçersiz tutar, boş sipariş kimliği, çok uzun metin, toplamdan büyük iş ortağı payı, pozitif tam sayı olmayan ay sayısı | Girdiyi düzeltin. Hiçbir şey gönderilmedi |
| `SignatureError` | Callback'te data veya imza yok, imza yanlış, veri çok büyük veya base64 JSON değil | HTTP 400 ile yanıt verin ve isteği yok sayın |
| `NotSentError` | Bağlantı tüm denemelerde kurulamadı, hiçbir şey gönderilmedi | Daha sonra aynı sipariş kimliğiyle tekrar denemek güvenlidir |
| `OutcomeUnknownError` | Para hareketi yaratan bir istek Epoint'e ulaştı ama net bir yanıt gelmedi | Körü körüne **tekrar denemeyin**. Önce durumu kontrol edin |
| `TransportError` | Bir okuma çağrısı (durum, listeler) her denemede başarısız oldu | Daha sonra tekrar deneyin |
| `HTTPStatusError` | Epoint bir HTTP hatasıyla veya JSON olmayan bir gövdeyle yanıt verdi | Loglayın, `status_code` ve `body` alanlarına bakın |
| `GatewayError` | Epoint `status: error` ile yanıt verdi | `code` ve mesajı okuyun. Çoğu zaman bir iş kuralıdır, örneğin tekrar kullanılmış bir sipariş kimliği |

## Nitelikler

`TransportError`, `NotSentError` ve `OutcomeUnknownError`
: `path` çağrılan URL'dir, `order_id` ise varsa çağrının ait olduğu sipariştir. `OutcomeUnknownError`, sorun bir 5xx yanıtıysa `status_code` da taşır.

`HTTPStatusError`
: `status_code`, `body` (çözülmüş JSON veya metnin ilk 200 karakteri) ve `path`.

`GatewayError`
: `code` (Epoint'in hata kodu veya `None`), `trace_id`, `status_code`, `payload` (yanıtın tamamı) ve `path`. `str(exc)` şu biçimdedir: `[CODE] message (trace TRACE_ID)`.

## Reddedilen kart bir istisna değildir

Hemen çekim yapan çağrılar, yani `cards.charge()`, `cards.payout()` ve `split.charge()`, ayrıca `payments.status()`, reddedilen veya başarısız bir ödeme için hata fırlatmaz, bir `Transaction` döndürür. `tx.paid` ve `tx.failed` özelliklerini kontrol edin. Yalnızca Epoint'in işlem oluşturmadan reddettiği bir istek `GatewayError` fırlatır.

## Tipik bir ödeme handler'ı

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
        return show_error(f"Ödeme başlatılamadı: {exc.message}")
    except NotSentError:
        return show_error("Ödeme servisine ulaşılamıyor. Lütfen bir dakika sonra tekrar deneyin.")
    except OutcomeUnknownError:
        order.mark_needs_check()
        return show_error("Ödeme isteğini doğrulayamadık. Kontrol edip size haber vereceğiz.")
    except GatewayError as exc:
        log.warning("Epoint %s isteğini reddetti: %s", order.attempt_id, exc)
        return show_error("Ödeme başlatılamadı.")
    order.epoint_transaction = checkout.transaction
    order.save()
    return redirect(checkout.redirect_url)
```

## Mesajları değiştirmek

Tüm mesajlar paketin içindeki bir YAML dosyasından gelir ve değiştirilebilir veya çevrilebilir. Bkz. [Mesajlar](messages.md).
