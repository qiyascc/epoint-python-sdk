# Entegrasyonu test etmek

Üç düzeyde test yapabilirsiniz: sahte bir ödeme altyapısıyla birim testleri, yerel bir sandbox ile entegrasyon testleri ve son olarak canlı altyapıda gerçek parayla bir kontrol.

## Sahte transport ile birim testleri

`httpx.MockTransport` içeren bir `httpx.Client` verin, SDK ağa hiç çıkmaz. Handler her isteği alır ve ihtiyacınız olan yanıtı döndürür:

```python
import httpx
import pytest
from epoint_sdk import Epoint, signing

PRIVATE = "test_private_key"
sent = []

def gateway(request: httpx.Request) -> httpx.Response:
    sent.append(request)
    if request.url.path == "/api/1/request":
        return httpx.Response(200, json={
            "status": "success",
            "redirect_url": "https://epoint.az/checkout/abc",
            "transaction": "te001",
        })
    return httpx.Response(404, json={"detail": "not found"})

@pytest.fixture
def ep():
    http = httpx.Client(transport=httpx.MockTransport(gateway))
    return Epoint("i000000001", PRIVATE, http_client=http)

def test_checkout(ep):
    checkout = ep.payments.create("19.90", "ORDER-1")
    assert checkout.transaction == "te001"
```

### İsteğin içine bakmak

İstekler `data` ve `signature` alanlarını içeren bir form olarak gönderilir. Yukarıdaki `gateway` her isteği `sent` listesinde tutar, böylece onları çözüp kodunuzun ne gönderdiğini kontrol edebilirsiniz:

```python
from urllib.parse import parse_qs

def test_amount_is_sent_as_number(ep):
    ep.payments.create("19.90", "ORDER-2")
    form = {k: v[0] for k, v in parse_qs(sent[-1].content.decode()).items()}
    assert signing.matches(PRIVATE, form["data"], form["signature"])
    payload = signing.decode(form["data"])
    assert payload["amount"] == 19.9
    assert payload["order_id"] == "ORDER-2"
```

### Arızaları taklit etmek

Hata yönetiminizi test etmek için handler'dan bir httpx istisnası fırlatın:

```python
from epoint_sdk import OutcomeUnknownError

def timeout(request):
    raise httpx.ReadTimeout("slow", request=request)

def test_charge_timeout_is_not_retried():
    ep = Epoint("i000000001", PRIVATE, http_client=httpx.Client(transport=httpx.MockTransport(timeout)))
    with pytest.raises(OutcomeUnknownError) as info:
        ep.cards.charge("card-1", "5", "SUB-9")
    assert info.value.order_id == "SUB-9"
```

Yeniden deneme testlerinin hızlı bitmesi için `max_retries=0` verin veya `backoff_base` ve `backoff_cap` için küçük değerler kullanın.

## Callback view'ını test etmek

`callback_form` bir veriyi Epoint'in yaptığı gibi imzalar:

```python
from epoint_sdk import callback_form

def test_callback_marks_order_paid(client, order):
    form = callback_form(PRIVATE, {
        "status": "success",
        "order_id": order.number,
        "transaction": "te001",
        "amount": str(order.total),
    })
    response = client.post("/payments/epoint/callback/", form)
    assert response.status_code == 200
    order.refresh_from_db()
    assert order.status == "paid"

def test_forged_callback_is_rejected(client, order):
    form = callback_form("wrong-key", {"status": "success", "order_id": order.number})
    response = client.post("/payments/epoint/callback/", form)
    assert response.status_code == 400
```

Ters gittiğinde para kaybettiren durumlar için test yazın: sahte imza, başka bir siparişe ait callback, yanlış tutar, tekrarlanan callback ve başarısız durum.

## epoint-sandbox ile entegrasyon testleri

[epoint-sandbox](https://github.com/martian56/epoint-sandbox), Epoint API'sini kendi bilgisayarınızda taklit eden bir topluluk projesidir: ödeme sayfası, test kartları, bir yönetim paneli ve sonuç adresinize gönderilen imzalı callback'ler. Epoint tarafından geliştirilmemiştir.

### 1. adım. Sandbox'ı başlatın

```console
$ docker run -d -p 8181:8181 --name epoint \
    --add-host=host.docker.internal:host-gateway \
    ghcr.io/martian56/epoint-sandbox
```

Yönetim paneli `http://localhost:8181` adresindedir.

### 2. adım. SDK'yı sandbox'a yönlendirin

```console
$ export EPOINT_BASE_URL=http://localhost:8181
$ export EPOINT_PUBLIC_KEY=i000000001
$ export EPOINT_PRIVATE_KEY=sandbox_private_key_0000000001
```

`http://localhost` adresine `allow_insecure_http` olmadan da izin verilir. Sandbox ağınızdaki başka bir makinede çalışıyorsa yalnızca orada `EPOINT_ALLOW_INSECURE_HTTP=true` da ayarlayın.

### 3. adım. Callback'lerin nereye gideceğini belirtin

Callback'ler konteynerin içinden gönderilir ve orada `localhost` konteynerin kendisidir. Kendi makinenize ulaşmak için `host.docker.internal` kullanın:

```console
$ curl -X PATCH http://localhost:8181/_sandbox/merchants/i000000001 \
    -H "Content-Type: application/json" \
    -d '{"result_url": "http://host.docker.internal:8000/payments/epoint/callback/"}'
```

### 4. adım. Test kartıyla ödeyin

Uygulamanızdan bir ödeme oluşturun, `redirect_url` adresini açın ve `4111 1111 1111 1111` kartı, gelecekteki herhangi bir son kullanma tarihi ve herhangi bir CVV ile ödeyin. Sandbox'ın README dosyasında kart reddi, 3-D Secure ve zaman aşımı durumları için başka kartlar da var.

Sandbox paneli her isteği, çözülmüş veriyi ve sunucunuzun yanıtıyla birlikte her callback denemesini gösterir. Bu da imza sorunlarını görmeyi kolaylaştırır.

## Canlı altyapıda son kontrol

Canlıya çıkmadan önce küçük bir tutarla ve gerçek bir kartla bir gerçek ödeme yapın, ardından `payments.reverse()` ile iade edin. Callback'in geldiğini, siparişin tam olarak bir kez ödendi olarak işaretlendiğini ve iadenin `returned` olarak göründüğünü kontrol edin.
