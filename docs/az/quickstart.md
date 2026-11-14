# Sürətli başlanğıc

Bu səhifədə bir ödənişin bütün yolu göstərilir: sorğu yaradılır, müştəri Epoint səhifəsinə göndərilir və nəticə serverinizdə təsdiqlənir. Paketin [quraşdırıldığı](installation.md) və [açarlarınızın](keys.md) hazır olduğu güman edilir.

## Ödəniş necə keçir

1. Serveriniz Epoint-dən ödəniş səhifəsi istəyir. Epoint `redirect_url` və `transaction` identifikatoru ilə cavab verir.
2. Müştərini `redirect_url` ünvanına yönləndirirsiniz. O, kart məlumatlarını Epoint səhifəsində daxil edir.
3. Epoint müştərini uğurlu və ya uğursuz ödəniş səhifənizə qaytarır.
4. Epoint nəticə ünvanınıza imzalı callback göndərir. Sifarişi ödənilmiş kimi qeyd etməyin vaxtı **məhz budur**.

3-cü addım yalnız müştəri üçündür. Uğurlu ödəniş səhifənizi hər kəs brauzerdə əllə aça bilər, ona görə də bu heç nəyi sübut etmir. 4-cü addım isə məxfi açarınızla imzalanır, imzası yoxlanandan sonra ona etibar etmək olar.

## 1-ci addım. Klienti yaradın

```python
from epoint_sdk import Epoint

ep = Epoint(
    "i000000001",
    "PRIVATE_KEY",
    success_url="https://shop.az/payment/ok",
    error_url="https://shop.az/payment/fail",
)
```

- İlk iki arqument açıq və məxfi açarınızdır.
- `success_url` və `error_url` bütün ödənişlər üçün standart dəyər olur. Lazım olanda hər sorğuda onları dəyişmək olar.
- Ödəniş səhifəsinin dili standart olaraq `az`, valyuta isə `AZN` olur.

Klienti tətbiq işə düşəndə bir dəfə yaradın və təkrar istifadə edin. O, HTTP bağlantı hovuzunu açıq saxlayır. Tətbiq dayananda `ep.close()` çağırın, qısa skriptlərdə isə `with` blokundan istifadə edin.

## 2-ci addım. Ödənişi yaradın

```python
checkout = ep.payments.create(
    "19.90",
    "ORDER-1042",
    description="Pro plan, 1 ay",
)
```

Sətir-sətir:

- `"19.90"` məbləğdir. Yuvarlaqlaşdırma sürprizləri olmasın deyə float yox, sətir və ya `Decimal` ötürün. İkidən çox onluq rəqəm, sıfır, mənfi ədəd, `NaN` və bool dəyərlər sorğu göndərilməzdən əvvəl `InvalidRequestError` ilə rədd edilir.
- `"ORDER-1042"` sifarişinizin identifikatorudur. Hər ödəniş üçün unikal olmalıdır. Epoint artıq gördüyü identifikatoru qəbul etmir və sizi ikiqat ödənişdən qoruyan da məhz budur.
- `description` ödəniş səhifəsində müştəriyə göstərilir.

Nəticə `Redirect` obyektidir:

```python
>>> checkout
Redirect(redirect_url='https://epoint.az/...', transaction='te001...', trace_id=None, message=None)
```

`checkout.transaction` dəyərini sifarişin yanında saxlayın. Vəziyyəti yoxlamaq və ya sonradan pulu qaytarmaq üçün o lazım olacaq.

## 3-cü addım. Müştərini Epoint səhifəsinə göndərin

Yönləndirmə freymvorkunuzdan asılıdır. Django-da belədir:

```python
from django.shortcuts import redirect

return redirect(checkout.redirect_url)
```

## 4-cü addım. Ödənişi callback-də təsdiqləyin

Epoint nəticə ünvanınıza iki forma sahəsi göndərir: `data` və `signature`. Formanı bütövlükdə `verify_callback` metoduna verin:

```python
from epoint_sdk import SignatureError

def epoint_callback(request):
    try:
        tx = ep.verify_callback(request.POST)
    except SignatureError:
        return HttpResponseBadRequest()

    order = Order.objects.get(number=tx.order_id)
    if tx.paid and tx.matches(order_id=order.number, amount=order.total):
        order.mark_paid(transaction=tx.transaction)
    return HttpResponse("OK")
```

- `verify_callback` imzanı sabit vaxtda yoxlayır və yalnız bundan sonra məlumatı açır. Saxta və ya zədələnmiş callback `SignatureError` qaldırır.
- `tx.paid` yalnız status `success` olanda `True` olur.
- `tx.matches(...)` callback-in gözlədiyiniz sifariş və məbləğ barədə olduğunu yoxlayır. Başqa, daha ucuz sifariş üçün gələn etibarlı callback bu sifarişi açmamalıdır.

Bu view-un real işə hazır tam versiyası [Django nümunəsindədir](examples/django.md).

## 5-ci addım. Şübhə olanda Epoint-dən soruşun

Callback heç gəlməsə, vəziyyəti birbaşa soruşun:

```python
tx = ep.payments.status(checkout.transaction)
print(tx.status, tx.paid, tx.pending)
```

Kart rədd ediləndə `status()` xəta qaldırmır. O, `failed` xassəsi `True` olan `Transaction` qaytarır.

## 6-cı addım. Klienti bağlayın

```python
ep.close()
```

və ya klienti kontekst meneceri kimi işlədin:

```python
with Epoint() as ep:
    ...
```

## Bundan sonra

- [Konfiqurasiya](configuration.md) bütün ayarları və açarların mühit dəyişənlərindən və ya fayldan necə oxunduğunu göstərir.
- [Ödənişlər](guides/payments.md) `create` metodunun digər seçimlərini, imzalı HTML formanı və taksiti izah edir.
- [Callback-lər](guides/callbacks.md) nəticənin hər sahəsini izah edir.
- [Xətalar](guides/errors.md) və [Etibarlılıq](guides/reliability.md) şəbəkə nasaz olanda nə etmək lazım olduğunu göstərir.
