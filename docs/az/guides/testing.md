# İnteqrasiyanın testi

Test üç səviyyədə aparıla bilər: saxta ödəniş sistemi ilə unit testlər, lokal sandbox ilə inteqrasiya testləri və sonda real ödəniş sistemində real pulla yoxlama.

## Saxta transport ilə unit testlər

`httpx.MockTransport` olan `httpx.Client` ötürün və SDK şəbəkəyə ümumiyyətlə çıxmayacaq. Handler hər sorğunu qəbul edir və sizə lazım olan cavabı qaytarır:

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

### Sorğunun içinə baxmaq

Sorğular `data` və `signature` sahələri olan forma kimi göndərilir. Yuxarıdakı `gateway` hər sorğunu `sent` siyahısında saxlayır, ona görə onları açıb kodunuzun nə göndərdiyini yoxlaya bilərsiniz:

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

### Xətaları imitasiya etmək

Xəta emalını yoxlamaq üçün handler-dən httpx istisnası qaldırın:

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

Təkrar cəhd testləri tez bitsin deyə `max_retries=0` təyin edin və ya `backoff_base` və `backoff_cap` üçün kiçik dəyərlər verin.

## Callback view-unun testi

`callback_form` məlumatı Epoint-in etdiyi kimi imzalayır:

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

Səhv olanda pul itkisinə səbəb olan hallar üçün test yazın: saxta imza, başqa sifariş üçün callback, səhv məbləğ, təkrar gələn callback və uğursuz status.

## epoint-sandbox ilə inteqrasiya testləri

[epoint-sandbox](https://github.com/martian56/epoint-sandbox) Epoint API-sini öz kompüterinizdə təkrarlayan icma layihəsidir: ödəniş səhifəsi, test kartları, idarə paneli və nəticə ünvanınıza göndərilən imzalı callback-lər. Onu Epoint hazırlamayıb.

### 1-ci addım. Sandbox-u işə salın

```console
$ docker run -d -p 8181:8181 --name epoint \
    --add-host=host.docker.internal:host-gateway \
    ghcr.io/martian56/epoint-sandbox
```

İdarə paneli `http://localhost:8181` ünvanındadır.

### 2-ci addım. SDK-nı sandbox-a yönəldin

```console
$ export EPOINT_BASE_URL=http://localhost:8181
$ export EPOINT_PUBLIC_KEY=i000000001
$ export EPOINT_PRIVATE_KEY=sandbox_private_key_0000000001
```

`http://localhost` ünvanı `allow_insecure_http` olmadan da icazəlidir. Sandbox şəbəkənizdəki başqa kompüterdə işləyirsə, yalnız orada `EPOINT_ALLOW_INSECURE_HTTP=true` da təyin edin.

### 3-cü addım. Callback-lərin hara göndəriləcəyini göstərin

Callback-lər konteynerin içindən göndərilir və orada `localhost` konteynerin özüdür. Öz kompüterinizə çatmaq üçün `host.docker.internal` işlədin:

```console
$ curl -X PATCH http://localhost:8181/_sandbox/merchants/i000000001 \
    -H "Content-Type: application/json" \
    -d '{"result_url": "http://host.docker.internal:8000/payments/epoint/callback/"}'
```

### 4-cü addım. Test kartı ilə ödəyin

Tətbiqinizdən ödəniş yaradın, `redirect_url` ünvanını açın və `4111 1111 1111 1111` kartı, gələcək istənilən bitmə tarixi və istənilən CVV ilə ödəyin. Sandbox-un README faylında kartın rədd edilməsi, 3-D Secure və gözləmə müddətinin bitməsi halları üçün başqa kartlar da var.

Sandbox-un idarə paneli hər sorğunu, açılmış məlumatı və serverinizin cavabı ilə birlikdə hər callback cəhdini göstərir. Bu, imza problemlərini görməyi asanlaşdırır.

## Real ödəniş sistemində son yoxlama

İşə buraxmazdan əvvəl kiçik məbləğlə və real kartla bir real ödəniş edin, sonra onu `payments.reverse()` ilə geri qaytarın. Callback-in gəldiyinə, sifarişin düz bir dəfə ödənilmiş kimi qeyd olunduğuna və geri qaytarmanın `returned` kimi göründüyünə baxın.
