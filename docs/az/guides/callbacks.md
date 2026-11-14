# Callback-lər

Callback Epoint-in serverinizə ödənişin nəticəsini bildirdiyi sorğudur. Ödəniş axınında etibar edə biləcəyiniz yeganə hissə odur, çünki məxfi açarınızla imzalanır. Bu səhifədə callback-i necə qəbul etmək, yoxlamaq və ona əsasən hərəkət etmək göstərilir.

## Epoint nə göndərir

Epoint tacir hesabınızda qeyd olunmuş nəticə ünvanına `POST` sorğusu göndərir. Sorğunun gövdəsi iki sahəli formadır:

`data`
: Nəticə JSON şəklində, base64 ilə kodlanmış.

`signature`
: Məxfi açarınızla hesablanmış `base64(sha1(private_key + data + private_key))`.

Məxfi açar yalnız sizə və Epoint-ə məlum olduğuna görə uyğun gələn imza bu `data` dəyərini məhz Epoint-in hazırladığını sübut edir.

## Callback-i yoxlamaq

Formanı bütövlükdə `verify_callback` metoduna verin:

```python
from epoint_sdk import SignatureError

try:
    tx = ep.verify_callback(request.POST)
except SignatureError:
    return bad_request()
```

Metod istənilən mapping obyekti ilə işləyir: Django-nun `request.POST`, Flask-ın `request.form`, Starlette və FastAPI-də `await request.form()` nəticəsi və ya adi `dict`. Sahə siyahı şəklində gəlsə, onun birinci dəyəri götürülür.

İki dəyər artıq ayrı-ayrılıqda əlinizdədirsə, onları iki arqument kimi verin:

```python
tx = ep.verify_callback(data, signature)
```

Klient olmadan, məsələn kiçik bir worker prosesində, modul səviyyəsindəki funksiyanı məxfi açarla çağırın:

```python
from epoint_sdk import verify_callback

tx = verify_callback(PRIVATE_KEY, request.POST)
```

### Nə yoxlanılır və hansı ardıcıllıqla

1. `data` və `signature` sahələrinin hər ikisi var və boş deyil.
2. `data` ən çox 64 KB, `signature` isə ən çox 128 simvoldur. Bundan böyük dəyərlər hash hesablanmazdan əvvəl rədd edilir.
3. İmza uyğun gəlir. Müqayisə sabit vaxtda aparılır.
4. `data` düzgün base64-dür və JSON obyektinə açılır.

Hər hansı yoxlama uğursuz olarsa, `SignatureError` qaldırılır və callback-in heç bir sahəsi oxunmur. Belə sorğuya HTTP 400 ilə cavab verin və başqa heç nə etməyin.

## Nəticəni oxumaq

`verify_callback` {py:class}`~epoint_sdk.Transaction` qaytarır. `payments.status()` da eyni tipi qaytarır. `Callback` bu sinfin digər adıdır.

| Sahə | Mənası |
| --- | --- |
| `status` | {py:class}`~epoint_sdk.Status` dəyəri: `new`, `success`, `failed`, `error`, `returned`, `server_error` və ya `unknown` |
| `transaction` | Epoint-in tranzaksiya identifikatoru |
| `order_id` | Sizin sifariş identifikatorunuz |
| `amount` | `Decimal` şəklində məbləğ və ya `None` |
| `code` | Bankın cavab kodu, Epoint göndəribsə |
| `message` | Epoint-dən və ya bankdan gələn oxunaqlı mesaj |
| `bank_transaction` | Bankın tranzaksiya identifikatoru |
| `bank_response` | Bankın xam cavabı |
| `operation_code` | Nəticənin hansı əməliyyata aid olduğu, aşağıya baxın |
| `rrn` | Kart şəbəkəsinin istinad nömrəsi (RRN) |
| `card_id` | Kart qeydiyyatı axınlarında yadda saxlanmış kartın identifikatoru |
| `card_name` | Kart sahibinin adı, Epoint göndəribsə |
| `card_mask` | `411111******1111` kimi gizlədilmiş kart nömrəsi |
| `split_amount` | Bölünmüş ödənişdə tərəfdaşın payı |
| `other_attr` | Ödənişlə göndərdiyiniz əlavə məlumat |
| `trace_id` | Epoint-in izləmə identifikatoru |
| `raw` | Açılmış JSON, lüğət şəklində |

Status köməkçi xassələrə çevrilir:

```python
tx.paid       # status: success
tx.failed     # status: failed və ya error
tx.returned   # status: returned
tx.pending    # status: new, server_error və ya unknown
tx.final      # gözləmədə deyil
```

Naməlum status dəyəri heç vaxt xəta qaldırmır. O, `Status.UNKNOWN` olur və gözləmədə sayılır. Beləliklə, kodunuz təxmin etmək əvəzinə gözləyir.

### Əməliyyat kodları

`operation_code` callback-in hansı növ əməliyyata aid olduğunu göstərir. Onu {py:class}`~epoint_sdk.OperationCode` ilə müqayisə edin:

| Dəyər | Sabit | Əməliyyat |
| --- | --- | --- |
| `001` | `OperationCode.CARD_REGISTRATION` | Kart ödənişsiz yadda saxlanılıb |
| `100` | `OperationCode.PAYMENT` | Ödəniş |
| `200` | `OperationCode.REGISTRATION_WITH_PAYMENT` | Kart ödənişlə birlikdə yadda saxlanılıb |

```python
from epoint_sdk import OperationCode

if tx.operation_code == OperationCode.CARD_REGISTRATION:
    save_card(tx.card_id, tx.card_mask)
```

## Callback-i sifarişinizlə tutuşdurmaq

Düzgün imza yalnız callback-i Epoint-in göndərdiyini sübut edir. Onun baxdığınız sifarişə aid olduğunu isə sübut etmir. Callback-i həmişə saxladığınız məlumatla müqayisə edin:

```python
order = Order.objects.get(number=tx.order_id)

if not tx.matches(order_id=order.number, amount=order.total, transaction=order.epoint_transaction):
    log.warning("Callback %s sifarişinə uyğun gəlmir", order.number)
    return HttpResponse("OK")
```

`matches()` bu hallarda `False` qaytarır:

- `order_id` verilib və fərqlidir,
- `transaction` verilib, callback-də tranzaksiya identifikatoru var və onlar fərqlidir,
- `amount` verilib və fərqlidir. Məbləğ `Decimal` kimi müqayisə olunur, ona görə `"19.9"` və `Decimal("19.90")` bərabər sayılır.

Vermədiyiniz arqumentlər yoxlanılmır.

## Handler-i təkrara davamlı etmək

Hər callback-in bir neçə dəfə gələ biləcəyini nəzərə alın və handler-i idempotent yazın:

```python
if tx.paid and order.status != "paid":
    order.mark_paid(transaction=tx.transaction)
```

İşi verilənlər bazası tranzaksiyası daxilində görün, bazanız dəstəkləyirsə sifariş sətrini kilidləyin və yalnız bundan sonra cavab verin.

## Cavab vermək

Nəticəni qeyd edən kimi HTTP 200 ilə tez cavab verin. E-poçt göndərmək və ya hesab-faktura hazırlamaq kimi ağır işləri fon tapşırığına keçirin ki, yavaş poçt serveri yavaş və ya uğursuz callback-ə çevrilməsin.

Callback serverdən serverə gələn sorğudur və CSRF tokeni daşımır. Callback view-unu CSRF qorumasından azad edin, [Django nümunəsində](../examples/django.md) olduğu kimi.

## Uğurlu ödəniş səhifəsi təsdiq deyil

Müştəri `success_url` səhifənizə düşəndə ona "ödənişinizi təsdiqləyirik" kimi mehriban səhifə göstərin və sifarişin vəziyyətini öz bazanızdan oxuyun. Callback hələ gəlməyibsə, səhifədən öz backend-inizi dövri olaraq soruşun və ya serverdə `ep.payments.status(transaction)` çağırın.

## Callback heç gəlməyəndə

Şəbəkələr nasaz olur. Uzun müddət gözləmədə qalan sifarişləri tapan və vəziyyətlərini birbaşa Epoint-dən soruşan dövri tapşırıq işə salın. Tam tapşırıq [üzləşmə nümunəsində](../examples/reconciliation.md) var.

## Testlərdə callback hazırlamaq

`callback_form` verilən məlumatdan Epoint-in edəcəyi kimi düzgün imzalanmış forma hazırlayır:

```python
from epoint_sdk import callback_form

form = callback_form(PRIVATE_KEY, {
    "status": "success",
    "order_id": "ORDER-1042",
    "transaction": "te001",
    "amount": 19.9,
})
response = client.post("/payments/epoint/callback/", form)
```

Ətraflı: [Test](testing.md).
