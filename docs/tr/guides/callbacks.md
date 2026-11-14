# Callback'ler

Callback, Epoint'in bir ödemenin sonucunu sunucunuza bildirdiği istektir. Ödeme akışında güvenebileceğiniz tek parça odur, çünkü gizli anahtarınızla imzalanır. Bu sayfa callback'i nasıl alacağınızı, doğrulayacağınızı ve ona göre nasıl davranacağınızı anlatır.

## Epoint ne gönderir

Epoint, üye işyeri hesabınızda kayıtlı sonuç adresine bir `POST` isteği gönderir. İsteğin gövdesi iki alanlı bir formdur:

`data`
: Sonuç, JSON olarak ve base64 ile kodlanmış halde.

`signature`
: Gizli anahtarınızla hesaplanan `base64(sha1(private_key + data + private_key))`.

Gizli anahtarı yalnızca siz ve Epoint bildiğiniz için, eşleşen bir imza bu `data` değerini tam olarak Epoint'in ürettiğini kanıtlar.

## Callback'i doğrulamak

Formun tamamını `verify_callback` metoduna verin:

```python
from epoint_sdk import SignatureError

try:
    tx = ep.verify_callback(request.POST)
except SignatureError:
    return bad_request()
```

Metot her türlü mapping ile çalışır: Django'nun `request.POST`'u, Flask'ın `request.form`'u, Starlette ve FastAPI'de `await request.form()` sonucu veya düz bir `dict`. Bir alan liste olarak gelirse ilk değeri kullanılır.

İki değer elinizde ayrı ayrı varsa bunları iki argüman olarak verin:

```python
tx = ep.verify_callback(data, signature)
```

İstemci olmadan, örneğin küçük bir worker içinde, modül düzeyindeki fonksiyonu gizli anahtarla çağırın:

```python
from epoint_sdk import verify_callback

tx = verify_callback(PRIVATE_KEY, request.POST)
```

### Neler, hangi sırayla kontrol edilir

1. `data` ve `signature` alanlarının ikisi de var ve boş değil.
2. `data` en fazla 64 KB, `signature` en fazla 128 karakter. Daha büyükleri hash hesaplanmadan önce reddedilir.
3. İmza eşleşiyor. Karşılaştırma sabit sürede yapılır.
4. `data` geçerli bir base64 ve bir JSON nesnesine çözülüyor.

Herhangi bir kontrol başarısız olursa `SignatureError` fırlatılır ve callback'in hiçbir alanı okunmaz. Böyle bir isteğe HTTP 400 ile yanıt verin ve başka hiçbir şey yapmayın.

## Sonucu okumak

`verify_callback` bir {py:class}`~epoint_sdk.Transaction` döndürür. `payments.status()` da aynı tipi döndürür. `Callback` bu sınıfın diğer adıdır.

| Alan | Anlamı |
| --- | --- |
| `status` | Bir {py:class}`~epoint_sdk.Status` değeri: `new`, `success`, `failed`, `error`, `returned`, `server_error` veya `unknown` |
| `transaction` | Epoint'in işlem kimliği |
| `order_id` | Sizin sipariş kimliğiniz |
| `amount` | `Decimal` olarak tutar veya `None` |
| `code` | Epoint gönderdiyse bankanın yanıt kodu |
| `message` | Epoint'ten veya bankadan gelen okunabilir mesaj |
| `bank_transaction` | Bankanın işlem kimliği |
| `bank_response` | Bankanın ham yanıtı |
| `operation_code` | Sonucun hangi işleme ait olduğu, aşağıya bakın |
| `rrn` | Kart ağının referans numarası (RRN) |
| `card_id` | Kart kaydı akışlarında kayıtlı kartın kimliği |
| `card_name` | Epoint gönderdiyse kart sahibinin adı |
| `card_mask` | `411111******1111` gibi maskelenmiş kart numarası |
| `split_amount` | Bölünmüş ödemelerde iş ortağının payı |
| `other_attr` | Ödemeyle gönderdiğiniz ek veri |
| `trace_id` | Epoint'in izleme kimliği |
| `raw` | Çözülmüş JSON, dict olarak |

Durum yardımcı özelliklere çevrilir:

```python
tx.paid       # durum: success
tx.failed     # durum: failed veya error
tx.returned   # durum: returned
tx.pending    # durum: new, server_error veya unknown
tx.final      # beklemede değil
```

Bilinmeyen bir durum değeri asla hata fırlatmaz. `Status.UNKNOWN` olur ve beklemede sayılır, böylece kodunuz tahmin yürütmek yerine bekler.

### İşlem kodları

`operation_code`, callback'in hangi tür işleme ait olduğunu söyler. {py:class}`~epoint_sdk.OperationCode` ile karşılaştırın:

| Değer | Sabit | İşlem |
| --- | --- | --- |
| `001` | `OperationCode.CARD_REGISTRATION` | Kart ödeme olmadan kaydedildi |
| `100` | `OperationCode.PAYMENT` | Ödeme |
| `200` | `OperationCode.REGISTRATION_WITH_PAYMENT` | Kart bir ödemeyle birlikte kaydedildi |

```python
from epoint_sdk import OperationCode

if tx.operation_code == OperationCode.CARD_REGISTRATION:
    save_card(tx.card_id, tx.card_mask)
```

## Callback'i siparişinizle eşleştirmek

Doğru bir imza yalnızca callback'i Epoint'in gönderdiğini kanıtlar. Baktığınız siparişe ait olduğunu kanıtlamaz. Her zaman sakladığınız bilgilerle karşılaştırın:

```python
order = Order.objects.get(number=tx.order_id)

if not tx.matches(order_id=order.number, amount=order.total, transaction=order.epoint_transaction):
    log.warning("Callback %s siparişiyle eşleşmiyor", order.number)
    return HttpResponse("OK")
```

`matches()` şu durumlarda `False` döndürür:

- `order_id` verilmiş ve farklı,
- `transaction` verilmiş, callback'te bir işlem kimliği var ve ikisi farklı,
- `amount` verilmiş ve farklı. Tutar `Decimal` olarak karşılaştırılır, yani `"19.9"` ile `Decimal("19.90")` eşittir.

Vermediğiniz argümanlar kontrol edilmez.

## Handler'ı tekrara dayanıklı yapmak

Her callback'in birden fazla gelebileceğini varsayın ve handler'ı idempotent yazın:

```python
if tx.paid and order.status != "paid":
    order.mark_paid(transaction=tx.transaction)
```

İşi bir veritabanı transaction'ı içinde yapın, veritabanınız destekliyorsa sipariş satırını kilitleyin ve ancak ondan sonra yanıt verin.

## Yanıt vermek

Sonucu kaydeder kaydetmez HTTP 200 ile hızlıca yanıt verin. E-posta göndermek veya fatura hazırlamak gibi ağır işleri bir arka plan görevine bırakın ki yavaş bir posta sunucusu yavaş veya başarısız bir callback'e dönüşmesin.

Callback'ler sunucudan sunucuya yapılan isteklerdir ve CSRF token taşımaz. Callback view'ını CSRF korumasından muaf tutun, [Django örneğinde](../examples/django.md) olduğu gibi.

## Başarılı ödeme sayfası bir onay değildir

Müşteri `success_url` sayfanıza geldiğinde ona "ödemenizi doğruluyoruz" gibi nazik bir sayfa gösterin ve siparişin durumunu kendi veritabanınızdan okuyun. Callback henüz gelmediyse sayfadan kendi backend'inizi belirli aralıklarla sorgulayın veya sunucuda `ep.payments.status(transaction)` çağırın.

## Callback hiç gelmezse

Ağlar sorun çıkarır. Uzun süre beklemede kalan siparişleri bulup durumlarını doğrudan Epoint'e soran periyodik bir görev çalıştırın. Görevin tamamı [mutabakat örneğinde](../examples/reconciliation.md).

## Testlerde callback üretmek

`callback_form`, verilen veriden Epoint'in yapacağı gibi doğru imzalanmış bir form üretir:

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

Ayrıntılar: [Test](testing.md).
