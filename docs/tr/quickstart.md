# Hızlı başlangıç

Bu sayfada tek bir ödeme baştan sona izleniyor: istek oluşturulur, müşteri Epoint sayfasına yönlendirilir ve sonuç sunucunuzda doğrulanır. Paketin [kurulu](installation.md) ve [anahtarlarınızın](keys.md) hazır olduğu varsayılıyor.

## Bir ödeme nasıl ilerler

1. Sunucunuz Epoint'ten bir ödeme sayfası ister. Epoint bir `redirect_url` ve bir `transaction` kimliğiyle yanıt verir.
2. Müşteriyi `redirect_url` adresine yönlendirirsiniz. Müşteri kart bilgilerini Epoint sayfasında girer.
3. Epoint müşteriyi başarılı veya başarısız ödeme sayfanıza geri gönderir.
4. Epoint sonuç adresinize imzalı bir callback gönderir. Siparişi ödendi olarak işaretlemenin zamanı **tam olarak budur**.

Üçüncü adım yalnızca müşteri içindir. Başarılı ödeme sayfanızı herkes tarayıcıya elle yazıp açabilir, bu yüzden hiçbir şey kanıtlamaz. Dördüncü adım ise gizli anahtarınızla imzalanır ve imzası doğrulandıktan sonra güvenilebilir.

## 1. adım. İstemciyi oluşturun

```python
from epoint_sdk import Epoint

ep = Epoint(
    "i000000001",
    "PRIVATE_KEY",
    success_url="https://shop.az/payment/ok",
    error_url="https://shop.az/payment/fail",
)
```

- İlk iki argüman açık ve gizli anahtarınızdır.
- `success_url` ve `error_url` tüm ödemeler için varsayılan olur. Gerekirse her çağrıda değiştirebilirsiniz.
- Ödeme sayfasının dili varsayılan olarak `az`, para birimi ise `AZN` olur.

İstemciyi uygulama açılırken bir kez oluşturun ve tekrar tekrar kullanın. İstemci bir HTTP bağlantı havuzunu açık tutar. Uygulama kapanırken `ep.close()` çağırın, kısa betiklerde ise `with` bloğu kullanın.

## 2. adım. Ödemeyi oluşturun

```python
checkout = ep.payments.create(
    "19.90",
    "ORDER-1042",
    description="Pro plan, 1 ay",
)
```

Satır satır:

- `"19.90"` tutardır. Yuvarlama sürprizleri yaşamamak için float yerine string veya `Decimal` verin. İkiden fazla ondalık basamak, sıfır, negatif sayılar, `NaN` ve bool değerler istek gönderilmeden `InvalidRequestError` ile reddedilir.
- `"ORDER-1042"` sipariş kimliğinizdir. Her ödeme için benzersiz olmalıdır. Epoint daha önce gördüğü bir kimliği kabul etmez ve sizi çift çekimden koruyan da budur.
- `description` ödeme sayfasında müşteriye gösterilir.

Sonuç bir `Redirect` nesnesidir:

```python
>>> checkout
Redirect(redirect_url='https://epoint.az/...', transaction='te001...', trace_id=None, message=None)
```

`checkout.transaction` değerini siparişin yanında saklayın. Durumu sorgulamak veya daha sonra iade yapmak için buna ihtiyacınız olacak.

## 3. adım. Müşteriyi Epoint'e gönderin

Yönlendirmenin nasıl yapılacağı kullandığınız çatıya bağlıdır. Django'da şöyledir:

```python
from django.shortcuts import redirect

return redirect(checkout.redirect_url)
```

## 4. adım. Ödemeyi callback'te onaylayın

Epoint sonuç adresinize iki form alanı gönderir: `data` ve `signature`. Formun tamamını `verify_callback` metoduna verin:

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

- `verify_callback` imzayı sabit sürede doğrular ve veriyi ancak bundan sonra çözer. Sahte veya bozuk bir callback `SignatureError` fırlatır.
- `tx.paid` yalnızca durum `success` olduğunda `True` olur.
- `tx.matches(...)` callback'in beklediğiniz sipariş ve tutarla ilgili olduğunu kontrol eder. Başka, daha ucuz bir sipariş için gelen geçerli bir callback bu siparişi açmamalıdır.

Bu view'ın canlıya hazır tam hali [Django örneğinde](examples/django.md).

## 5. adım. Emin değilseniz Epoint'e sorun

Callback hiç gelmezse durumu doğrudan sorun:

```python
tx = ep.payments.status(checkout.transaction)
print(tx.status, tx.paid, tx.pending)
```

Kart reddedildiğinde `status()` hata fırlatmaz. `failed` özelliği `True` olan bir `Transaction` döndürür.

## 6. adım. İstemciyi kapatın

```python
ep.close()
```

veya istemciyi bağlam yöneticisi olarak kullanın:

```python
with Epoint() as ep:
    ...
```

## Sırada ne var

- [Yapılandırma](configuration.md) tüm ayarları ve anahtarların ortam değişkenlerinden veya bir dosyadan nasıl okunacağını gösterir.
- [Ödemeler](guides/payments.md) `create` metodunun diğer seçeneklerini, imzalı HTML formunu ve taksiti anlatır.
- [Callback'ler](guides/callbacks.md) sonucun her alanını açıklar.
- [Hatalar](guides/errors.md) ve [Güvenilirlik](guides/reliability.md) ağ sorun çıkardığında ne yapmanız gerektiğini anlatır.
