# Ödənişlər

Adi kart ödənişi Epoint-in öz səhifəsində baş verir. Serveriniz ödənişi yaradır, müştəri Epoint səhifəsində ödəyir, nəticə isə imzalı callback ilə geri gəlir. Bu səhifədə belə ödənişə başlamağın bütün yolları göstərilir.

## Ödəniş yaratmaq

```python
checkout = ep.payments.create(
    "49.00",
    "ORDER-2001",
    description="İllik abunə",
    language="en",
    currency="AZN",
    success_url="https://shop.az/payment/ok?order=ORDER-2001",
    error_url="https://shop.az/payment/fail?order=ORDER-2001",
)
```

| Arqument | Mütləqdir | Mənası |
| --- | --- | --- |
| `amount` | bəli | `str`, `Decimal` və ya `int` şəklində məbləğ. Ən çox iki onluq rəqəm, sıfırdan böyük |
| `order_id` | bəli | Sifarişinizin unikal identifikatoru, 255 simvola qədər |
| `description` | xeyr | Ödəniş səhifəsində göstərilən mətn, 1000 simvola qədər |
| `language` | xeyr | `az`, `en` və ya `ru`. Standart olaraq `language` ayarı götürülür |
| `currency` | xeyr | `AZN`, `USD`, `EUR` və ya `RUB`. Standart olaraq `currency` ayarı götürülür |
| `success_url` | xeyr | Müştərinin ödənişdən sonra gedəcəyi səhifə. Standart olaraq `success_url` ayarı götürülür |
| `error_url` | xeyr | Müştərinin uğursuz ödənişdən sonra gedəcəyi səhifə. Standart olaraq `error_url` ayarı götürülür |
| `installment` | xeyr | `True` olanda hesabınız icazə verirsə, müştəri səhifədə taksit planı seçə bilir |
| `other_attr` | xeyr | Epoint-in ödənişlə birlikdə saxladığı əlavə məlumat. Nəticədə `other_attr` sahəsində geri gəlir |

`order_id` arqumentindən sonrakı arqumentlər yalnız açar sözlə verilir.

Metod {py:class}`~epoint_sdk.Redirect` qaytarır:

| Sahə | Mənası |
| --- | --- |
| `redirect_url` | Müştərini göndərməli olduğunuz Epoint səhifəsi |
| `transaction` | Epoint-in bu ödəniş üçün identifikatoru. Onu sifarişlə birlikdə saxlayın |
| `trace_id` | Epoint-in izləmə identifikatoru, dəstəyə müraciət edəndə lazım olur |
| `message` | Ödəniş sistemindən gələn mesaj, əgər varsa |
| `raw` | Bütöv JSON cavabı, lüğət (dict) şəklində |

## Sifariş identifikatorları

Sifariş identifikatoru sizin idempotentlik açarınızdır. Epoint artıq qəbul etdiyi identifikatoru ikinci dəfə qəbul etmir, ona görə:

- identifikatoru hər ödəniş cəhdi üçün bir dəfə yaradın və Epoint-ə müraciət etməzdən əvvəl saxlayın,
- şəbəkə xətasından sonra eyni cəhdi təkrarlayanda **eyni** identifikatoru işlədin,
- **yeni** identifikatoru yalnız müştəri həqiqətən yeni cəhdə başlayanda yaradın, məsələn kart rədd ediləndən sonra.

Sadə üsul sifariş nömrəsinə cəhd sayğacını əlavə etməkdir: `ORDER-2001-1`, `ORDER-2001-2`.

## Məbləğlər

SDK göndərməzdən əvvəl hər məbləği iki onluq rəqəmli `Decimal` tipinə çevirir:

```python
ep.payments.create("10", "A-1")            # 10.00
ep.payments.create(Decimal("9.9"), "A-2")  # 9.90
```

Bunlar `InvalidRequestError` qaldırır və heç nə göndərilmir:

```python
ep.payments.create("1.005", "A-3")   # ikidən çox onluq rəqəm
ep.payments.create(0, "A-4")         # sıfırdan böyük deyil
ep.payments.create("NaN", "A-5")     # sonlu ədəd deyil
ep.payments.create(True, "A-6")      # bool məbləğ deyil
```

Float qəbul olunur, amma sətir və ya `Decimal` həmişə daha etibarlı seçimdir.

## Yönləndirmə əvəzinə imzalı forma

`payments.form()` metodu `create()` ilə eyni arqumentləri qəbul edir, amma Epoint-ə sorğu göndərmir. O, sorğunu lokal imzalayır və müştərinin brauzerindən göndəriləcək forma qaytarır:

```python
form = ep.payments.form("19.90", "ORDER-1042", description="Pro plan")
form.action   # https://epoint.az/api/1/checkout
form.fields   # {"data": "...", "signature": "..."}
```

Şablonda:

```html
<form method="post" action="{{ form.action }}">
  <input type="hidden" name="data" value="{{ form.data }}">
  <input type="hidden" name="signature" value="{{ form.signature }}">
  <button type="submit">19.90 AZN ödə</button>
</form>
```

Brauzerin birbaşa Epoint səhifəsinə getməsini istəyəndə bu üsuldan istifadə edin, məsələn sadə HTML səhifəsindən. Callback `create()` ilə olduğu kimi işləyir.

## Vəziyyəti yoxlamaq

```python
tx = ep.payments.status("te001234")
```

Cavab {py:class}`~epoint_sdk.Transaction` obyektidir. Onu oxumağın ən asan yolu köməkçi xassələrdir:

| Xassə | Status bu olanda `True` olur |
| --- | --- |
| `paid` | `success` |
| `failed` | `failed` və ya `error` |
| `returned` | `returned` (ödəniş geri qaytarılıb) |
| `pending` | `new`, `server_error` və ya naməlum istənilən dəyər |
| `final` | gözləmədə olmayan istənilən status |

Kartın rədd edilməsi xəta deyil, adi cavabdır: `status()` xəta qaldırmaq əvəzinə `failed` xassəsi `True` olan tranzaksiya qaytarır. Status sorğusunu təkrarlamaq təhlükəsizdir, ona görə SDK onu gözləmə müddəti bitəndə və server xətalarında yenidən göndərir.

## Ödəniş səhifəsində taksit

Hesabınızda taksit aktivdirsə, `installment=True` müştəriyə Epoint səhifəsində plan seçməyə imkan verir:

```python
ep.payments.create("1200", "ORDER-3001", description="Noutbuk", installment=True)
```

Planı öz səhifənizdə seçdirmək üçün [Taksit](installments.md) səhifəsinə baxın.

## Öz məlumatınızı ötürmək

`other_attr` ödənişə əlavə məlumat qoşmağa imkan verir. O, imzalı sorğunun bir hissəsidir və `Transaction.other_attr` sahəsində geri gəlir:

```python
ep.payments.create("5", "ORDER-4001", other_attr={"customer": 77})
```

Bu sahənin hansı formatda qəbul olunduğunu Epoint müəyyən edir, ona görə iç-içə məlumata güvənməzdən əvvəl Epoint ilə dəqiqləşdirin.

## Pul qəbul etməyin digər yolları

- [Yadda saxlanmış kartlar](saved-cards.md): müştərini yenidən Epoint səhifəsinə göndərmədən kartdan pul çıxmaq.
- [Ön avtorizasiya](preauth.md): pulu indi bloklamaq, sonra silmək.
- [Bölünmüş ödəniş](split.md): bir ödənişi tərəfdaşla bölüşmək.
- [Apple Pay və Google Pay](apple-google-pay.md): yönləndirmə əvəzinə səhifəyə yerləşdirilən vidjet.
- [Elektron pul kisələri](wallets.md): Epoint-in dəstəklədiyi pul kisəsi ilə ödəniş.
