# Uç noktalar ve ham istekler

Her API yolu ayrı bir ayar olarak tutulur, böylece Epoint tarafındaki bir değişikliğe yeni bir SDK sürümünü beklemeden uyum sağlayabilirsiniz.

## Varsayılan yollar

| Ad | Varsayılan yol | Kullanan |
| --- | --- | --- |
| `payment` | `/api/1/request` | `payments.create` |
| `checkout` | `/api/1/checkout` | `payments.form` (formun `action` adresi) |
| `status` | `/api/1/get-status` | `payments.status` |
| `reverse` | `/api/1/reverse` | `payments.reverse` |
| `hold` | `/api/1/pre-auth-request` | `payments.hold` |
| `capture` | `/api/1/pre-auth-complete` | `payments.capture` |
| `card_register` | `/api/1/card-registration` | `cards.register` |
| `card_register_pay` | `/api/1/card-registration-with-pay` | `cards.register_and_pay` |
| `card_charge` | `/api/1/execute-pay` | `cards.charge` |
| `card_status` | `/api/1/get-status-card` | `cards.status` |
| `payout` | `/api/1/refund-request` | `cards.payout` |
| `split_payment` | `/api/1/split-request` | `split.create` |
| `split_charge` | `/api/1/split-execute-pay` | `split.charge` |
| `split_register_pay` | `/api/1/split-card-registration-with-pay` | `split.register_and_pay` |
| `installment_plans` | `/api/1/get-installment-request` | `installments.plans` |
| `installment_payment` | `/api/1/installment-request` | `installments.create` |
| `wallets` | `/api/1/wallet/status` | `wallets.list` |
| `wallet_payment` | `/api/1/wallet/payment` | `wallets.pay` |
| `widget` | `/api/1/token/widget` | `widgets.create` |
| `widget_split` | `/api/1/token/split-payment` | `widgets.split` |
| `invoice_create` | `/api/1/invoices/create` | `invoices.create` |
| `invoice_update` | `/api/1/invoices/update` | `invoices.update` |
| `invoice_view` | `/api/1/invoices/view` | `invoices.get` |
| `invoice_list` | `/api/1/invoices/list` | `invoices.list` |
| `invoice_sms` | `/api/1/invoices/send-sms` | `invoices.send_sms` |
| `invoice_email` | `/api/1/invoices/send-email` | `invoices.send_email` |
| `b2b_transfer` | `/api/1/b2b/payment` | `transfers.create` |
| `b2b_status` | `/api/1/b2b/payment/{order_id}` | `transfers.status` |
| `heartbeat` | `/api/heartbeat` | `heartbeat` |

Yollar `base_url`'e göredir. Süslü parantez içindeki değerler her çağrıda doldurulur ve URL için kodlanır.

## Bir yolu değiştirmek

Kodda:

```python
ep = Epoint(endpoints={"payment": "/api/2/request"})
```

Yalnızca belirttiğiniz yollar değişir. Diğerleri varsayılanlarında kalır.

Yapılandırma dosyasında:

```toml
[endpoints]
payment = "/api/2/request"
```

Ortam değişkeniyle, parçalar arasında çift alt çizgiyle:

```console
$ export EPOINT_ENDPOINTS__PAYMENT=/api/2/request
```

## SDK'da olmayan bir uç noktayı çağırmak

`request()` herhangi bir veriyi imzalar ve herhangi bir uç noktaya gönderir. Ona tablodaki bir uç nokta adını veya `/` ile başlayan bir yolu verin:

```python
answer = ep.request("/api/1/some-new-call", {"order_id": "A-1", "amount": 10})
```

Yanıt, hiçbir işlemden geçmemiş çözülmüş JSON'dur. Hatalar diğer çağrılardaki gibi ele alınır: `status: error` için `GatewayError`, HTTP hataları için `HTTPStatusError` fırlatılır.

Varsayılan olarak `request()` para hareketi yaratan bir çağrı sayılır ve sonucu belirsiz bir hatadan sonra asla yeniden denenmez. Yalnızca okuma yapan bir çağrıda yeniden denemeye izin vermek için `safe=True` verin:

```python
ep.request("/api/1/some-report", {"date": "2026-03-01"}, safe=True)
```

`public_key` değeriniz veriye eklenir, boş değerler (`None` veya `""`) ise imzalamadan önce çıkarılır.
