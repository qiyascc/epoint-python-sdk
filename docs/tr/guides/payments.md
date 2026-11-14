# Ödemeler

Standart bir kart ödemesi Epoint'in kendi sayfasında gerçekleşir. Sunucunuz ödemeyi oluşturur, müşteri Epoint sayfasında öder ve sonuç imzalı bir callback ile geri gelir. Bu sayfa böyle bir ödemeyi başlatmanın tüm yollarını anlatır.

## Ödeme oluşturmak

```python
checkout = ep.payments.create(
    "49.00",
    "ORDER-2001",
    description="Yıllık abonelik",
    language="en",
    currency="AZN",
    success_url="https://shop.az/payment/ok?order=ORDER-2001",
    error_url="https://shop.az/payment/fail?order=ORDER-2001",
)
```

| Argüman | Zorunlu | Anlamı |
| --- | --- | --- |
| `amount` | evet | `str`, `Decimal` veya `int` olarak tutar. En fazla iki ondalık basamak, sıfırdan büyük |
| `order_id` | evet | Benzersiz sipariş kimliğiniz, en fazla 255 karakter |
| `description` | hayır | Ödeme sayfasında gösterilen metin, en fazla 1000 karakter |
| `language` | hayır | `az`, `en` veya `ru`. Varsayılan olarak `language` ayarı kullanılır |
| `currency` | hayır | `AZN`, `USD`, `EUR` veya `RUB`. Varsayılan olarak `currency` ayarı kullanılır |
| `success_url` | hayır | Müşterinin ödemeden sonra gideceği sayfa. Varsayılan olarak `success_url` ayarı kullanılır |
| `error_url` | hayır | Müşterinin başarısız ödemeden sonra gideceği sayfa. Varsayılan olarak `error_url` ayarı kullanılır |
| `installment` | hayır | `True` olduğunda, hesabınız izin veriyorsa müşteri sayfada bir taksit planı seçebilir |
| `other_attr` | hayır | Epoint'in ödemeyle birlikte sakladığı ek veri. Sonuçta `other_attr` alanında geri gelir |

`order_id` sonrasındaki argümanlar yalnızca anahtar kelimeyle verilir.

Çağrı bir {py:class}`~epoint_sdk.Redirect` döndürür:

| Alan | Anlamı |
| --- | --- |
| `redirect_url` | Müşteriyi göndermeniz gereken Epoint sayfası |
| `transaction` | Epoint'in bu ödeme için kimliği. Siparişle birlikte saklayın |
| `trace_id` | Epoint'in izleme kimliği, destek ekibine başvururken işe yarar |
| `message` | Ödeme altyapısından gelen mesaj, varsa |
| `raw` | Yanıtın tamamı, dict olarak |

## Sipariş kimlikleri

Sipariş kimliği sizin idempotency anahtarınızdır. Epoint daha önce kabul ettiği bir sipariş kimliğini tekrar kabul etmez, bu yüzden:

- kimliği her ödeme denemesi için bir kez üretin ve Epoint'e istek atmadan önce kaydedin,
- bir ağ hatasından sonra aynı denemeyi tekrarlıyorsanız **aynı** kimliği kullanın,
- **yeni** kimliği yalnızca müşteri gerçekten yeni bir denemeye başladığında üretin, örneğin kartı reddedildikten sonra.

Basit bir yöntem sipariş numarasına bir deneme sayacı eklemektir: `ORDER-2001-1`, `ORDER-2001-2`.

## Tutarlar

SDK göndermeden önce her tutarı iki ondalık basamaklı bir `Decimal`'e çevirir:

```python
ep.payments.create("10", "A-1")            # 10.00
ep.payments.create(Decimal("9.9"), "A-2")  # 9.90
```

Bunlar `InvalidRequestError` fırlatır ve hiçbir şey gönderilmez:

```python
ep.payments.create("1.005", "A-3")   # ikiden fazla ondalık basamak
ep.payments.create(0, "A-4")         # sıfırdan büyük değil
ep.payments.create("NaN", "A-5")     # sonlu bir sayı değil
ep.payments.create(True, "A-6")      # bool bir tutar değildir
```

Float kabul edilir ama string veya `Decimal` her zaman daha güvenli seçimdir.

## Yönlendirme yerine imzalı form

`payments.form()` metodu `create()` ile aynı argümanları alır ama Epoint'e istek göndermez. İsteği yerelde imzalar ve müşterinin tarayıcısından gönderilecek bir form döndürür:

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
  <button type="submit">19.90 AZN öde</button>
</form>
```

Tarayıcının doğrudan Epoint sayfasına gitmesini istediğinizde kullanın, örneğin düz bir HTML sayfasından. Callback, `create()` ile olduğu gibi çalışır.

## Durumu sorgulamak

```python
tx = ep.payments.status("te001234")
```

Yanıt bir {py:class}`~epoint_sdk.Transaction` nesnesidir. Onu okumanın en kolay yolu yardımcı özelliklerdir:

| Özellik | Durum şu olduğunda `True` |
| --- | --- |
| `paid` | `success` |
| `failed` | `failed` veya `error` |
| `returned` | `returned` (ödeme iade edildi) |
| `pending` | `new`, `server_error` veya bilinmeyen herhangi bir değer |
| `final` | beklemede olmayan her durum |

Kartın reddedilmesi bir hata değil, normal bir yanıttır: `status()` hata fırlatmak yerine `failed` özelliği `True` olan bir işlem döndürür. Durum sorgusunu tekrarlamak güvenlidir, bu yüzden SDK onu zaman aşımlarında ve sunucu hatalarında yeniden dener.

## Ödeme sayfasında taksit

Hesabınızda taksit açıksa `installment=True` müşterinin Epoint sayfasında bir plan seçmesini sağlar:

```python
ep.payments.create("1200", "ORDER-3001", description="Dizüstü bilgisayar", installment=True)
```

Planı kendi sayfanızda seçtirmek için [Taksit](installments.md) sayfasına bakın.

## Kendi verinizi eklemek

`other_attr` ödemeye ek veri eklemenizi sağlar. İmzalı isteğin bir parçasıdır ve `Transaction.other_attr` alanında geri gelir:

```python
ep.payments.create("5", "ORDER-4001", other_attr={"customer": 77})
```

Bu alanın hangi biçimde kabul edildiğine Epoint karar verir, bu yüzden iç içe veriye güvenmeden önce Epoint ile teyit edin.

## Para tahsil etmenin diğer yolları

- [Kayıtlı kartlar](saved-cards.md): müşteriyi tekrar Epoint sayfasına göndermeden karttan çekim yapmak.
- [Ön provizyon](preauth.md): parayı şimdi bloke etmek, sonra tahsil etmek.
- [Bölünmüş ödeme](split.md): tek bir ödemeyi bir iş ortağıyla paylaşmak.
- [Apple Pay ve Google Pay](apple-google-pay.md): yönlendirme yerine sayfaya gömülen bir widget.
- [Dijital cüzdanlar](wallets.md): Epoint'in desteklediği bir cüzdanla ödeme.
