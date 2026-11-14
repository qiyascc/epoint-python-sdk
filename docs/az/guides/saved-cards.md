# Yadda saxlanmış kartlar

Kartı yadda saxlamaq müştərini yenidən ödəniş səhifəsinə göndərmədən onun kartından pul çıxmağa imkan verir. Abunəliklər, bir kliklə ödəniş və balans artırma məhz bunun üzərində qurulur. Kartın özü Epoint-də qalır, siz yalnız `card_id` saxlayırsınız.

## Kartı ödənişsiz yadda saxlamaq

```python
reg = ep.cards.register(description="Növbəti ödənişlər üçün kartınızı yadda saxlayın")
user.pending_card_id = reg.card_id
redirect(reg.redirect_url)
```

`register()` yalnız açar sözlü arqumentlər qəbul edir:

| Arqument | Standart dəyər | Mənası |
| --- | --- | --- |
| `payouts` | `False` | `True` olanda kart payout üçün qeydiyyata alınır və sonra ona pul göndərmək olur |
| `description` | yoxdur | Epoint səhifəsindəki mətn |
| `language` | ayardan | Səhifənin dili |
| `success_url` | ayardan | Uğurlu nəticədən sonra müştərinin qayıtdığı ünvan |
| `error_url` | ayardan | Uğursuz nəticədən sonra müştərinin qayıtdığı ünvan |

Metod `card_id`, `redirect_url`, `transaction`, `trace_id` və `raw` sahələri olan {py:class}`~epoint_sdk.CardRegistration` qaytarır. `card_id` dərhal məlum olur, amma kartı yalnız müştəri səhifədəki addımları bitirəndən sonra istifadə etmək olar.

## Kartı ilk ödənişlə birlikdə yadda saxlamaq

Mağazaların çoxu kartı müştəri ilk dəfə ödəyəndə yadda saxlayır:

```python
reg = ep.cards.register_and_pay("9.90", "SUB-1001-1", description="Aylıq plan")
redirect(reg.redirect_url)
```

Metod `installment` və `other_attr` istisna olmaqla `payments.create()` ilə eyni arqumentləri qəbul edir və `CardRegistration` qaytarır.

## Kartı yoxlamaq

```python
card = ep.cards.status(card_id)
if card.usable:
    user.save_card(card.id, card.mask, card.expiry)
```

{py:class}`~epoint_sdk.Card` sinfinin sahələri:

| Sahə | Mənası |
| --- | --- |
| `id` | Kartın identifikatoru |
| `status` | {py:class}`~epoint_sdk.CardStatus` dəyəri: `new`, `active`, `pending`, `rejected`, `expired`, `session_expired` və ya `unknown` |
| `usable` | Yalnız status `active` olanda `True` |
| `name` | Kartın adı, Epoint göndəribsə |
| `mask` | Gizlədilmiş nömrə |
| `expiry` | Epoint-in göndərdiyi şəkildə bitmə tarixi |
| `description` | Verdiyiniz təsvir |

Yeni kart barədə callback-dən də xəbər tuta bilərsiniz: onun `operation_code` dəyəri `001` və ya `200` olur, `card_id` və `card_mask` sahələri isə doldurulur. Bax: [Callback-lər](callbacks.md#əməliyyat-kodları).

## Yadda saxlanmış kartdan pul çıxmaq

```python
tx = ep.cards.charge(user.card_id, "9.90", "SUB-1001-2", description="Aylıq plan, mart")
if tx.paid:
    extend_subscription(user)
elif tx.failed:
    notify_card_declined(user, tx.message)
```

Arqumentlər bu ardıcıllıqla verilir: `card_id`, məbləğ və `order_id`. Bunlardan əlavə `description`, `language` və `currency` açar sözlü arqumentləri var.

Pul dərhal çıxılır və cavab `Transaction` olur. Kartın rədd edilməsi xəta **qaldırmır**: `failed` xassəsi `True` olan, bankın `code` və `message` dəyərlərini daşıyan tranzaksiya alırsınız. Yalnız sorğunun özü rədd edilərsə, məsələn kart identifikatoru naməlumdursa, `GatewayError` qaldırılır.

Yadda saxlanmış kartdan pul çıxmaq pul hərəkət etdirir, ona görə nəticəsi bəlli olmayan xətadan sonra heç vaxt təkrarlanmır. Hər ödəniş dövrü üçün yeni `order_id` işlədin, eyni identifikatoru yalnız həmin dövrü təkrarlayanda istifadə edin.

## Karta ödəniş

Karta ödəniş (payout) pulu karta **göndərir**: keşbek, uduş və ya marketpleysdə satıcının qazancı üçün. Kart `payouts=True` ilə qeydiyyata alınmış olmalıdır:

```python
reg = ep.cards.register(payouts=True, description="Pul çıxarmaq üçün kart")
```

Sonra:

```python
tx = ep.cards.payout(seller.payout_card_id, "120.00", "PAYOUT-5531", description="Qazanc, 12-ci həftə")
```

Karta ödəniş tacir hesabınızın ayrıca imkanıdır. Aktiv deyilsə, Epoint sorğunu rədd edir və SDK `GatewayError` qaldırır.

## Kartları məsuliyyətlə saxlamaq

- `card_id`, gizlədilmiş nömrəni və bitmə tarixini saxlayın. Tam kart nömrəsini heç vaxt saxlamağa çalışmayın, onsuz da onu görmürsünüz.
- İstifadəçiyə yadda saxlanmış kartı hesab səhifəsindən silməyə imkan verin və silinən kartdan dərhal pul çıxmağı dayandırın.
- `**** 1111` kimi gizlədilmiş nömrəni göstərin ki, istifadəçi hansı kartdan pul çıxılacağını bilsin.

Tam aylıq ödəniş tapşırığı [abunəlik nümunəsindədir](../examples/subscriptions.md).
