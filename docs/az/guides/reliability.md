# Etibarlılıq

Şəbəkə iki çox fərqli şəkildə nasaz olur və ödəniş klienti onları bir-birindən ayırmalıdır:

- **Heç nə göndərilməyib.** Bağlantı rədd edilib və ya heç açılmayıb. Yenidən cəhd etmək zərərsizdir.
- **Nəsə göndərilib, amma aydın cavab gəlməyib.** Sorğu serverinizdən çıxandan sonra gözləmə müddəti bitib, bağlantı qırılıb və ya 5xx xətası gəlib. Epoint kartdan pulu artıq çıxmış ola bilər. Eyni sorğunu yenidən göndərsəniz, pul iki dəfə çıxıla bilər.

SDK hər çağırışı iki qrupdan birinə aid edir və onlara fərqli qaydalar tətbiq edir.

## Çağırışların iki növü

Pul hərəkət etdirən çağırışlar
: `payments.create`, `payments.reverse`, `payments.hold`, `payments.capture`, `cards.register`, `cards.register_and_pay`, `cards.charge`, `cards.payout`, bütün `split` çağırışları, `installments.create`, `wallets.pay`, bütün `widgets` çağırışları, `invoices.create`, `invoices.update`, `invoices.send_sms`, `invoices.send_email`, `transfers.create`, həmçinin `safe=True` verilməyibsə `request()`.

Yalnız oxuyan çağırışlar
: `payments.status`, `cards.status`, `installments.plans`, `wallets.list`, `invoices.get`, `invoices.list`, `transfers.status` və `heartbeat`.

## Hər xətada nə baş verir

| Xəta | Pul hərəkət etdirən çağırışlar | Yalnız oxuyan çağırışlar |
| --- | --- | --- |
| Bağlantı rədd edilib, bağlantı və ya hovuz gözləmə müddəti bitib | Təkrarlanır, sonra `NotSentError` | Təkrarlanır, sonra `NotSentError` |
| Cavabı gözləmə müddəti bitib, göndərildikdən sonra bağlantı qırılıb | **Təkrarlanmır**, `OutcomeUnknownError` | Təkrarlanır, sonra `TransportError` |
| HTTP 429 | Təkrarlanır, sonra `HTTPStatusError` | Təkrarlanır, sonra `HTTPStatusError` |
| HTTP 500, 502, 503, 504 | **Təkrarlanmır**, `OutcomeUnknownError` | Təkrarlanır, sonra `HTTPStatusError` |
| Digər 5xx | `OutcomeUnknownError` | `HTTPStatusError` |
| JSON olmayan gövdə ilə 2xx | `OutcomeUnknownError` | `HTTPStatusError` |
| Digər 4xx | `HTTPStatusError` | `HTTPStatusError` |
| `status: error` olan JSON | `GatewayError` | `GatewayError` |

HTTP 429 Epoint-in sorğunu emal etmədiyini bildirir, ona görə ödənişlər üçün də təkrarlanır.

## SDK nə qədər gözləyir

`max_retries` (standart dəyər 2) əlavə cəhdlərin sayıdır. SDK `n` nömrəli cəhddən (0-dan sayılır) əvvəl

```text
min(backoff_cap, backoff_base * 2 ** n) + random(0, backoff_base / 2)
```

saniyə gözləyir. Standart dəyərlərlə bu, təxminən əvvəlcə 0.5, sonra 1 saniyədir. Təsadüfi hissə çoxlu worker-in eyni anda təkrar cəhd etməsinin qarşısını alır.

Hər cəhd bağlantı üçün ən çox `connect_timeout` (standart dəyər 10), hər oxuma və yazma üçün isə ən çox `timeout` (standart dəyər 30) saniyə gözləyir.

```python
ep = Epoint(timeout=15, connect_timeout=5, max_retries=3, backoff_base=0.3, backoff_cap=4)
```

`max_retries=0` təkrar cəhdləri tamamilə söndürür.

## OutcomeUnknownError ilə necə davranmalı

İstisna `order_id` dəyərini daşıyır. Yeni sifariş identifikatoru yaratmayın və sorğunu yenidən göndərməyin. Əvvəlcə nə baş verdiyini öyrənin:

```python
from epoint_sdk import OutcomeUnknownError

try:
    tx = ep.cards.charge(card_id, "9.90", "SUB-1001-3")
except OutcomeUnknownError as exc:
    queue_check(exc.order_id)
```

Sonra fon tapşırığı ödənişi yoxlayır. Ödəniş səhifəsindən keçən ödənişlər üçün `transaction` identifikatoru əlinizdədir və `payments.status()` çağıra bilərsiniz. Kartdan birbaşa pul çıxılıbsa, callback-i gözləyin və ya **eyni sifariş identifikatoru ilə** yenidən cəhd edin: Epoint artıq qəbul etdiyi identifikatoru rədd edir, ona görə pul ikinci dəfə çıxıla bilməz. Bu təkrar cəhddə gələn `GatewayError` birinci cəhdin Epoint-ə çatdığını göstərir, onun necə bitdiyini isə callback bildirir.

## Özünüz təhlükəsiz təkrarlamaq

1. Birinci çağırışdan əvvəl sifariş identifikatorunu saxlayın.
2. `NotSentError` alanda eyni identifikatorla istədiyiniz vaxt yenidən cəhd edin.
3. `OutcomeUnknownError` alanda əvvəlcə yoxlayın. Yalnız eyni identifikatorla təkrarlayın.
4. Xətanı "keçmək" üçün heç vaxt yeni sifariş identifikatoru yaratmayın. İkiqat ödənişlər məhz belə yaranır.

## Sorğu ölçüsü məhdudiyyətləri

- Mətn sahələri göndərilməzdən əvvəl yoxlanılır: `order_id` 255 simvola, `description` 1000 simvola, telefon nömrələri 32 simvola, e-poçt ünvanları 254 simvola, IBAN 34 simvola qədər.
- 64 KB-dan böyük callback `data` dəyəri və 128 simvoldan uzun imza heç bir hash hesablanmadan rədd edilir. Beləcə nəhəng saxta sorğu serverinizi məşğul saxlaya bilmir.
