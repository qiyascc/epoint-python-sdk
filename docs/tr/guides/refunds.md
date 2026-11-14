# İadeler ve iptaller

Epoint'te parayı geri vermenin iki yolu vardır ve ikisi aynı şey değildir:

- **İptal (reversal)** mevcut bir ödemeyi tamamen veya kısmen geri alır. Para, ödemenin yapıldığı karta döner.
- **Karta ödeme (payout)** parayı payout için kaydedilmiş bir karta gönderir. Önceki bir ödemeye bağlı değildir. Bkz. [Kayıtlı kartlar](saved-cards.md#karta-ödeme).

"Müşteri parasını geri istiyor" gibi olağan bir durumda iptali kullanın.

## Tam iptal

```python
result = ep.payments.reverse("te001234")
if result.ok:
    order.mark_refunded()
```

Ödemeyi oluştururken sakladığınız `transaction` kimliğini verin.

## Kısmi iptal

Tutarı ikinci argüman olarak verin:

```python
result = ep.payments.reverse("te001234", "5.00")
```

Tutar, ödemelerdeki kurallara tabidir: sıfırdan büyük, en fazla iki ondalık basamak.

```{note}
Tutar ikinci konumsal argümandır. Parametrenin adı `amount_` olduğu için `reverse(transaction, amount="5.00")` değil, `reverse(transaction, "5.00")` yazın.
```

`currency` ve `language` anahtar kelimeli argüman olarak verilebilir ve varsayılan olarak ayarlarınızdan alınır.

## Sonuç

`reverse()` bir {py:class}`~epoint_sdk.Result` döndürür:

| Alan | Anlamı |
| --- | --- |
| `status` | Bir `Status` değeri |
| `ok` | Durum `success` olduğunda `True` |
| `transaction` | Yanıttaki işlem kimliği |
| `message` | Ödeme altyapısından gelen mesaj |
| `trace_id` | Epoint'in izleme kimliği |
| `raw` | Yanıtın tamamı |

Epoint iptali doğrudan reddederse, örneğin ödeme zaten iade edilmişse, SDK Epoint'in `code` değeri ve mesajıyla bir `GatewayError` fırlatır:

```python
from epoint_sdk import GatewayError

try:
    ep.payments.reverse("te001234")
except GatewayError as exc:
    log.warning("İade reddedildi: %s", exc)
```

Başarılı bir tam iptalden sonra `payments.status(transaction)` ödemeyi `returned` durumuyla gösterir.

## İptal iki kez gönderilmez

İptal para hareketi yaratır, bu yüzden SDK ona bir ödeme gibi davranır: istek gönderildikten sonra zaman aşımı olur veya bağlantı koparsa istek **tekrarlanmaz**. Bunun yerine `OutcomeUnknownError` alırsınız. Yeniden denemeden önce ödemenin durumunu kontrol edin:

```python
from epoint_sdk import OutcomeUnknownError

try:
    ep.payments.reverse(tx_id, "5.00")
except OutcomeUnknownError:
    tx = ep.payments.status(tx_id)
    if tx.returned:
        ...
```

Kuralların tamamı [Güvenilirlik](reliability.md) sayfasında.

## İadeleri kayıt altına almak

Siparişlerin yanında bir iade tablosu tutun: tutar, zaman, kimin istediği ve aldığınız `Result`. Kısmi iadeler birikir ve müşteri ne olduğunu sorduğunda bu geçmişe ihtiyacınız olur.

İade akışının tamamı [mutabakat örneğinde](../examples/reconciliation.md).
