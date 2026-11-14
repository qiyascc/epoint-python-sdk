# Təhlükəsizlik

Ödəniş inteqrasiyalarına hücumlar adətən bir neçə məlum nöqtəyə yönəlir. Bu səhifədə həmin yerlər sadalanır, SDK-nın hər biri üçün nə etdiyi və sizin üzərinizə nə qaldığı göstərilir.

## 1. Yalnız imzalı callback-ə etibar edin

`success_url` səhifənizə yönləndirmə heç nəyi sübut etmir. Bu ünvanı hər kəs brauzerə yaza bilər. Sifarişi yalnız bunlardan biri baş verəndən sonra ödənilmiş kimi qeyd edin:

- `verify_callback` yoxlamasından keçmiş callback və ya
- serverinizin etdiyi `payments.status()` çağırışı.

## 2. Callback-in məhz bu sifarişə aid olduğunu yoxlayın

Etibarlı imza callback-i Epoint-in göndərdiyini göstərir, onun açmaq istədiyiniz sifarişə aid olduğunu isə yox. Təcavüzkar ucuz sifariş üçün 1 AZN ödəyib həmin callback-i baha sifariş üçün təkrar göndərməyə cəhd edə bilər. Callback-i qeydlərinizlə müqayisə edin:

```python
if tx.paid and tx.matches(order_id=order.number, amount=order.total, transaction=order.epoint_transaction):
    order.mark_paid()
```

## 3. Məxfi açarı serverdə saxlayın

- Onu heç vaxt brauzerə və ya mobil tətbiqə göndərməyin. İmzalama yalnız serverdə aparılır.
- Onu repozitoriyadan və loqlardan kənarda saxlayın. SDK açarı `SecretStr` kimi saxlayır, ona görə ayarlar çap ediləndə `**********` görünür, `repr(ep)` isə yalnız açıq açarı göstərir.
- Açarı mühit dəyişənindən və ya sirr meneceri xidmətindən yükləyin.
- Açarın sızdığından şübhələnirsinizsə, dərhal Epoint-dən yeni açar cütü istəyin.

## 4. Yalnız https

İmzalı sorğular adi `http` ilə göndərilmir. İstisna localhost və daxili sandbox üçün açıq şəkildə təyin etdiyiniz `allow_insecure_http` ayarıdır. Bu ayarı real mühitdə heç vaxt aktiv etməyin.

## 5. Göndərməzdən əvvəl yoxlayın

Məbləğlər serverinizdən hər hansı sorğu çıxmazdan əvvəl yoxlanılır: gizli yuvarlaqlaşdırmalı float, `NaN`, mənfi dəyər və `1` kimi görünən bool keçmir. Sifariş identifikatorlarının və mətnlərin uzunluq həddi var. Bu xətalar müştəriyə yox, proqramçıya görünməlidir.

## 6. Callback ünvanını sui-istifadədən qoruyun

- SDK 64 KB-dan böyük callback məlumatını və 128 simvoldan uzun imzanı hash hesablamadan rədd edir.
- İmzalar `hmac.compare_digest` ilə müqayisə olunur, ona görə cavab vaxtı təcavüzkara heç nə demir.
- Etibarsız callback-lərə HTTP 400 ilə cavab verin və başqa heç bir iş görməyin.
- Ünvan internetə açıqdırsa, proksi səviyyəsində sorğu sayını məhdudlaşdırın.

## 7. Brauzer mesajlarına işarə kimi baxın

Apple Pay və Google Pay vidjeti nəticəni `postMessage` ilə bildirir. `event.origin` dəyərini `widget.origin` ilə yoxlayın, hətta bundan sonra da mesajı yalnız öz serverinizdən ödənişi yoxlamasını istəmək üçün işlədin. `WidgetMessage.looks_paid` adı bunu xatırlatmaq üçün belə seçilib.

## 8. Pulu heç vaxt iki dəfə çıxmayın

Pul hərəkət etdirən çağırışlar nəticəsi bəlli olmayan xətadan sonra təkrarlanmır. Öz kodunuzda da belə saxlayın: `OutcomeUnknownError` alanda əvvəlcə yoxlayın və yalnız eyni sifariş identifikatoru ilə təkrarlayın. Bax: [Etibarlılıq](reliability.md).

## 9. Ehtiyatla loq yazın

`order_id`, `transaction`, `trace_id`, status və məbləğləri loqa yazın. Məxfi açarı, real mühitdə callback-lərin bütöv gövdəsini və müştərinin daxil etdiyi heç bir məlumatı loqa yazmayın. Epoint dəstəyi sizdən məhz `trace_id` dəyərini istəyəcək.

## İşə buraxmazdan əvvəl yoxlama siyahısı

- [ ] `base_url` `https://epoint.az` ünvanıdır və `allow_insecure_http` təyin olunmayıb.
- [ ] Məxfi açar mühit dəyişənindən və ya sirr meneceri xidmətindən gəlir.
- [ ] Callback view-u imzanı yoxlayır və `matches()` çağırır.
- [ ] Sifarişlər yalnız callback-də və ya `payments.status()` çağırışından sonra ödənilmiş kimi qeyd olunur.
- [ ] Callback handler-i idempotentdir.
- [ ] `OutcomeUnknownError` yeni sifariş identifikatoruna yox, vəziyyətin yoxlanmasına aparır.
- [ ] Uzun müddət gözləmədə qalan sifarişləri yoxlayan dövri tapşırıq var.
- [ ] Vidjet olan səhifə `Permissions-Policy: payment=(self "https://epoint.az")` başlığını göndərir.
