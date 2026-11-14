# Kayıtlı kartlar

Kartı kaydetmek, müşteriyi tekrar ödeme sayfasına göndermeden kartından çekim yapmanızı sağlar. Abonelikler, tek tıkla ödeme ve bakiye yükleme bunun üzerine kurulur. Kartın kendisi Epoint'te kalır, siz yalnızca bir `card_id` saklarsınız.

## Kartı ödeme olmadan kaydetmek

```python
reg = ep.cards.register(description="Sonraki ödemeler için kartınızı kaydedin")
user.pending_card_id = reg.card_id
redirect(reg.redirect_url)
```

`register()` yalnızca anahtar kelimeli argüman alır:

| Argüman | Varsayılan | Anlamı |
| --- | --- | --- |
| `payouts` | `False` | `True` olduğunda kart payout için kaydedilir ve daha sonra karta para gönderilebilir |
| `description` | yok | Epoint sayfasındaki metin |
| `language` | ayardan | Sayfa dili |
| `success_url` | ayardan | Başarılı sonuçtan sonra müşterinin döndüğü adres |
| `error_url` | ayardan | Başarısız sonuçtan sonra müşterinin döndüğü adres |

`card_id`, `redirect_url`, `transaction`, `trace_id` ve `raw` alanlarına sahip bir {py:class}`~epoint_sdk.CardRegistration` döndürür. `card_id` hemen bilinir ama kart ancak müşteri sayfadaki adımları tamamladıktan sonra kullanılabilir.

## Kartı ilk ödemeyle birlikte kaydetmek

Çoğu mağaza kartı müşteri ilk kez öderken kaydeder:

```python
reg = ep.cards.register_and_pay("9.90", "SUB-1001-1", description="Aylık plan")
redirect(reg.redirect_url)
```

`installment` ve `other_attr` dışında `payments.create()` ile aynı argümanları alır ve bir `CardRegistration` döndürür.

## Kartı kontrol etmek

```python
card = ep.cards.status(card_id)
if card.usable:
    user.save_card(card.id, card.mask, card.expiry)
```

{py:class}`~epoint_sdk.Card` sınıfının alanları:

| Alan | Anlamı |
| --- | --- |
| `id` | Kart kimliği |
| `status` | Bir {py:class}`~epoint_sdk.CardStatus` değeri: `new`, `active`, `pending`, `rejected`, `expired`, `session_expired` veya `unknown` |
| `usable` | Yalnızca durum `active` olduğunda `True` |
| `name` | Epoint gönderdiyse kartın adı |
| `mask` | Maskelenmiş numara |
| `expiry` | Epoint'in gönderdiği biçimde son kullanma tarihi |
| `description` | Verdiğiniz açıklama |

Yeni kartı callback'ten de öğrenebilirsiniz: `operation_code` değeri `001` veya `200` olur, `card_id` ve `card_mask` alanları doludur. Bkz. [Callback'ler](callbacks.md#islem-kodlari).

## Kayıtlı karttan çekim yapmak

```python
tx = ep.cards.charge(user.card_id, "9.90", "SUB-1001-2", description="Aylık plan, mart")
if tx.paid:
    extend_subscription(user)
elif tx.failed:
    notify_card_declined(user, tx.message)
```

Argümanlar sırasıyla `card_id`, tutar ve `order_id`'dir. Bunlara ek olarak `description`, `language` ve `currency` anahtar kelimeli argümanları vardır.

Çekim hemen yapılır ve yanıt bir `Transaction` olur. Kartın reddedilmesi hata **fırlatmaz**: `failed` özelliği `True` olan ve bankanın `code` ile `message` değerlerini taşıyan bir işlem alırsınız. Yalnızca isteğin kendisi reddedilirse, örneğin kart kimliği bilinmiyorsa, `GatewayError` fırlatılır.

Kayıtlı karttan çekim para hareketi yaratır, bu yüzden sonucu belirsiz bir hatadan sonra asla tekrarlanmaz. Her fatura dönemi için yeni bir `order_id` kullanın ve aynı kimliği yalnızca aynı dönemi tekrar denediğinizde kullanın.

## Karta ödeme

Karta ödeme (payout) parayı karta **gönderir**: nakit iade (cashback), ödüller veya bir pazaryerinde satıcı kazançları için. Kartın `payouts=True` ile kaydedilmiş olması gerekir:

```python
reg = ep.cards.register(payouts=True, description="Para çekme kartı")
```

Ardından:

```python
tx = ep.cards.payout(seller.payout_card_id, "120.00", "PAYOUT-5531", description="Kazanç, 12. hafta")
```

Karta ödeme üye işyeri hesabınızın ayrı bir özelliğidir. Açık değilse Epoint isteği reddeder ve SDK `GatewayError` fırlatır.

## Kartları sorumlu şekilde saklamak

- `card_id`, maskelenmiş numara ve son kullanma tarihini saklayın. Tam kart numarasını asla saklamaya çalışmayın, zaten onu hiç görmezsiniz.
- Kullanıcıların kayıtlı kartı hesap sayfalarından silmesine izin verin ve silinen karttan hemen çekim yapmayı bırakın.
- `**** 1111` gibi maskelenmiş numarayı gösterin ki kullanıcı hangi kartından çekim yapılacağını bilsin.

Aylık faturalandırma görevinin tamamı [abonelik örneğinde](../examples/subscriptions.md).
