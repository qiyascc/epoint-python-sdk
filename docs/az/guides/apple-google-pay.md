# Apple Pay və Google Pay

Apple Pay və Google Pay yönləndirmə ilə yox, öz səhifənizə yerləşdirdiyiniz vidjet vasitəsilə işləyir. Müştəri düyməyə toxunur, Face ID, barmaq izi və ya PIN ilə təsdiqləyir və saytınızda qalır. Bu token ödənişlərini Epoint hər tacir üçün ayrıca aktivləşdirir.

## Necə işləyir

1. Serveriniz `ep.widgets.create()` ilə vidjet yaradır. Epoint `widget_url` qaytarır.
2. Səhifəniz `widget_url` ünvanını `iframe` daxilində göstərir.
3. Müştəri ödənişi bitirəndə vidjet səhifənizə `postMessage` göndərir.
4. Səhifəniz bunu serverə bildirir, server isə ödənişi `payments.status()` ilə təsdiqləyir və ya imzalı callback-i gözləyir.

3-cü addımdakı `postMessage` yalnız işarədir. Brauzerdəki məlumatı dəyişmək mümkündür, ona görə nəticəni 4-cü addımda server təsdiqləməlidir.

## 1-ci addım. Vidjeti yaradın

```python
widget = ep.widgets.create("19.90", "ORDER-1043", "Pro plan")
order.epoint_transaction = widget.transaction
order.save()
```

Üç arqumentin hamısı mütləqdir: məbləğ, sifariş identifikatoru və təsvir. Cavab {py:class}`~epoint_sdk.Widget` olur:

| Sahə | Mənası |
| --- | --- |
| `widget_url` | `iframe` daxilində açılacaq ünvan |
| `transaction` | Epoint-in tranzaksiya identifikatoru |
| `origin` | `widget_url` ünvanının sxemi və hostu, `postMessage` yoxlaması üçün |
| `trace_id` | Epoint-in izləmə identifikatoru |
| `raw` | Bütöv cavab |

## 2-ci addım. Vidjeti yerləşdirin

```html
<iframe src="{{ widget.widget_url }}" allow="payment" title="Apple Pay / Google Pay"
        style="width:100%;height:240px;border:0"></iframe>
```

`allow="payment"` atributu mütləqdir. Səhifəniz həmçinin Epoint-dən ödənişlərə icazə verən `Permissions-Policy` başlığı göndərməlidir:

```text
Permissions-Policy: payment=(self "https://epoint.az")
```

Məsələn, Django-da bunu middleware-də və ya cavabın özündə təyin edin:

```python
response["Permissions-Policy"] = 'payment=(self "https://epoint.az")'
```

## 3-cü addım. Mesajı dinləyin

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

`event.origin` dəyərini həmişə `widget.origin` ilə müqayisə edin. Başqa mənbədən gələn mesajlar nəzərə alınmamalıdır.

Mesajı serverdə oxumaq istəyirsinizsə, məsələn loqa yazmaq və ya müştəriyə ilkin bildiriş göstərmək üçün, onu `WidgetMessage.from_event` metoduna verin:

```python
from epoint_sdk import WidgetMessage

hint = WidgetMessage.from_event(json.loads(request.body))
hint.looks_paid   # vidjet "success" deyirsə True
```

{py:class}`~epoint_sdk.WidgetMessage` `status`, `order_id`, `transaction`, `amount`, `card_mask` və `message` sahələrini oxuyur. Xassənin adı qəsdən `paid` yox, `looks_paid` qoyulub: bu, brauzerdən gələn yoxlanılmamış məlumatdır.

## 4-cü addım. Serverdə təsdiqləyin

```python
def order_check(request, number):
    order = get_object_or_404(Order, number=number)
    tx = ep.payments.status(order.epoint_transaction)
    if tx.paid and tx.matches(order_id=order.number, amount=order.total):
        order.mark_paid(transaction=tx.transaction)
    return JsonResponse({"paid": order.is_paid})
```

İmzalı callback də gəlir, ona görə bu view işə düşənə qədər sifariş artıq ödənilmiş ola bilər. Handler-i idempotent saxlayın.

## Vidjetdə bölünmüş ödəniş

```python
checkout = ep.widgets.split("100.00", "ORDER-5004", "i000000002", "85.00", description="Çıraq")
```

Arqumentlər `split.create()` ilə eynidir. SDK cavabı `Redirect` kimi qaytarır, Epoint-dən gələn bütöv JSON isə `checkout.raw` sahəsindədir.

## Mənbəni özünüz yoxlamaq

`origin_of(url)` istənilən URL-in kiçik hərflərlə sxemini və hostunu, bunlar yoxdursa `None` qaytarır. `Widget.origin` da ondan istifadə edir:

```python
from epoint_sdk import origin_of

origin_of("https://epoint.az/widget/abc?x=1")   # "https://epoint.az"
```
