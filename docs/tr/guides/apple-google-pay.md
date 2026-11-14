# Apple Pay ve Google Pay

Apple Pay ve Google Pay yönlendirmeyle değil, kendi sayfanıza gömdüğünüz bir widget ile çalışır. Müşteri düğmeye dokunur, Face ID, parmak izi veya PIN ile onaylar ve sitenizde kalır. Bu token ödemelerini Epoint her üye işyeri için ayrıca açar.

## Nasıl çalışır

1. Sunucunuz `ep.widgets.create()` ile bir widget oluşturur. Epoint bir `widget_url` döndürür.
2. Sayfanız `widget_url` adresini bir `iframe` içinde gösterir.
3. Müşteri ödemeyi tamamladığında widget sayfanıza bir `postMessage` gönderir.
4. Sayfanız bunu sunucuya bildirir, sunucu da ödemeyi `payments.status()` ile doğrular veya imzalı callback'i bekler.

Üçüncü adımdaki `postMessage` yalnızca bir ipucudur. Tarayıcıdaki veri değiştirilebilir, bu yüzden sonucu dördüncü adımda sunucu doğrulamalıdır.

## 1. adım. Widget'ı oluşturun

```python
widget = ep.widgets.create("19.90", "ORDER-1043", "Pro plan")
order.epoint_transaction = widget.transaction
order.save()
```

Üç argümanın hepsi zorunludur: tutar, sipariş kimliği ve açıklama. Yanıt bir {py:class}`~epoint_sdk.Widget` olur:

| Alan | Anlamı |
| --- | --- |
| `widget_url` | `iframe` içinde açılacak adres |
| `transaction` | Epoint'in işlem kimliği |
| `origin` | `widget_url` adresinin şeması ve sunucusu, `postMessage` kontrolü için |
| `trace_id` | Epoint'in izleme kimliği |
| `raw` | Yanıtın tamamı |

## 2. adım. Widget'ı gömün

```html
<iframe src="{{ widget.widget_url }}" allow="payment" title="Apple Pay / Google Pay"
        style="width:100%;height:240px;border:0"></iframe>
```

`allow="payment"` niteliği zorunludur. Sayfanız ayrıca Epoint'ten gelen ödemelere izin veren bir `Permissions-Policy` başlığı göndermelidir:

```text
Permissions-Policy: payment=(self "https://epoint.az")
```

Örneğin Django'da bunu bir middleware'de veya doğrudan yanıt üzerinde ayarlayın:

```python
response["Permissions-Policy"] = 'payment=(self "https://epoint.az")'
```

## 3. adım. Mesajı dinleyin

```html
<script>
addEventListener("message", (event) => {
  if (event.origin !== "{{ widget.origin }}") return;
  fetch("{% url 'order-check' order.number %}", {
    method: "POST",
    headers: {"X-CSRFToken": "{{ csrf_token }}"},
  }).then(() => location.reload());
});
</script>
```

`event.origin` değerini her zaman `widget.origin` ile karşılaştırın. Başka bir kaynaktan gelen mesajlar yok sayılmalıdır.

Mesajı sunucuda okumak isterseniz, örneğin loglamak veya müşteriye erken bir bilgi göstermek için, onu `WidgetMessage.from_event` metoduna verin:

```python
from epoint_sdk import WidgetMessage

hint = WidgetMessage.from_event(json.loads(request.body))
hint.looks_paid   # widget "success" diyorsa True
```

{py:class}`~epoint_sdk.WidgetMessage` şu alanları okur: `status`, `order_id`, `transaction`, `amount`, `card_mask` ve `message`. Özelliğe bilerek `paid` yerine `looks_paid` adı verildi: bu, tarayıcıdan gelen doğrulanmamış bir veridir.

## 4. adım. Sunucuda doğrulayın

```python
def order_check(request, number):
    order = get_object_or_404(Order, number=number)
    tx = ep.payments.status(order.epoint_transaction)
    if tx.paid and tx.matches(order_id=order.number, amount=order.total):
        order.mark_paid(transaction=tx.transaction)
    return JsonResponse({"paid": order.is_paid})
```

İmzalı callback de gelir, bu yüzden bu view çalıştığında sipariş zaten ödenmiş olabilir. Handler'ı idempotent tutun.

## Widget'ta bölünmüş ödeme

```python
checkout = ep.widgets.split("100.00", "ORDER-5004", "i000000002", "85.00", description="Lamba")
```

Argümanlar `split.create()` ile aynıdır. SDK yanıtı bir `Redirect` olarak döndürür, Epoint'ten gelen JSON'un tamamı da `checkout.raw` alanındadır.

## Kaynağı kendiniz kontrol etmek

`origin_of(url)` herhangi bir URL'nin küçük harfli şemasını ve sunucusunu, bunlar yoksa `None` döndürür. `Widget.origin` da bunu kullanır:

```python
from epoint_sdk import origin_of

origin_of("https://epoint.az/widget/abc?x=1")   # "https://epoint.az"
```
