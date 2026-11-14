# Geri qaytarma və ləğv

Epoint-də pulu geri qaytarmağın iki yolu var və onlar eyni şey deyil:

- **Ləğv (reversal)** mövcud ödənişi tam və ya qismən ləğv edir. Pul ödənişin edildiyi karta qayıdır.
- **Karta ödəniş (payout)** pulu payout üçün qeydiyyatdan keçmiş yadda saxlanmış karta göndərir. Əvvəlki ödənişlə bağlı deyil. Bax: [Yadda saxlanmış kartlar](saved-cards.md#karta-ödəniş).

"Müştəri pulunu geri istəyir" kimi adi hal üçün ləğvdən istifadə edin.

## Tam ləğv

```python
result = ep.payments.reverse("te001234")
if result.ok:
    order.mark_refunded()
```

Ödəniş yaradılanda saxladığınız `transaction` identifikatorunu verin.

## Qismən ləğv

Məbləği ikinci arqument kimi verin:

```python
result = ep.payments.reverse("te001234", "5.00")
```

Məbləğ ödənişlərdəki qaydalara tabedir: sıfırdan böyük, ən çox iki onluq rəqəm.

```{note}
Məbləğ ikinci mövqe arqumentidir. Parametrin adı `amount_` olduğuna görə `reverse(transaction, amount="5.00")` yox, `reverse(transaction, "5.00")` yazın.
```

`currency` və `language` açar sözlü arqument kimi verilə bilər, standart olaraq ayarlarınızdan götürülür.

## Nəticə

`reverse()` {py:class}`~epoint_sdk.Result` qaytarır:

| Sahə | Mənası |
| --- | --- |
| `status` | `Status` dəyəri |
| `ok` | Status `success` olanda `True` |
| `transaction` | Cavabdakı tranzaksiya identifikatoru |
| `message` | Ödəniş sistemindən gələn mesaj |
| `trace_id` | Epoint-in izləmə identifikatoru |
| `raw` | Bütöv JSON cavabı |

Epoint ləğvi birbaşa rədd edərsə, məsələn ödəniş artıq qaytarılıbsa, SDK Epoint-in `code` dəyəri və mesajı ilə `GatewayError` qaldırır:

```python
from epoint_sdk import GatewayError

try:
    ep.payments.reverse("te001234")
except GatewayError as exc:
    log.warning("Geri qaytarma rədd edildi: %s", exc)
```

Uğurlu tam ləğvdən sonra `payments.status(transaction)` ödənişi `returned` statusu ilə göstərir.

## Ləğv iki dəfə göndərilmir

Ləğv pul hərəkət etdirir, ona görə SDK ona ödənişə yanaşdığı kimi yanaşır: sorğu göndəriləndən sonra gözləmə müddəti bitərsə və ya bağlantı qırılarsa, sorğu **təkrarlanmır**. Əvəzində `OutcomeUnknownError` alırsınız. Yenidən cəhd etməzdən əvvəl ödənişin vəziyyətini yoxlayın:

```python
from epoint_sdk import OutcomeUnknownError

try:
    ep.payments.reverse(tx_id, "5.00")
except OutcomeUnknownError:
    tx = ep.payments.status(tx_id)
    if tx.returned:
        ...
```

Bütün qaydalar [Etibarlılıq](reliability.md) səhifəsindədir.

## Geri qaytarmaları qeyd etmək

Sifarişlərin yanında geri qaytarmalar cədvəli saxlayın: məbləğ, vaxt, kimin istədiyi və aldığınız `Result`. Qismən qaytarmalar cəmlənir və müştəri nə baş verdiyini soruşanda bu tarixçə lazım olur.

Tam geri qaytarma axını [üzləşmə nümunəsinin](../examples/reconciliation.md) bir hissəsidir.
